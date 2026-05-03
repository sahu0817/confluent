# Debezium PostGres CDC Source Connector for Confluent Platform
## Contents
- [Start Confluent Platform](#Start-Confluent-Platform)
- [Start Postgres Container](#Start-a-postgres-DB-in-docker-container)
- [Deploy the connector](#Deploy-the-connector)
- [Verify the events in the Topic](#Verify-the-events-in-the-Topic) 
- [Deploy Errors & Resolutions](#Deploy-Errors-&-Resolutions)
- [Confluent Platform Logs](#Confluent-logs)

### Reference
- [Debezium Postgres connector](https://debezium.io/documentation/reference/2.5/connectors/postgresql.html)

## Start Confluent Platform 
#### Local
```
> confluent local services start

Using CONFLUENT_CURRENT: /tmp/confluent.079104
Connect is [UP]
Control Center is [UP]
Kafka is [UP]
Kafka REST is [UP]
ksqlDB Server is [UP]
Schema Registry is [UP]
ZooKeeper is [UP]
```
#### Install debezium postgres plugin
> :information_source: Use **confluent-hub install debezium/debezium-connector-postgresql:latest** for the latest version.
```
> confluent-hub install debezium/debezium-connector-postgresql:2.2.1

The component can be installed in any of the following Confluent Platform installations:
  1. /home/ubuntu/confluent-7.1.1 (based on $CONFLUENT_HOME)
  2. / (installed rpm/deb package)
  3. /home/ubuntu/confluent-7.1.1 (where this tool is installed)
Choose one of these to continue the installation (1-3): 1
Do you want to install this into /home/ubuntu/confluent-7.1.1/share/confluent-hub-components? (yN) y


Component's license:
Apache 2.0
https://github.com/debezium/debezium/blob/master/LICENSE.txt
I agree to the software license agreement (yN) y

You are about to install 'debezium-connector-postgresql' from Debezium Community, as published on Confluent Hub.
Do you want to continue? (yN) y

Downloading component Debezium PostgreSQL CDC Connector 2.2.1, provided by Debezium Community from Confluent Hub and installing into /home/ubuntu/confluent-7.1.1/share/confluent-hub-components
Detected Worker's configs:
  1. Standard: /home/ubuntu/confluent-7.1.1/etc/kafka/connect-distributed.properties
  2. Standard: /home/ubuntu/confluent-7.1.1/etc/kafka/connect-standalone.properties
  3. Standard: /home/ubuntu/confluent-7.1.1/etc/schema-registry/connect-avro-distributed.properties
  4. Standard: /home/ubuntu/confluent-7.1.1/etc/schema-registry/connect-avro-standalone.properties
Do you want to update all detected configs? (yN) y

Adding installation directory to plugin path in the following files:
  /home/ubuntu/confluent-7.1.1/etc/kafka/connect-distributed.properties
  /home/ubuntu/confluent-7.1.1/etc/kafka/connect-standalone.properties
  /home/ubuntu/confluent-7.1.1/etc/schema-registry/connect-avro-distributed.properties
  /home/ubuntu/confluent-7.1.1/etc/schema-registry/connect-avro-standalone.properties

Completed
```


#### Validate the plugin is installed
```
> curl -sS localhost:8083/connector-plugins | jq '.[].class'  | grep Postgres
"io.debezium.connector.postgresql.PostgresConnector"
```
> Restart confluent if not found 'confluent local services restart'

## Start a postgres DB in docker container  
#### docker-compose.yml
```
version: '3.1'

services:

  db:
    image: postgres
    restart: always
    environment:
      POSTGRES_PASSWORD: example
    ports:
      - 5432:5432
    command:
      - "postgres"
      - "-c"
      - "wal_level=logical"

  adminer:
    image: adminer
    restart: always
    ports:
      - 8080:8080

```
> :warning: wal_level default is replica, cannot be changed when the db is running. Change to logical in the docker-compose to avoid the below ERROR
```
{"error_code":400,"message":"Connector configuration is invalid and contains the following 1 error(s):
Error while validating connector config: Postgres server wal_level property must be 'logical' but is: 'replica'
You can also find the above list of errors at the endpoint `/connector-plugins/{connectorType}/config/validate`"}
```
####  Start
```
> docker-compose up -d

[+] Running 2/2
 ✔ Container postgres-db-1       Started                              0.0s 
 ✔ Container postgres-adminer-1  Started                              0.5s 
```
#### Check
```
> docker ps

CONTAINER ID   IMAGE       COMMAND                  CREATED              STATUS              PORTS                                       NAMES
a2e7bfd500e4   postgres    "docker-entrypoint.s…"   About a minute ago   Up About a minute   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   postgres-db-1
8269b7c89ac0   adminer     "entrypoint.sh php -…"   About a minute ago   Up About a minute   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   postgres-adminer-1
```
#### Create Database and change default user password
```
> docker exec -it postgres-db-1 bash

root@a2e7bfd500e4:/# psql -h localhost -U postgres
psql (16.1 (Debian 16.1-1.pgdg120+1))
Type "help" for help.

postgres=# CREATE DATABASE PGTEST;
CREATE DATABASE
postgres=# \l
                                                      List of databases
   Name    |  Owner   | Encoding | Locale Provider |  Collate   |   Ctype    | ICU Locale | ICU Rules |   Access privileges   
-----------+----------+----------+-----------------+------------+------------+------------+-----------+-----------------------
 pgtest    | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |            |           | 
 postgres  | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |            |           | 
 template0 | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |            |           | =c/postgres          +
           |          |          |                 |            |            |            |           | postgres=CTc/postgres
 template1 | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |            |           | =c/postgres          +
           |          |          |                 |            |            |            |           | postgres=CTc/postgres
(4 rows)

postgres=# alter user postgres with password 'pgtest123';
ALTER ROLE

postgres=# \c pgtest;
You are now connected to database "pgtest" as user "postgres".
```
#### Create a table and load sample data

```
pgtest=# create table movies (ID INT PRIMARY KEY NOT NULL, NAME TEXT NOT NULL, TYPE TEXT NOT NULL, TS TIMESTAMP without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')); 
CREATE TABLE
pgtest=# insert into movies values (1, 'Avengers', 'Action');
INSERT 0 1
pgtest=# insert into movies values (2, 'IronMan', 'Action');
INSERT 0 1
pgtest=# select * from movies;
 id |   name   |  type  |             ts             
----+----------+--------+----------------------------
  1 | Avengers | Action | 2024-02-22 01:16:09.762639
  2 | IronMan  | Action | 2024-02-22 01:16:32.363629
(2 rows)

pgtest=# exit
root@a2e7bfd500e4:/# exit
```
#### Alternatively you can use a desktop tool like DBeaver/DBVisualizer and connect to the DB with the following URL
```
host: 18.220.31.188
port: 5432
user: postgres
password: pgtest123   <-- altered above
```
## Deploy the connector
```
> curl -X PUT -H "Content-Type: application/json" --url http://localhost:8083/connectors/pg_conn/config -d @pg_conn.json

{
  "name": "pg_conn",
  "config": {
    "name": "pg_conn",
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "18.220.31.188",
    "database.port": "5432",
    "database.dbname": "pgtest",
    "database.user": "postgres",
    "database.password": "pgxxxxxxx",
    "kafka.api.key": "XA7xxxxxxxxxx",
    "kafka.api.secret": "5PKVoxxxxxxxxxxxxxxxx",
    "kafka.endpoint": "SASL_SSL://pkc-921jm.us-east-2.aws.confluent.cloud:9092",
    "output.data.format": "AVRO",
    "table.whitelist": "movies",
    "tasks.max": "1",
    "mode": "timestamp",
    "timestamp.column.name": "ts",
    "topic.prefix": "pgsource."
  },
  "tasks": [],
  "type": "source"
}

```
> :warning: Note the kafka.* parameters have no effect when deployed in CP. It picks the bootstrap server from the worker.properties.

#### Check the status
```
> curl -X GET -H "Content-Type: application/json" --url http://localhost:8083/connectors/pg_conn/status | jq

{
  "name": "pg_conn",
  "connector": {
    "state": "RUNNING",
    "worker_id": "172.31.14.247:8083"
  },
  "tasks": [
    {
      "id": 0,
      "state": "RUNNING",
      "worker_id": "172.31.14.247:8083"
    }
  ],
  "type": "source"
}
```

## Verify the events in the Topic

```
> kafka-avro-console-consumer --bootstrap-server localhost:9092  --topic pgsource..public.movies --from-beginning

{"before":null,"after":{"pgsource..public.movies.Value":{"id":1,"name":"Avengers","type":"Action","ts":1708572745401143}},"source":{"version":"2.2.1.Final","connector":"postgresql","name":"pgsource.","ts_ms":1708573849127,"snapshot":{"string":"first"},"db":"pgtest","sequence":{"string":"[null,\"26619544\"]"},"schema":"public","table":"movies","txId":{"long":748},"lsn":{"long":26619544},"xmin":null},"op":"r","ts_ms":{"long":1708573849321},"transaction":null}
{"before":null,"after":{"pgsource..public.movies.Value":{"id":2,"name":"IronMan","type":"Action","ts":1708572751794615}},"source":{"version":"2.2.1.Final","connector":"postgresql","name":"pgsource.","ts_ms":1708573849127,"snapshot":{"string":"last"},"db":"pgtest","sequence":{"string":"[null,\"26619544\"]"},"schema":"public","table":"movies","txId":{"long":748},"lsn":{"long":26619544},"xmin":null},"op":"r","ts_ms":{"long":1708573849325},"transaction":null}
{"before":null,"after":{"pgsource..public.movies.Value":{"id":3,"name":"Oppenheimer","type":"Classic","ts":1708574107779843}},"source":{"version":"2.2.1.Final","connector":"postgresql","name":"pgsource.","ts_ms":1708574107780,"snapshot":{"string":"false"},"db":"pgtest","sequence":{"string":"[null,\"26630232\"]"},"schema":"public","table":"movies","txId":{"long":749},"lsn":{"long":26630232},"xmin":null},"op":"c","ts_ms":{"long":1708574108123},"transaction":null}

```
## Deploy Errors & Resolutions
```
> curl -X PUT -H "Content-Type: application/json" --url http://localhost:8083/connectors/pgtest_connector/config -d @pg_conn.json
{"error_code":500,"message":"Unexpected character ('k' (code 107)): was expecting comma to separate Object entries\n at [Source: (org.glassfish.jersey.message.internal.ReaderInterceptorExecutor$UnCloseableInputStream); line: 1, column: 254]"}
```
> Resolution: DoubleQuotes not closed properly

```
> curl -X PUT -H "Content-Type: application/json" --url http://localhost:8083/connectors/pgtest_connector/config -d @pg_conn.json
{"error_code":400,"message":"Connector configuration is invalid and contains the following 1 error(s):\nError while validating connector config: Postgres server wal_level property must be 'logical' but is: 'replica'\nYou can also find the above list of errors at the endpoint `/connector-plugins/{connectorType}/config/validate`"}
```
> Resolution: Change the wal_level settings in the docker-compose file

```
> curl -X PUT -H "Content-Type: application/json" --url http://localhost:8083/connectors/pgtest_connector/config -d @pg_conn.json
. . .
Caused by: org.postgresql.util.PSQLException: ERROR: could not access file \"decoderbufs\": No such file or directory
. . .
```
> Resolution: "plugin.name": "pgoutput" is missing in the connector config.
> > :information_source: The name of the PostgreSQL logical decoding plug-in installed on the PostgreSQL server. Supported values are decoderbufs, and pgoutput. Default is decoderbufs.
> pgoutput is the default logical decoding output plugin used by Postgres to decode the WAL file entries and send the change data capture events to the consumer in binary format. 

## Confluent logs
```
> confluent local services connect log | grep "records sent"

[2024-02-22 03:55:08,524] INFO [pg_conn|task-0] 3 records sent during previous 00:04:19.537, last recorded offset of {server=pgsource.} partition is {transaction_id=null, lsn_proc=26630232, messageType=INSERT, lsn=26630232, txId=749, ts_usec=1708574107780527} (io.debezium.connector.common.BaseSourceTask:195)
```
```
> confluent local services connect log  | grep public.movies

[2024-02-22 03:50:49,238] INFO [pg_conn|task-0] Adding table public.movies to the list of capture schema tables (io.debezium.relational.RelationalSnapshotChangeEventSource:267)
[2024-02-22 03:50:49,239] INFO [pg_conn|task-0] Snapshot step 3 - Locking captured tables [public.movies] (io.debezium.relational.RelationalSnapshotChangeEventSource:126)
[2024-02-22 03:50:49,305] INFO [pg_conn|task-0] For table 'public.movies' using select statement: 'SELECT "id", "name", "type", "ts" FROM "public"."movies"' (io.debezium.relational.RelationalSnapshotChangeEventSource:399)
[2024-02-22 03:50:49,308] INFO [pg_conn|task-0] Exporting data from table 'public.movies' (1 of 1 tables) (io.debezium.relational.RelationalSnapshotChangeEventSource:513)
[2024-02-22 03:50:49,325] INFO [pg_conn|task-0]          Finished exporting 2 records for table 'public.movies' (1 of 1 tables); total duration '00:00:00.017' (io.debezium.relational.RelationalSnapshotChangeEventSource:559)
[2024-02-22 03:50:49,393] INFO [pg_conn|task-0] REPLICA IDENTITY for 'public.movies' is 'DEFAULT'; UPDATE and DELETE events will contain previous values only for PK columns (io.debezium.connector.postgresql.PostgresSchema:100)
[2024-02-22 03:50:49,473] INFO [pg_conn|task-0] REPLICA IDENTITY for 'public.movies' is 'DEFAULT'; UPDATE and DELETE events will contain previous values only for PK columns (io.debezium.connector.postgresql.PostgresSchema:100)
[2024-02-22 03:50:49,905] WARN [pg_conn|task-0] [Producer clientId=connector-producer-pg_conn-0] Error while fetching metadata with correlation id 3 : {pgsource..public.movies=LEADER_NOT_AVAILABLE} (org.apache.kafka.clients.NetworkClient:1222)
[2024-02-22 03:50:50,006] INFO [pg_conn|task-0] [Producer clientId=connector-producer-pg_conn-0] Resetting the last seen epoch of partition pgsource..public.movies-0 to 0 since the associated topicId changed from null to tMMBiglZQ2OKj8T8K-9T_g (org.apache.kafka.clients.Metadata:402)
[2024-02-22 03:50:50,011] INFO [Worker clientId=connect-1, groupId=connect-cluster] Resetting the last seen epoch of partition pgsource..public.movies-0 to 0 since the associated topicId changed from null to tMMBiglZQ2OKj8T8K-9T_g (org.apache.kafka.clients.Metadata:402)
```
