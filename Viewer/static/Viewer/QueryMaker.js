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
        if (node.type) {
            matches += `:${node.type}`;
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

let node_id_generator = id_generator();
let QMdiv = $("#QM");

let add_btn = $("#add");

class Node {
    constructor() {
        nodes.push(this);
        add_btn.onclick = this.new_node;
        this.id = "Node" + node_id_generator.next().value;
        this.type = "";
        this.returned = false;
        this.name = "";
        this.link = null;
        this.next = null;
        this.node_div = $(`<div id=${this.id}></div>`);
        this.select_type = $(`<SELECT onchange='this.set_type()'></SELECT>`);
        this.get_types();
        this.node_div.append(this.select_type);
        add_btn.before(this.node_div);
    }

    get descriptor() {
        let cypher = "(";
        if (this.type) {
            cypher += `:${this.type}`;
        }
        if (this.name !== "") {
            cypher += ` {name: "${this.name}" }`;
        }
        return cypher + ")";
    }

    get query() {
        let cypher = "MATCH ";
        for (let node of nodes) {
            if (node == this) {
                break;
            }
            cypher += node.descriptor;

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

    set_type() {
        this.type = this.select_type.find(":selected").text();
    }

    get_types() {
        let types_query = this.query + "(a) RETURN DISTINCT labels(a) as type";
        session.run(types_query).then(result => {
            this.select_type.append($("<OPTION value='Unknown'>Unknown</OPTION>"));
            for (let record of result.records) {
                console.log(record);
                let label = record.get('type')[0];
                console.log(label);
                this.select_type.append($(`<OPTION value='${label}'>${label}</OPTION>`));
            }
        });
    }

    //
    // get_types() {
    //     let types_query = this.query + "(a) RETURN DISTINCT labels(a)";
    //     // let resultPromise = session.run(types_query);
    //     // resultPromise.then(this.set_type_list);
    //     let list = "";
    //     cx.run(types_query,{},{onRecord:this.set_type_list});
    //     this.select_type.innerHTML = list;
    // }

    // set_type_list(record, list) {
    //     const node = record[0][0];
    //     console.log(node);
    //     list += ($(`<OPTION value='${node}'>${node}</OPTION>`));
    //     return list;
    // }

    update_name_list() {
        let name_query = this.query + '(a';
        if (this.type) {
            name_query += `:${this.type}`;
        }
        name_query += ') RETURN a.name';
        // completion list is a set to avoid repetition
        let results = session.run(name_query);
        for (name of results) {
            //    update name seelection
        }
    }

    get html() {
        let newDiv = document.createElement("div");
        newDiv.setAttribute("id", this.id);
        let list_types = this.get_types();
        for (types of list_types) {
            newDiv.innerHTML = "<OPTION "
        }
    }

    new_node() {
        this.link = new Relation(this);
        this.link.next.update_name_list();
        update_global_query();
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
        this.next = new Node();
        this.update_type_list();
    }

    update_type_list() {
        let type_query = this.previous.query + this.previous.descriptor + `-[r]-${this.next} RETURN DISTINCT type(r) as types`;

        let results = session.run(type_query);
        let types = [];
        types.push("Unknown");
        for (label of results) {
            types.push(label);
        }
    }

    dist_switch() {
        this.simple = !this.simple;
        update_global_query();
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

    // main(){
    //    init = ImportGraph.Node(this)
    //    init.update_name_list()
    //    ImportGraph.update_global_query(ImportGraph())
    //    return render(request, "ComputeGraph/stat_load.html")
}
