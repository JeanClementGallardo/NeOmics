const neo4j = require('neo4j-driver/types').v1;

const driver = neo4j.driver('bolt://localhost:7474/', neo4j.auth.basic('neo4j', 'admin'));
const session = driver.session();

const personName = 'Alice';
const resultPromise = session.run(
  'CREATE (a:Person {name: $name}) RETURN a',
  {name: personName}
);

resultPromise.then(result => {
  session.close();

  const singleRecord = result.records[0];
  const node = singleRecord.get(0);


  // on application exit:
  driver.close();
});