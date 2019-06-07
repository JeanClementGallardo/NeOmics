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

//////////// Query Maker \\\\\\\\\\\\\\

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
        node.type = node.select_type.find(":selected").val();
        if (node.type && node.type !== "Unknown") {
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
                // link.type = link.select_type.find(":selected").val();
                // console.log(link.select_type.find(":selected").val());
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
            returned.substring(0, (returned.length - 2));
        }
        query = matches + returned;
        $("#cypher").val(query);
    }
}

let node_id_generator = id_generator();
let rel_id_generator = id_generator();
let add_btn = $("#add");

class Node {
    constructor() {
        nodes.push(this);
        this.id = "Node" + node_id_generator.next().value;
        this.type = "";
        this.returned = false;
        this.name = "";
        this.link = null;

        this.node_div = $(`<div id=${this.id}></div>`);
        this.select_type = $(`<SELECT onchange="update_global_query()"></SELECT>`);
        this.check_return = $(`<input type="checkbox" onchange="return_value()">Return</input>`);
        this.get_types();
        this.node_div.append(this.select_type);
        this.node_div.append(this.check_return);
        add_btn.before(this.node_div);
    }

    return_value(){
        this.returned = !this.returned;
    }

    get descriptor() {
        let cypher = "(";
        if (this.type && this.type !== "Unknown") {
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
                }
                cypher += "]-";
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
            this.select_type.empty();
            this.select_type.append($("<OPTION value='Unknown'>Unknown</OPTION>"));
            for (let record of result.records) {
                let label = record.get('type')[0];
                this.select_type.append($(`<OPTION value='${label}'>${label}</OPTION>`));
            }
        });
    }


    // update_name_list() {
    //     let name_query = this.query + '(a';
    //     if (this.type) {
    //         name_query += `:${this.type}`;
    //     }
    //     name_query += ') RETURN a.name';
    //     // completion list is a set to avoid repetition
    //     let results = session.run(name_query);
    //     for (name of results) {
    //         //    update name selection
    //     }
    // }
}

function new_node() {
    let last_node = nodes[nodes.length - 1];
    last_node.link = new Relation(last_node);
    last_node.link.set_next();
    // last_node.link.next.update_name_list();
    update_global_query();
}

function remove_node() {
    let node_id = nodes[nodes.length -1].id;
    let rel_id = "Rel" + nodes[nodes.length -2].id.substr(node_id.length - 1);
    document.getElementById(node_id).parentNode.removeChild(document.getElementById(node_id));
    document.getElementById(rel_id).parentNode.removeChild(document.getElementById(rel_id));
    update_global_query();
}

class Relation {

    constructor(previous) {
        this.id = "Rel" + rel_id_generator.next().value;
        this.simple = true;
        this.returned = false;
        this.type = "";
        this.min = 0;
        this.max = 0;

        this.previous = previous;
        this.rel_div = $(`<div id=${this.id}></div>`);

        this.select_type = $(`<SELECT onchange="update_global_query()"></SELECT>`);
        this.rel_div.append(this.select_type);
        add_btn.before(this.rel_div);

    }

    set_next() {
        this.next = new Node();
        this.next.select_type.change(this.update_type_list);
        this.update_type_list();
    }

    update_type_list() {
        this.type = this.select_type.find(":selected").val();
        let selected = this.select_type.find(":selected").val();
        let type_query = this.previous.query + this.previous.descriptor + `-[r]-() RETURN DISTINCT type(r) as types`;
        this.select_type.empty();
        session.run(type_query).then(result => {
            for (let record of result.records) {
                let label = record.get('types');
                if (label === selected) {
                    this.select_type.append($(`<OPTION value='${label}' selected>${label}</OPTION>`));
                } else {
                    this.select_type.append($(`<OPTION value='${label}'>${label}</OPTION>`));
                }
            }
        });
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
}

new Node();
update_global_query();