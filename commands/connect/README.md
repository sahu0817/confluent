## Connect 
### CC
#### List connectors
```
> confluent connect cluster list
      ID     |           Name           | Status  | Type | Trace  
-------------+--------------------------+---------+------+--------
  lcc-gwrxjr | AzureBlobSinkConnector_0 | RUNNING | sink |  
```

#### Describe connector
```
confluent connect cluster describe lcc-gwrxjr
Connector Details
+--------+--------------------------+
| ID     | lcc-gwrxjr               |
| Name   | AzureBlobSinkConnector_0 |
| Status | RUNNING                  |
| Type   | sink                     |
+--------+--------------------------+


Task Level Details
  Task ID |  State   
----------+----------
        0 | RUNNING  

Configuration Details
            Config            |                          Value                           
------------------------------+----------------------------------------------------------
  azblob.account.key          | ****************                                         
  azblob.account.name         | ****************                                         
  azblob.container.name       | srinivassahu                                             
  cloud.environment           | prod                                                     
  cloud.provider              | azure                                                    
  connector.class             | AzureBlobSink                                            
  flush.size                  | 2                                                        
  input.data.format           | AVRO                                                     
  kafka.api.key               | ****************                                         
  kafka.api.secret            | ****************                                         
  kafka.auth.mode             | KAFKA_API_KEY                                            
  kafka.endpoint              | SASL_SSL://pkc-ryzn9.westus3.azure.confluent.cloud:9092  
  kafka.region                | westus3                                                  
  max.poll.interval.ms        | 60000                                                    
  name                        | AzureBlobSinkConnector_0                                 
  output.data.format          | AVRO                                                     
  rotate.interval.ms          | 600000                                                   
  rotate.schedule.interval.ms | 600000                                                   
  tasks.max                   | 1                                                        
  time.interval               | HOURLY                                                   
  topics                      | abs_avro 
```
#### Pause Connector
```
> confluent connect cluster pause lcc-gwrxjr
Paused connector "lcc-gwrxjr".

> confluent connect cluster describe lcc-gwrxjr
Connector Details
+--------+--------------------------+
| ID     | lcc-gwrxjr               |
| Name   | AzureBlobSinkConnector_0 |
| Status | PAUSED                   |
| Type   | sink                     |
+--------+--------------------------+


Task Level Details
  Task ID |  State   
----------+----------
        0 | STOPPED  

```
#### Resume Connector
```
> confluent connect cluster resume lcc-gwrxjr
Resumed connector "lcc-gwrxjr".
```

#### Connect log events
> The types of events logged in the topic are currently limited to io.confluent.logevents.connect.TaskFailed and io.confluent.logevents.connect.ConnectorFailed.

> Audit logs & connect event logs are in the same kafka cluster and same service account
```
[ubuntu@awst2x ~]# confluent connect event describe
+-----------------+------------------------------+
| Cluster         | lkc-0kqvp                    |
| Environment     | env-q5yy6                    |
| Service Account | sa-4jgq7w                    |
| Topic Name      | confluent-connect-log-events |
+-----------------+------------------------------+

[ubuntu@awst2x ~]# confluent environment use env-q5yy6  
Using environment "env-q5yy6".

[ubuntu@awst2x ~]# confluent kafka cluster use lkc-0kqvp 
Set Kafka cluster "lkc-0kqvp" as the active cluster for environment "env-q5yy6".

[ubuntu@awst2x ~]# confluent api-key create --service-account sa-4jgq7w --resource lkc-0kqvp   
It may take a couple of minutes for the API key to be ready.
Save the API key and secret. The secret is not retrievable later.
+------------+------------------------------------------------------------------+
| API Key    | XFQRHFS3NSF3REP4                                                 |
| API Secret | AuWKv********************************************************ET5 |
+------------+------------------------------------------------------------------+

[ubuntu@awst2x ~]# confluent api-key use XFQRHFS3NSF3REP4 --resource lkc-0kqvp  
Using API Key "XFQRHFS3NSF3REP4".

[ubuntu@awst2x ~]# confluent kafka topic consume -b confluent-connect-log-events
```
### CP
#### List connect Plugins installed

```
> confluent local services connect plugin list

OR

> curl --request GET --url localhost:8083/connector-plugins  | jq
 
[
  {
    "class": "io.confluent.connect.azure.datalake.gen2.AzureDataLakeGen2SinkConnector",
    "type": "sink",
    "version": "1.6.18"
  },
  {
    "class": "io.confluent.connect.azuresqldw.AzureSqlDwSinkConnector",
    "type": "sink",
    "version": "1.0.6"
  },
  {
    "class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "type": "sink",
    "version": "14.0.11"
  },
  {
    "class": "io.confluent.connect.replicator.ReplicatorSourceConnector",
    "type": "source",
    "version": "7.1.1"
  },
  {
    "class": "io.confluent.connect.servicenow.ServiceNowSinkConnector",
    "type": "sink",
    "version": "2.3.9"
  }
]
```

#### Check local connect logs
```
 confluent local services connect log
```
#### Validate a connector configuration

