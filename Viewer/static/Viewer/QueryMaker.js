function* id_generator() {

    function product(iterables, repeat) {

        let argv = Array.prototype.slice.call(arguments), argc = argv.length;
        if (argc === 2 && !isNaN(argv[argc - 1])) {
            let copies = [];
            for (let i = 0; i < argv[argc - 1]; i++) {
                copies.push(argv[0].slice()); // Clone
            }
            argv = copies;
        }

        return argv.reduce(function tl(accumulator, value) {
            let tmp = [];
            accumulator.forEach(function (a0) {
                value.forEach(function (a1) {
                    tmp.push(a0.concat(a1));
                });
            });
            return tmp;
        }, [[]]);
    }

    function* count(first_val = 0, step = 1) {

        let x = first_val;
        while (true) {
            yield x;
            x += step;
        }
    }

    let letters = [];
    for (let i = 97; i <= 122; i++) {
        letters.push(String.fromCodePoint(i))
    }

    for (let size of count(1)) {
        for (let s of product(letters, size)) {
            yield s.join('')
        }
    }
}


let query = "";
let nodes = [];

function add_node() {
    return true
}

function update_global_query() {
    let ids = id_generator();
    let matches = "MATCH ";
    let returned = " RETURN ";
    let return_sth = false;
    for (let node of nodes) {
        matches += "(";
        if (node.returned === 1) {
            let node_id = ids.next().value;
            matches += node_id;
            returned += `${node_id}, `;
            return_sth = true;
        }
        if (node.node_type) {
            matches += `:${node.node_type}`;
        }
        if (node.name !== "") {
            matches += ` {name: "${node.name}" }`;
        }
        matches += ")";
        let link = node.link;
        if (link) {
            link.update_type_list();
            matches += "-[";
            if (link.simple) {
                let link_type = link.type;
                if (link.returned) {
                    let link_id = next(ids);
                    matches += link_id;
                    returned += `${link_id}, `;
                    return_sth = true;
                }
                if (link_type) {
                    matches += `:${link_type}`;
                }
            } else {
                matches += `*${link.min}..${link.max}`;
            }
            matches += "]-";
        }
        if (return_sth) {
            returned.substring(0, (returned.length - 2))
        }
        query = matches + returned;
    }
}


class Node {
    constructor() {
        nodes.push(this);
        this.node_type = "";
        this.returned = false;
        this.name_options = [];
        this.name = "";
        this.link = null;
        this.next = null;
    }

    get descriptor() {
        let cypher = "(";
        if (this.node_type) {
            cypher += `:${this.node_type}`;
        }
        if (this.name !== "") {
            cypher += ` {name: "${this.name}" }`;
        }
        return cypher + ")";
    }

    get query() {
        let cypher = "MATCH ";
        for (let node of nodes) {
            if (node === this) {
                break;
            }
            cypher += node.descriptor();

            let link = node.link;
            if (link) {
                link.update_type_list();
                cypher += "-[";
                if (link.simple) {
                    let link_type = link.type;
                    if (link_type) {
                        cypher += `:"${link_type}"`;
                    }
                } else {
                    cypher += `*${link.min}..${link.max}`;
                    cypher += "]-"
                }
            }
        }
        return cypher;
    }

    display_types() {
        let types_query = this.query + "(a) RETURN DISTINCT labels(a) as type";
        let results = session.run(types_query);
        let types = [];
        types.push("Unknown");
        for (label of results) {
            types.push(label);
        }
    }

    /**
     * Set the autocompletion list accordingly to current node information
     *
     */

    update_name_list() {
        let name_query = this.query + '(a';
        if (this.node_type) {
            name_query += `:${this.node_type}`;
        }
        name_query += ') RETURN a.name';
        // completion list is a set to avoid repetition
        let results = session.run(name_query);
        for (name of results) {
            //    update name seelection
        }
    }


    new_node() {
        this.link = Relation(this);
        this.link.next.update_name_list();
        ImportGraph.update_global_query(ImportGraph());
    }

}

class Relation {

    constructor(previous) {
        this.simple = true;

        this.returned = false;

        this.type = "";
        this.type_options = [];

        this.min = 0;
        this.max = 0;

        this.previous = previous;
        this.next = ImportGraph.nodes;
        this.update_type_list();
    }

    update_type_list() {
        let type_query = this.previous.query + this.previous.descriptor + `-[r]-${this.next} RETURN DISTINCT type(r) as types`;

        let results = session.run(types_query);
        let types = [];
        types.push("Unknown");
        for (label of results) {
            types.push(label);
        }
    }

    dist_switch() {
        if (this.simple) {
            this.simple = false;
        } else {
            this.simple = true;
        }
        ImportGraph.update_global_query();
    }

    update_max() {
        if (this.max < this.min) {
            this.max = this.min;
        }
    }

    update_min() {
        if (this.max < this.min) {
            this.min = this.max
        }
    }

    // main():
    //    init = ImportGraph.Node(this)
    //    init.update_name_list()
    //    ImportGraph.update_global_query(ImportGraph())
    //    return render(request, "ComputeGraph/stat_load.html")
}