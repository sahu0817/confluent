
# MSSQL Sink Connector for Confluent Cloud 
## Tutorial Workflow 
- Provisions a mssql server in Docker
- Provisions Cloud infrastructure with Terraform
  - Service Account
  - RBACs to Create Topics, Deadletter Queues, Describe cluster, Create & Delete Schemas
  - ACLs to CREATE, READ, WRITE to the Deadletter topic ( This should not be necessary if not for the bug: https://confluentinc.atlassian.net/browse/CC-39052 )
  - Create Topic
  - Create Schema
  - Deploy Connector
- Publish Events to the Topic
- Redeploy the connector to start from specific offsets

### Prerequisites 
- Confluent cloud cluster and a Cloud scoped Key & Secret for Terraform.
- A host to run mssql on docker with a public IP accessible from Confluent Cloud e.g AWS EC2-
- A SQL IDE like DBVisualizer or terminal SQLCMD Client - [Installation Instructions](https://learn.microsoft.com/en-us/sql/linux/sql-server-linux-setup-tools?view=sql-server-ver16&tabs=ubuntu-install#install-tools-on-linux)
  
## Tutorial    
- [Deploy MSSQL 2019 server in docker](#Deploy-mssql-2019-server-in-docker)
    - [Validate SQL Server Connectivity](#Validate-SQL-Server-Connectivity)
    - [SQL Server Initial Setup](#SQL-Server-Initial-Setup)
- [Deploy a Connector in Confluent Cloud with Terraform](#Deploy-a-Connector-in-Confluent-Cloud-with-Terraform)
    - [Check Status of the connector](#Check-Status-of-the-connector)
- [Produce Events to the topic](#Produce-Events-to-the-topic)
- [Validate the events in db table](#Validate-the-events-in-db-table)
- [Redeploy the connector to start from specific offsets](#Redeploy-the-connector-to-start-from-specific-offsets)
- [Troubleshoot](#Troubleshooting)
- [Cleanup](#Cleanup)
  


## Deploy MSSQL 2019 server in docker
#### Start mssql
```
> docker-compose up -d
[+] Running 1/1
 ✔ Container mssql  Started                                                                                

> docker ps

CONTAINER ID   IMAGE                                        COMMAND                  CREATED          STATUS          PORTS                                       NAMES
b9b6fb71331b   mcr.microsoft.com/mssql/server:2019-latest   "/opt/mssql/bin/perm…"   32 minutes ago   Up 32 minutes   0.0.0.0:5434->1433/tcp, :::5434->1433/tcp   mssql
```

#### Validate SQL Server connectivty
Connect within the container 
```
> docker exec -it mssql bash
root@ce8e821050f4:/# /opt/mssql-tools18/bin/sqlcmd -S localhost -U SA -P "Srinivas@1" -C
psql (16.1 (Debian 16.1-1.pgdg120+1))
Type "help" for help.

1> select 'connected from pod'
2> go

------------------
connected from pod
```
Connect from localhost
```
> sqlcmd -S localhost,5434 -U SA -P "Srinivas@1" -C -Q "select 'connected'"

---------
connected

(1 rows affected)
```
Connect from internet ( Use DBVisualizer like tool on laptop )
```
Database Server: 18.220.31.188
Port           : 5434
Database       : testdb 
Database Userid: SA
Database Password: Srinivas@1
```
#### SQL Server Initial Setup
This setup Creates database testdb, table Employee, Enables CDC, Inserts two rows to Employee table 
```
> sqlcmd -S localhost,5434 -U SA -P "Srinivas@1" -C -i setup.sql
Changed database context to 'testdb'.
Job 'cdc.testdb_capture' started successfully.
Job 'cdc.testdb_cleanup' started successfully.
source_schema source_table capture_instance object_id   source_object_id start_lsn              end_lsn supports_net_changes has_drop_pending     role_name  index_name                     filegroup_name create_date             index_column_list captured_column_list
------------- ------------- --------------- ----------- ---------------- ---------------------- ------- -------------------- -------------------- ---------- ------------------------------ -------------- ----------------------- ----------------- ---------------------------------------------
dbo           Employee     dbo_Employee     965578478   581577110        0x0000002800000B380040 NULL    0                    NULL                 cdc_reader PK__Employee__7AD04FF15CA69CC1 NULL      
  2025-04-26 00:04:18.267 [EmployeeID]      [EmployeeID], [FirstName], [LastName]

(1 rows affected)
(1 rows affected)
```

Note: If you see this msg that means the SQLServerAgent is NOT RUNNING
`SQLServerAgent is not currently running so it cannot be notified of this action.`

```
> sqlcmd -S localhost,5434 -U SA -P "Srinivas@1" -C -i check_agent.sql
Current Service State
------------------------------------------------------------------------------------------------------------------------------------
Running.

(1 rows affected)
```

## Deploy a Connector in Confluent Cloud with Terraform
> :information_source: You need a Cloud scoped Key / Secret to run Terraform script

```
~/connectors/mssql/terraform > env | grep TF
TF_VAR_confluent_cloud_api_key=xxxxxx
TF_VAR_confluent_cloud_api_secret=xxxxxxxxxxxx

~/connectors/mssql/terraform > terraform init

~/connectors/mssql/terraform > terraform plan
Plan: 18 to add, 0 to change, 0 to destroy.

~/connectors/mssql/terraform > terraform apply
. . .
confluent_service_account.service-account: Creation complete after 1s [id=sa-xq8m5qz]
confluent_api_key.schema-registry: Creation complete after 1m0s [id=ZCVMEGWPWM2FUUJI]
confluent_role_binding.schema-registry-access: Creation complete after 1m30s [id=rb-O2yVJ0]
confluent_role_binding.connector-consumer-group: Creation complete after 1m31s [id=rb-boWQ3Q]
confluent_role_binding.connector-developer-write: Creation complete after 1m31s [id=rb-G05Xbj]
confluent_role_binding.cloud-cluster-admin-for-acl: Creation complete after 1m31s [id=rb-ARmAQe]
confluent_role_binding.connector-developer-write-confluent-bug: Creation complete after 1m31s [id=rb-18OwRm]
confluent_role_binding.connector-cluster-operator: Creation complete after 1m31s [id=rb-oQOXK1]
confluent_role_binding.connector-developer-read: Creation complete after 1m31s [id=rb-weXq4r]
confluent_role_binding.connector-developer-write-dlt: Creation complete after 1m31s [id=rb-DELoj9]
confluent_schema.connector_topic: Creation complete after 11s [id=lsrc-mgog12/srinivas_mssql_sink_test-value/latest]
confluent_api_key.kafka: Creation complete after 2m2s [id=XB3HKAJ324K2N4TL]
confluent_kafka_topic.connector_topic: Creation complete after 11s [id=lkc-86p6xm/srinivas_mssql_sink_test]
confluent_role_binding.connector-resource-owner-dlt: Creation complete after 1m31s [id=rb-J2JNmV]
confluent_kafka_acl.dlq["READ"]: Creation complete after 10s [id=lkc-86p6xm/TOPIC#dlq-lcc#PREFIXED#User:sa-xq8m5qz#*#READ#ALLOW]
confluent_kafka_acl.dlq["WRITE"]: Creation complete after 10s [id=lkc-86p6xm/TOPIC#dlq-lcc#PREFIXED#User:sa-xq8m5qz#*#WRITE#ALLOW]
confluent_kafka_acl.dlq["DELETE"]: Creation complete after 10s [id=lkc-86p6xm/TOPIC#dlq-lcc#PREFIXED#User:sa-xq8m5qz#*#DELETE#ALLOW]
confluent_connector.sink: Creation complete after 5m12s [id=lcc-j6j2rw]

Apply complete! Resources: 18 added, 0 changed, 0 destroyed.
```

#### Check Status of the connector
```
> curl --request GET --url "https://api.confluent.cloud/connect/v1/environments/${ENV_ID}/clusters/${CLUSTER_ID}/connectors/${CONNECTOR_NAME}/status" --header 'Authorization: Basic '$CLOUD_AUTH'' | jq

{
  "name": "srinivas-mssql-sink-test",
  "connector": {
    "state": "RUNNING",
    "worker_id": "srinivas-mssql-sink-test",
    "trace": ""
  },
  "tasks": [
    {
      "id": 0,
      "state": "RUNNING",
      "worker_id": "srinivas-mssql-sink-test",
      "msg": ""
    }
  ],
  "type": "sink",
  "errors_from_trace": [],
  "validation_errors": [],
  "override_message": "",
  "validation_error_category_info": null,
  "is_csfle_error": false,
  "error_details": null,
  "error_summary": "",
  "error_recommendation_enabled": false,
  "plugin_lifecycle": "ACTIVE"
}
```
## Produce Events to the topic
```
> kafka-avro-console-producer --bootstrap-server pkc-09zmdp.us-east-1.aws.confluent.cloud:9092 --topic srinivas-mssql-sink-test \
--producer.config java.config  \
--property basic.auth.credentials.source="USER_INFO" \
--property value.schema.file=./schema.avsc \
--property schema.registry.url="https://psrc-1ymy5nj.us-east-1.aws.confluent.cloud" \
--property schema.registry.basic.auth.user.info="xxxx:xxxxxxxxxxx" \
--property basic.auth.credentials.source="USER_INFO"

{ "order_id": 1, "order_name": "test1" }
{ "order_id": 2, "order_name": "test2" }
^C
```
## Validate the events in db table
```
[ubuntu@mc ~/connectors/mssql/terraform]# docker exec -it mssql bash
mssql@6eeb76d57cfa:/$ /opt/mssql-tools18/bin/sqlcmd -S localhost -U SA -P "Srinivas@1" -C
1> use testdb;
2> go
Changed database context to 'testdb'.
1> select * from kafka_srinivas_mssql_sink_test;
2> go
order_id    order_name
----------- ------------ 
          1 test1
          2 test2

(2 rows affected)
```

## Redeploy the connector to start from specific offsets
ℹ️ Uncomment and update the offsets blocks in the main.tf. Update the kafka_partition & kafka_offset accordingly. Note the connector starts from the next offset.

```
~/connectors/mssql/terraform > terraform plan
. . .
Plan: 0 to add, 1 to change, 0 to destroy.

~/connectors/mssql/terraform > terraform apply
. . .
confluent_connector.sink: Modifications complete after 34s [id=lcc-99m6j7]

Apply complete! Resources: 0 added, 1 changed, 0 destroyed.
```

:warning: As the `insert.mode` is configured for `UPSERT` you do not see new rows in the table but the connector messages processed count should go up.

## Troubleshoot 
 

## Cleanup
#### Delete Cloud Infrastructure
```
[ubuntu@mc ~/connectors/mssql/terraform]# terraform destroy
. . .
confluent_connector.sink: Destruction complete after 1s
confluent_kafka_acl.dlq["WRITE"]: Destruction complete after 0s
confluent_kafka_acl.dlq["DELETE"]: Destruction complete after 0s
confluent_kafka_acl.dlq["READ"]: Destruction complete after 1s
confluent_role_binding.connector-developer-write: Destruction complete after 0s
confluent_role_binding.cloud-cluster-admin-for-acl: Destruction complete after 0s
confluent_role_binding.connector-developer-write-dlt: Destruction complete after 0s
confluent_role_binding.connector-resource-owner-dlt: Destruction complete after 0s
confluent_role_binding.connector-developer-read: Destruction complete after 0s
confluent_role_binding.connector-cluster-operator: Destruction complete after 0s
confluent_role_binding.connector-developer-write-confluent-bug: Destruction complete after 0s
confluent_role_binding.connector-consumer-group: Destruction complete after 0s
confluent_schema.connector_topic: Destruction complete after 10s
confluent_kafka_topic.connector_topic: Destruction complete after 11s
confluent_role_binding.schema-registry-access: Destruction complete after 0s
confluent_api_key.schema-registry: Destruction complete after 0s
confluent_api_key.kafka: Destruction complete after 0s
confluent_service_account.service-account: Destruction complete after 1s

Destroy complete! Resources: 18 destroyed.
```
#### Delete Docker
```
> docker-compose stop
> docker-compose rm
> docker volume prune
```

