//Construction du QueryMaker

const resultPromise = session.run(
    'MATCH (n) return n'
);

resultPromise.then(result => {
    session.close();
    let i = 0;
    let list = "<SELECT id ='test'><OPTION>First node selection<br>";
    for (let row in result) {
        const singleRecord = result.records[i];
        const node = singleRecord.get(0);
        list = list + "<OPTION>" + node.labels;
        i++;
    }
    document.getElementById("first").innerHTML = list + "</SELECT>";
});

function selectNode() {
    var e = document.getElementById("test");
    var strUser = e.options[e.selectedIndex].text;
    document.getElementById("cypher").append(" " + strUser);
}

function addNode() {
    let currentDiv = document.getElementById("QM");
    let newDiv = document.createElement("form");
    newDiv.setAttribute("id", "next");
    currentDiv.insertBefore(newDiv, document.getElementById('add'));

    const resultPromise = session.run(
        'MATCH (n) return n'
    );

    resultPromise.then(result => {
        session.close();
        let i = 0;
        let list = "<SELECT><OPTION>Node selection<br>";
        for (let row in result) {
            const singleRecord = result.records[i];
            const node = singleRecord.get(0);
            list = list + "<OPTION>" + node.labels;
            i++;
        }
        newDiv.innerHTML = list + "</SELECT>";
    });
}

function removeNode() {
    let element = document.getElementById("next");
    element.parentNode.removeChild(element);
}

// Fonction pour neovis


function reload() {
    let cypher = document.getElementById("cypher").value;
    if (cypher.length > 3) {
        viz.renderWithCypher(cypher);
    } else {
        viz.reload();
    }
}

function stabilize() {
    viz.stabilize();
}

