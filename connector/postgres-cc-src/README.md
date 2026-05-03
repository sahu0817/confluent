# Debezium PostGres CDC Source Connector for Confluent Cloud
## Contents
- [Start Postgres Container](#Start-a-postgres-server-in-docker)
- [Deploy the connector in Confluent Cloud](#Deploy-the-postgresql-connector-in-CC)


### Reference
- [Debezium Postgres connector](https://debezium.io/documentation/reference/2.5/connectors/postgresql.html)
  
### Prereq 
Confluent cloud cluster with a APIKey & Secret

## Start a postgres server in docker
```
> cat docker-compose.yml
version: '3.1'

services:

  db:
    image: postgres
    restart: always
    environment:
      POSTGRES_PASSWORD: example
    ports:
      - 5432:5432

  adminer:
    image: adminer
    restart: always
    ports:
      - 8080:8080
```

#### Start postgres
```
> docker-compose up -d
Creating network "postgres_default" with the default driver
Creating postgres_adminer_1 ... done
Creating postgres_db_1      ... done

> docker ps

CONTAINER ID   IMAGE      COMMAND                  CREATED         STATUS         PORTS                                       NAMES
0263650b5b0f   postgres   "docker-entrypoint.s…"   7 seconds ago   Up 6 seconds   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   postgres_db_1
0c52dc10145f   adminer    "entrypoint.sh php -…"   7 seconds ago   Up 6 seconds   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   postgres_adminer_1
```

#### Connect ( with container name)
```
> docker exec -it postgres_db_1 bash
root@ce8e821050f4:/# psql -h localhost -U postgres
psql (16.1 (Debian 16.1-1.pgdg120+1))
Type "help" for help.

postgres=# CREATE DATABASE pgtest;
CREATE DATABASE

postgres=# \l
   Name    |  Owner   | Encoding | Locale Provider |  Collate   |   Ctype    | ICU Locale | ICU Rules |   Access privileges   
-----------+----------+----------+-----------------+------------+------------+------------+-----------+-----------------------
 postgres  | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |            |           | 
 pgtest    | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |            |           | 
 template0 | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |            |           | =c/postgres          +
           |          |          |                 |            |            |            |           | postgres=CTc/postgres
 template1 | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |            |           | =c/postgres          +
           |          |          |                 |            |            |            |           | postgres=CTc/postgres
(4 rows)

pgtest=# alter user postgres with password 'Srinivas123';
ALTER ROLE

postgres=# \c pgtest
You are now connected to database "pgtest" as user "postgres".

pgtest=# create table authors(ID INT PRIMARY KEY NOT NULL, NAME TEXT NOT NULL, TYPE TEXT NOT NULL);
CREATE TABLE

pgtest=# insert into authors values(1, 'OReilly', 'Docker');
INSERT 0 1

pgtest=# select * from authors;
 id |  name   |  type  
----+---------+--------
  1 | OReilly | Docker
(1 row)

postgres=# exit
```

##### Alternatively you can Install postgressql client or use a desktop tool like DBeaver / DBVisualizer
```
> sudo apt install postgresql-client
> psql -h localhost -d pgtest -U postgres
Password for user postgres: Srinivas123
psql (12.16 (Ubuntu 12.16-0ubuntu0.20.04.1), server 16.1 (Debian 16.1-1.pgdg120+1))

pgtest=# select * from authors;
 id |  name   |  type  
----+---------+--------
  1 | OReilly | Docker
(1 row)
pgtest=# exit
```

#### Connect from internet ( Use DBVisualizer on laptop )
connect string: jdbc:postgressql://18.220.31.188:5432/pgtest   password: example
 
## Deploy the postgresql connector in CC 
> :information_source: the configuration can be done manually in CC UI or use REST API. Use the appropriate kafka.* values reflecting your cloud cluster 
```
> curl --request GET --url "https://api.confluent.cloud/connect/v1/environments/env-z3y7v3/clusters/lkc-1w9gn5/connectors/pg_cc_source" --header 'Authorization: Basic '$CLOUD_AUTH64'' | jq '.'
{
  "name": "pg_cc_source",
  "type": "source",
  "config": {
    "cloud.environment": "prod",
    "cloud.provider": "aws",
    "connection.host": "18.220.31.188",
    "connection.password": "****************",
    "connection.port": "5432",
    "connection.user": "connector",
    "connector.class": "PostgresSource",
    "db.name": "pgtest",
    "kafka.api.key": "3PMFLZIHGACR7COK",
    "kafka.api.secret": "****************",
    "kafka.endpoint": "SASL_SSL://pkc-921jm.us-east-2.aws.confluent.cloud:9092",
    "kafka.region": "us-east-2",
    "name": "pg_cc_source",
    "output.data.format": "AVRO",
    "schema.pattern": "public",
    "ssl.rootcertfile": "",
    "table.whitelist": "authors",   <---- this is case sensitive
    "tasks.max": "1",
    "topic.prefix": "pgsource",
    "transaction.isolation.mode": "SERIALIZABLE"
  },
  "tasks": [
    {
      "connector": "pg_cc_source",
      "task": 0
    }
  ]
}
```
#### Check Status of the connector
```
> curl --request GET --url "https://api.confluent.cloud/connect/v1/environments/env-z3y7v3/clusters/lkc-1w9gn5/connectors/pg_cc_source/status" --header 'Authorization: Basic '$CLOUD_AUTH64'' | jq '.'
{
  "name": "pg_cc_source",
  "connector": {
    "state": "FAILED",
    "worker_id": "pg_cc_source",
    "trace": "Unable to validate configuration. If an update was made to the configuration, this means that the configuration was invalid, and the connector continues to operate on a previous configuration that passed validation. Errors:\ntable.whitelist: Table(s) don't exist or no SELECT privilege over Table(s) \"public.AUTHORS\"\n"
  },
  "tasks": [],
  "type": "source",
  "errors_from_trace": [],
  "validation_errors": [
    "table.whitelist: Table(s) don't exist or no SELECT privilege over Table(s) \"public.AUTHORS\""
  ],
  "override_message": ""
}
```
> :information_source: Table name is case sensitive, changed to authors from AUTHORS



#### Provide appropriate GRANTs 
```
postgres=# create USER connector WITH NOSUPERUSER CREATEDB CREATEROLE LOGIN ;
CREATE ROLE
                                           ^
postgres=# alter user connector with password 'Srinivas123';
ALTER ROLE

postgres=# \du+
                                    List of roles
 Role name |                         Attributes                         | Description 
-----------+------------------------------------------------------------+-------------
 connector | Create role, Create DB                                     | 
 postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS | 

postgres=# GRANT SELECT ON TABLE AUTHORS to connector;
ERROR:  relation "authors" does not exist

postgres=# \connect pgtest
You are now connected to database "pgtest" as user "postgres".

pgtest=# GRANT SELECT ON TABLE AUTHORS to connector;
GRANT
```
> :warning: You may see this error: Caused by: org.postgresql.util.PSQLException: FATAL: permission denied to start WAL sender
  Detail: Only roles with the REPLICATION attribute may start a WAL sender process.

> :warning: io.debezium.jdbc.JdbcConnectionException: ERROR: permission denied for database pgtest
```
pgtest=# alter user connector REPLICATION;
ALTER ROLE
pgtest=# \du+
                                    List of roles
 Role name |                         Attributes                         | Description
-----------+------------------------------------------------------------+-------------
 connector | Create role, Create DB, Replication                        |
 postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS |

pgtest=# GRANT CONNECT ON DATABASE pgtest TO connector;
GRANT
```

#### Check the status
```
> curl --request GET --url "https://api.confluent.cloud/connect/v1/environments/env-z3y7v3/clusters/lkc-1w9gn5/connectors/pg_cc_source/status" --header 'Authorization: Basic '$CLOUD_AUTH64'' | jq '.'
{
  "name": "pg_cc_source",
  "connector": {
    "state": "RUNNING",
    "worker_id": "pg_cc_source",
    "trace": ""
  },
  "tasks": [
    {
      "id": 0,
      "state": "RUNNING",
      "worker_id": "pg_cc_source",
      "msg": ""
    }
  ],
  "type": "source",
  "errors_from_trace": [],
  "validation_errors": [],
  "override_message": ""
}
```

> :warning: Though Connector deployed successfully, it was loading one row that exists in the authors table in a infinite loop.
> :information_source: Behaviour of the default mode: BULK. Need to have a column that can be used as a timestamp or increment 

#### Resolution ( mode: timestamp ,timestamp.column.name: "ts" )
```
pgtest=# create table movies (ID INT PRIMARY KEY NOT NULL, NAME TEXT NOT NULL, TYPE TEXT NOT NULL, TS TIMESTAMP without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'));
CREATE TABLE
pgtest=# insert into movies values (1, 'Avengers', 'Action');
INSERT 0 1
pgtest=# select * from movies;
 id |   name   |  type  |             ts             
----+----------+--------+----------------------------
  1 | Avengers | Action | 2023-11-14 21:05:42.192383
(1 row)

pgtest=# GRANT SELECT ON TABLE MOVIES to connector;
GRANT
```

#### ReDeploy after the above changes
```
> curl --request GET --url "https://api.confluent.cloud/connect/v1/environments/env-z3y7v3/clusters/lkc-1w9gn5/connectors/pg_cc_source_v2/config" --header 'Authorization: Basic '$CLOUD_AUTH64'' | jq '.'
{
  "name": "pg_cc_source_v2",
  "cloud.environment": "prod",
  "cloud.provider": "aws",
  "connection.host": "18.220.31.188",
  "connection.password": "****************",
  "connection.port": "5432",
  "connection.user": "postgres",
  "connector.class": "PostgresSource",
  "db.name": "pgtest",
  "kafka.api.key": "3PMFLZIHGACR7COK",
  "kafka.api.secret": "****************",
  "kafka.endpoint": "SASL_SSL://pkc-921jm.us-east-2.aws.confluent.cloud:9092",
  "kafka.region": "us-east-2",
  "output.data.format": "AVRO",
  "ssl.rootcertfile": "",
  "table.whitelist": "movies",
  "tasks.max": "1",
  "mode": "timestamp",
  "timestamp.column.name": "ts",
  "topic.prefix": "pgsource."
}
```


