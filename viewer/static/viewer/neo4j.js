const driver = neo4j.v1.driver('bolt://localhost:7687', neo4j.v1.auth.basic('neo4j', 'admin'));
const session = driver.session();

const resultPromise = session.run(
    'MATCH p=()-[]->() RETURN p'
);

resultPromise.then(result => {
    session.close();
    list = "";
    for (i = 0; i<10; i++) {
        const singleRecord = result.records[i];
        const node = singleRecord.get(0);
        list = list+node+" \n";
    }
    document.getElementById("test").innerHTML = list;
    driver.close();
});