> Look for errors []
```
> curl -X PUT -H "Content-Type: application/json" --url http://localhost:8083/connector-plugins/PostgresConnector/config/validate -d @pg_conn.json | jq

{
  "name": "io.debezium.connector.postgresql.PostgresConnector",
  "error_count": 1,
  "groups": [
    "Common",
    "Transforms",
    "Predicates",
    "Error Handling",
    "Topic Creation",
    "Exactly Once Support",
    "offsets.topic",
    "Postgres",
    "Connector",
    "Events"
  ],
  "configs": [
. . .
      {
      "definition": {
        "name": "database.server.name",
        "type": "STRING",
        "required": false,
        "default_value": null,
        "importance": "HIGH",
        "documentation": "Unique name that identifies the database server and all recorded offsets, and that is used as a prefix for all schemas and topics. Each distinct installation should have a separate namespace and be monitored by at most one Debezium connector.",
        "group": "Postgres",
        "width": "MEDIUM",
        "display_name": "Namespace",
        "dependents": [],
        "order": 1
      },
      "value": {
        "name": "database.server.name",
        "value": null,
        "recommended_values": [],
        "errors": [
          "A value is required"
        ],
        "visible": true
      }
    },
. . .
```
#### Check status of a connector
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
      "state": "FAILED",
      "worker_id": "172.31.14.247:8083",
      "trace": "io.debezium.DebeziumException: Creation of replication slot failed\n\tat io.debezium.connector.postgresql.PostgresConnectorTask.start(PostgresConnectorTask.java:147)\n\tat io.debezium.connector.common.BaseSourceTask.startIfNeededAndPossible(BaseSourceTask.java:244)\n\tat io.debezium.connector.common.BaseSourceTask.poll(BaseSourceTask.java:153)\n\tat org.apache.kafka.connect.runtime.WorkerSourceTask.poll(WorkerSourceTask.java:307)\n\tat org.apache.kafka.connect.runtime.WorkerSourceTask.execute(WorkerSourceTask.java:263)\n\tat org.apache.kafka.connect.runtime.WorkerTask.doRun(WorkerTask.java:200)\n\tat org.apache.kafka.connect.runtime.WorkerTask.run(WorkerTask.java:255)\n\tat java.base/java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:515)\n\tat java.base/java.util.concurrent.FutureTask.run(FutureTask.java:264)\n\tat java.base/java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1128)\n\tat java.base/java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:628)\n\tat java.base/java.lang.Thread.run(Thread.java:829)\nCaused by: org.postgresql.util.PSQLException: ERROR: could not access file \"decoderbufs\": No such file or directory\n\tat org.postgresql.core.v3.QueryExecutorImpl.receiveErrorResponse(QueryExecutorImpl.java:2676)\n\tat org.postgresql.core.v3.QueryExecutorImpl.processResults(QueryExecutorImpl.java:2366)\n\tat org.postgresql.core.v3.QueryExecutorImpl.execute(QueryExecutorImpl.java:356)\n\tat org.postgresql.jdbc.PgStatement.executeInternal(PgStatement.java:496)\n\tat org.postgresql.jdbc.PgStatement.execute(PgStatement.java:413)\n\tat org.postgresql.jdbc.PgStatement.executeWithFlags(PgStatement.java:333)\n\tat org.postgresql.jdbc.PgStatement.executeCachedSql(PgStatement.java:319)\n\tat org.postgresql.jdbc.PgStatement.executeWithFlags(PgStatement.java:295)\n\tat org.postgresql.jdbc.PgStatement.execute(PgStatement.java:290)\n\tat io.debezium.connector.postgresql.connection.PostgresReplicationConnection.createReplicationSlot(PostgresReplicationConnection.java:451)\n\tat io.debezium.connector.postgresql.PostgresConnectorTask.start(PostgresConnectorTask.java:140)\n\t... 11 more\n"
    }
  ],
  "type": "source"
}

```
#### Delete a connector
```
> curl -X DELETE -H "Content-Type: application/json" --url http://localhost:8083/connectors/pg_conn

> curl -X GET -H "Content-Type: application/json" --url http://localhost:8083/connectors/pg_conn/status | jq
{
  "error_code": 404,
  "message": "No status found for connector pg_conn"
}
```

#### List Log Level for specific logger
```
> curl -Ss -X GET http://localhost:8083/admin/loggers/root | jq
{
  "level": "INFO"
}

> curl -Ss -X PUT -H "Content-Type:application/json" -d '{"level": "DEBUG"}' http://localhost:8083/admin/loggers/com.clickhouse.client.AbstractClient | jq
[
  "com.clickhouse.client.AbstractClient"
]

> curl -Ss -X GET http://localhost:8083/admin/loggers/ | jq
{
  "com.clickhouse.client.AbstractClient": {
    "level": "DEBUG"
  },
  "com.clickhouse.client.AbstractSocketClient": {
    "level": "INFO"
  },
  "com.clickhouse.client.ClickHouseClientBuilder": {
    "level": "INFO"
  },
  . . .
```
