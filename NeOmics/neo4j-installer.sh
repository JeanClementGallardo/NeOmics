#!/bin/bash

if [[ $# -ne 7 ]]
then
    echo "ERROR: Should be called with neo4j-installer <ROOT_PATH> <DB_NAME> <SERVER_ADDRESS> <BOLT_PORT> <HTTP_PORT> <USER> <PASSWORD>"
    exit 1
fi

ROOT_PATH=$1
DB_NAME=$2
SERVER_ADDRESS=$3
BOLT_PORT=$4
HTTP_PORT=$5
USER=$6
PASSWORD=$7

INSTANCE_ROOT="${ROOT_PATH}/neo4j_instances"
mkdir -p ${INSTANCE_ROOT}


rm -rf "$INSTANCE_ROOT/$DB_NAME"
cp -rf ${ROOT_PATH}/neo4j-community-3.5.6 "$INSTANCE_ROOT/$DB_NAME"
sed -i "s/#dbms.connector.http.listen_address=:7474/dbms.connector.http.listen_address=:$HTTP_PORT/" "$INSTANCE_ROOT/$DB_NAME/conf/neo4j.conf"
sed -i "s/#dbms.active_database=graph.db/dbms.active_database=$DB_NAME.db/" "$INSTANCE_ROOT/$DB_NAME/conf/neo4j.conf"
sed -i "s/#dbms.connectors.default_listen_address=0.0.0.0/dbms.connectors.default_listen_address=$SERVER_ADDRESS/" "$INSTANCE_ROOT/$DB_NAME/conf/neo4j.conf"
sed -i "s/#dbms.connector.bolt.listen_address=:7687/dbms.connector.bolt.listen_address=:$BOLT_PORT/" "$INSTANCE_ROOT/$DB_NAME/conf/neo4j.conf"
sed -i "s/dbms.connector.https.enabled=true/dbms.connector.https.enabled=false/" "$INSTANCE_ROOT/$DB_NAME/conf/neo4j.conf"

${INSTANCE_ROOT}/${DB_NAME}/bin/neo4j start

while ! echo exit | nc ${SERVER_ADDRESS} ${BOLT_PORT}; do sleep 10; done

TMP_PASSWORD=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
${INSTANCE_ROOT}/${DB_NAME}/bin/cypher-shell -a "bolt://$SERVER_ADDRESS:$BOLT_PORT" -u neo4j -p neo4j "CALL dbms.security.changePassword('$TMP_PASSWORD');"
${INSTANCE_ROOT}/${DB_NAME}/bin/cypher-shell -a "bolt://$SERVER_ADDRESS:$BOLT_PORT" -u neo4j -p ${TMP_PASSWORD} "CALL dbms.security.createUser('$USER', '$PASSWORD', false);"
#${INSTANCE_ROOT}/${DBNAME}/bin/cypher-shell -a "bolt://$SERVER_ADDRESS:$BOLT_PORT" -u neo4j -p ${TMP_PASSWORD} "CALL dbms.security.addRoleToUser('admin', '$USER');"
# Only if entreprise edition

#./${INSTANCE_ROOT}/${DB_NAME}/bin/neo4j stop