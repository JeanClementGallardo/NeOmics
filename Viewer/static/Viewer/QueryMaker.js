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
        node.get_types();
        matches += "(";
        node.returned = node.check_return.is(':checked');
        if (node.returned) {
            let node_id = ids.next().value;
            matches += node_id;
            returned += `${node_id}, `;
            return_sth = true;
        }
        if (node.type && node.type !== "Unknown") {
            console.log(node.type);
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
                link.returned = link.check_return.is(':checked');
                if (link.returned) {
                    let link_id = ids.next().value;
                    matches += link_id;
                    returned += `${link_id}, `;
                    return_sth = true;
                }
                if (link_type && link.type !== "Unknown") {
                    matches += `:${link_type}`;
                }
            } else {
                matches += `*${link.min}..${link.max}`;
            }
            matches += "]-";
        }
    }
    if (return_sth) {
        returned = returned.substring(0, (returned.length - 2));
    }
    query = matches + returned;
    $("#cypher").val(query);
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

        this.node_div = $(`<div id=${this.id} class="selectBox"></div>`);
        this.select_type = $(`<SELECT onchange="update_global_query()"></SELECT>`);
        this.check_return = $(`<input type="checkbox" onchange="update_global_query()" id=${this.id} class="return_check">Return</input>`);
        this.node_div.append(this.select_type);
        this.node_div.append(this.check_return);
        add_btn.before(this.node_div);
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
                cypher += "-[";
                if (link.simple) {
                    let link_type = link.type;
                    if (link_type && link_type !== "Unknown") {
                        cypher += `:${link_type}`;
                    }
                } else {
                    cypher += `*${link.min}..${link.max}`;
                }
                cypher += "]-";
            }
        }
        return cypher;
    }

    remove() {
        this.node_div.remove();
    }

    get_types() {
        this.type = this.select_type.find(":selected").val();
        let selected = this.select_type.find(":selected").val();
        let types_query = this.query + "(a) RETURN DISTINCT labels(a) as type";
        this.select_type.empty();
        this.select_type.append($("<OPTION value='Unknown'>Unknown</OPTION>"));
        session.run(types_query).then(result => {
            for (let record of result.records) {
                let label = record.get('type')[0];
                if (label === selected) {
                    this.select_type.append($(`<OPTION value='${label}' selected>${label}</OPTION>`));
                } else {
                    this.select_type.append($(`<OPTION value='${label}'>${label}</OPTION>`));
                }
            }
        });
    }
}


function new_node() {
    let last_node = nodes[nodes.length - 1];
    last_node.link = new Relation(last_node);
    last_node.link.set_next();
    update_global_query();
}

function remove_node() {
    nodes.pop().remove();
    nodes[nodes.length - 1].link.remove();
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
        this.rel_div = $(`<div id=${this.id} class="selectBox"></div>`);
        this.image = $(`<img src="${simpleLinkPath}" onclick="Relation.dist_switch(${this.previous.id})" class="rel_img">`);

        this.rel_div.append(this.image);
        this.select_type = $(`<SELECT onchange="update_global_query()"></SELECT>`);
        this.check_return = $(`<input type="checkbox" onchange="update_global_query()" id=${this.id} class="return_check">Return</input>`);
        this.rel_div.append(this.select_type);
        this.rel_div.append(this.check_return);
        add_btn.before(this.rel_div);

    }

    set_next() {
        this.next = new Node();
    }

    update_type_list() {
        this.type = this.select_type.find(":selected").val();
        let selected = this.select_type.find(":selected").val();
        let type_query = this.previous.query + this.previous.descriptor + `-[r]-() RETURN DISTINCT type(r) as types`;
        this.select_type.empty();
        this.select_type.append($("<OPTION value='Unknown'>Unknown</OPTION>"));
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

    remove() {
        this.rel_div.remove();
        this.previous.link = null;
    }


    static dist_switch(id) {
        console.log(id);
        let link = nodes.find(node => node.id === id.id).link;

        link.simple = !link.simple;
        link.image.attr("src",composedLinkPath);

        // update_global_query();
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