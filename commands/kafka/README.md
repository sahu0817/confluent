## Contents
- [Config](#Config)
- [Login](#Login)
- [Topic](#Topic)
- [Producer](#Producer)
- [Consumer](#Consumer)
- [Reset Offsets](#Reset-Offsets)
- [Consumer Groups](#Consumer-Groups)
- [Logging](#Logging)
- [Performance Test](#Performance-Test)
- [Rebalance Cluster](#Rebalance-Cluster)

### Config
#### Java Config
``` 
ssl.endpoint.identification.algorithm=https
sasl.mechanism=PLAIN
security.protocol=SASL_SSL
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="ERYZXXXXXXAYBMIU" password="6QLOwLojsEUyNGbXXXXXXXXXcervvX4pkvPWIKp24LeaL7+mgWLkGFhfNpbIG";
````


### Login
#### CC
```
> confluent login --save
email:
Password:
```
#### CC with SSO account and you cannot launch a browser
```
> confluent login --save --no-browser
email:
Password:
```

#### CP (RBAC enabled ) 
```
confluent login --url https://ip-172-32-58-28.us-west-2.compute.internal:8090
Enter your Confluent credentials:
Username: mds
Password: mds-secret
```

#### Get ClusterID
rbac.cfg
```
bootstrap.servers=ip-172-32-58-28.us-west-2.compute.internal:9094
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
ssl.truststore.location=/home/ubuntu/security/ssl/kafka-truststore.jks
ssl.truststore.password=changeme
ssl.keystore.location=/home/ubuntu/security/ssl/srini-keystore.jks
ssl.keystore.password=changeme
ssl.key.password=changeme
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required \
    username=alice \
    password="alice-secret";
```
```
kafka-cluster cluster-id --bootstrap-server ip-172-32-58-28.us-west-2.compute.internal:9094 --config rbac.cfg
Cluster ID: lw_j8rxUS22zKtvw7o2uQg
```

### Topic
#### Create a topic - CC

```
> confluent kafka topic create  testtopic --partitions 2
Created topic "testtopic".
```
#### Create with compact policy - CP
```
> kafka-topics --bootstrap-server localhost:9092 --create --topic compact1  --config cleanup.policy=compact --partitions 3
```
#### Create a topic with RecordNameStrategy - CC
```
> confluent kafka topic create firehose-multi-schema --config confluent.value.subject.name.strategy=io.confluent.kafka.serializers.subject.RecordNameStrategy --partitions  2
Created topic "firehose-multi-schema".
```
#### Change Topic Retention - CP
```
> kafka-configs --alter --bootstrap-server  localhost:9092 --entity-type topics --entity-name srini.testdb.testdb.testtable  --add-config retention.bytes=0
Completed updating config for topic srini.testdb.testdb.testtable.
```
```
> kafka-configs --alter --bootstrap-server  localhost:9092 --entity-type topics --entity-name srini.testdb.testdb.testtable  --add-config retention.ms=500
Completed updating config for topic srini.testdb.testdb.testtable.
```
#### Delete records in topic - ( Validate this )
```
> cat delete.json
{
  "partitions": [
    {
      "topic": "test1",
      "partition": 0,
      "offset": -1
    }
  ],
  "version": 1
}

> kafka-delete-records --bootstrap-server  pkc-ymrq7.us-east-2.aws.confluent.cloud:9092 --offset-json-file delete.json
Executing records delete operation
Records delete operation completed:
partition: test1-0      error: org.apache.kafka.common.errors.TimeoutException: Timed out waiting for a node assignment. Call: topicsMetadata
```
#### Compute Topic Size - CP

```
> kafka-log-dirs --bootstrap-server localhost:9092 --topic-list 'perf-test,test-topic' --describe  | grep '^{' | jq
{
  "brokers": [
    {
      "broker": 0,
      "logDirs": [
        {
          "partitions": [
            {
              "partition": "test-topic-0",
              "size": 167,
              "offsetLag": 0,
              "isFuture": false
            },
            {
              "partition": "perf-test-0",
              "size": 521217620,
              "offsetLag": 0,
              "isFuture": false
            }
          ],
          "error": null,
          "logDir": "/tmp/confluent.079104/kafka/data"
        }
      ]
    }
  ],
  "version": 1
}

> kafka-log-dirs --bootstrap-server localhost:9092 --topic-list 'perf-test,test-topic' --describe  | grep '^{'  \
| jq '[ ..|.size? | numbers ] | add'
521217787
```
#### Change Topic Retention - CC
```
confluent kafka topic update test1 --config "retention.ms=1"
Updated the following configuration values for topic "test1" (read-only configs were not updated):
      Name     | Value | Read-Only
---------------+-------+------------
  retention.ms |     1 | false
```
#### Disable auto topic creation
```
> confluent kafka cluster configuration update --config auto.create.topics.enable=false
Successfully requested to update configuration "auto.create.topics.enable".
```
#### Count messages in Topic
GetOffsetShell
```
[ubuntu@awst2x ~/confluent-7.6.0/bin]# ./kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic perf-test | awk -F ":" '{sum += $3} END {print sum}'
134181
```
ConsumerGroup
```
[ubuntu@awst2x ~/confluent-7.6.0/bin]# kafka-consumer-groups --bootstrap-server localhost:9092 --reset-offsets --to-earliest --topic perf-test --group TopicCountValidator --execute
GROUP                          TOPIC                          PARTITION  NEW-OFFSET     
TopicCountValidator            perf-test                      0          0              
TopicCountValidator            perf-test                      1          0              

[ubuntu@awst2x ~/confluent-7.6.0/bin]# kafka-consumer-groups --bootstrap-server localhost:9092 --group TopicCountValidator --describe 2>/dev/null | grep TopicCountValidator | awk -F ' ' '{sum += $6} END {print sum}'
134181
```
### Producer
#### Produce without schema to CC
```
kafka-console-producer --bootstrap-server pkc-ymrq7.us-east-2.aws.confluent.cloud:9092 --topic test1 --producer.config java.config
[2023-11-07 19:43:35,702] WARN The configuration 'session.timeout.ms' was supplied but isn't a known config. (org.apache.kafka.clients.producer.ProducerConfig)
>{"name": "hat", "price": 15.00, "quantity": 3}
>{"name": "shoes", "price": 72.00, "quantity": 1}
>{"name": "jacket", "price": 250.00, "quantity": 1}
^C
```

#### Produce with schema to CC (Note: create the same schema compact.avsc for the topic in CC - else the messages will be unreadable )
```
kafka-avro-console-producer --bootstrap-server pkc-ymrq7.us-east-2.aws.confluent.cloud:9092 --topic compact1 --producer.config java.config.srini_std  \
> --property key.serializer=org.apache.kafka.common.serialization.StringSerializer \
> --property parse.key=true --property key.separator=, \
> --property value.schema.file=$HOME/compact.avsc
one,{"seq":1}
two,{"seq":2}
three,{"seq":3}
four,{"seq":4}
one,{"seq":1}
^C
```
If you schema contains default NULL values you should pass the data as shown below to avoid this error
Error: Caused by: org.apache.avro.AvroTypeException: Expected start-union. Got VALUE_STRING
```
{"field1": { "string": "one"}, "field2": { "string": "two"} , "field3": { "string" : "three"}}
{"field1": { "string": "one"}, "field2": { "string": "two"} , "field3": { "string" : "three2"}}
{"field1": { "string": "one"}, "field2": { "string": "two"} , "field3": { "string" : "three3"}}
```

#### Produce with schema to CC (Note: This auto creates the schema )
```
kafka-avro-console-producer --bootstrap-server pkc-ymrq7.us-east-2.aws.confluent.cloud:9092 --topic synapse_cc_topic \
--producer.config java.config  \
--property basic.auth.credentials.source="USER_INFO" \
--property value.schema='{"type":"record","name":"myrecord","fields":[{"name":"name","type":"string"}, {"name":"price","type":"float"}, {"name":"quantity","type":"int"}]}' \
--property schema.registry.url="https://psrc-4r3n1.us-central1.gcp.confluent.cloud"  \
--property schema.registry.basic.auth.user.info="7DZCRXXXXX3NBY2Y:cds+qrG+ChOek+Oq+/gAxX+XXXXX/DI0cliF0KNAqSS7If+6TB2BSdUl26flWvq3" \
--property basic.auth.credentials.source="USER_INFO"
{"name": "shoes", "price": 72.00, "quantity": 1}
^C
```

#### Produce with schema to local CP
```
kafka-avro-console-producer --broker-list localhost:9092 --topic synapse_topic --property value.schema='{"type":"record","name":"myrecord","fields":[{"name":"name","type":"string"}, {"name":"price","type":"float"}, {"name":"quantity","type":"int"}]}'
{"name": "hat", "price": 15.00, "quantity": 3}
{"name": "shoes", "price": 72.00, "quantity": 1}
{"name": "jacket", "price": 250.00, "quantity": 1}
^C
```
### Consumer  
#### No Schema
```
confluent kafka topic consume --from-beginning -b test1
Starting Kafka Consumer. Use Ctrl-C to exit.
{"ordertime":1497014222380,"orderid":18,"itemid":"Item_184","address":{"city":"Mountain View","state":"CA","zipcode":94041}}
{"ordertime":1497014222380,"orderid":18,"itemid":"Item_184","address":{"city":"Mountain View","state":"CA","zipcode":94041}}
```
#### Avro schema
```
confluent kafka topic consume --from-beginning -b test1 --value-format=avro
```
#### With SchemaRegistry
```
confluent kafka topic consume -b transactions2 \
--value-format avro \
--api-key $CLOUD_KEY \
--api-secret $CLOUD_SECRET \
--schema-registry-endpoint $SCHEMA_REGISTRY_URL \
--schema-registry-api-key OPFQQXXXXXBZKMU \
--schema-registry-api-secret eGZrOlV5GuX539VDXXXXXXXXlX8ulD+GfPKZle5L6vCvoOCOrglNWFGzzB9
```
#### consume from a specific partition/offset and use jq to extract fields of interest
```
kafka-avro-console-consumer --bootstrap-server etsckci1s011.abc.amerisourcebergen.com:9092 \
--topic ATTP.SAPSR3.ZDT_SN_REQ \
--offset 538325 \
--partition 0 \
--consumer.config /app/ckc/client/client_ssl_mtls_rbac_9092.cfg \
--property schema.registry.url=https://etsckci1s003.abc.amerisourcebergen.com:8081 \
--property schema.registry.ssl.truststore.location=/opt/confluent/ssl/private/kafka_broker.truststore.jks \
--property schema.registry.ssl.truststore.password=XXXXXX \
--property basic.auth.credentials.source=USER_INFO \
--property basic.auth.user.info=stg_sckc_cp_meta_bnd:XXXXXX |grep MANDT|jq -c -M '[.ZZ_GUID,.ERDAT,.ERTIM,.op_type]'
```

#### consume from a connect offset
```
kafka-console-consumer --bootstrap-server ip-172-32-58-28.us-west-2.compute.internal:9094  --topic connect-cluster-offsets --from-beginning --property print.key=true --property print.timestamp=true --consumer.config srini.cfg
```

#### consume with rack.id enabled - FFF enabled clusters
Note: client.rack=\<AWS-Zone-ID\> NOT \<AWS-Zone-Name\>
```
confluent kafka topic consume eos-data-pipeline-test-topic --from-beginning --config="client.rack=use1-az6"
```
### Reset Offsets
#### Dry run
```
kafka-consumer-groups --bootstrap-server pkc-ymrq7.us-east-2.aws.confluent.cloud:9092 --command-config ccloud.cfg --reset-offsets --to-earliest  --group connect-lcc-qj20g2 --timeout 60000 --dry-run
Error: Assignments can only be reset if the group 'connect-lcc-qj20g2' is inactive, but the current state is Stable.
GROUP                          TOPIC                          PARTITION  NEW-OFFSET
```

#### Other types of resets
```
--reset-offsets --to-earliest --group $CONSUMER_GROUP --topic $TOPIC_NAME --execute
--reset-offsets --to-latest --group $CONSUMER_GROUP --topic $TOPIC_NAME --execute
--reset-offsets --to-datetime $RESET_VALUE --group $CONSUMER_GROUP --topic $TOPIC_NAME --execute
--reset-offsets --to-offset $RESET_VALUE --topic $TOPIC_NAME --group $CONSUMER_GROUP --execute
```
### Consumer Groups
#### list groups
```
kafka-consumer-groups --bootstrap-server pkc-ymrq7.us-east-2.aws.confluent.cloud:9092 --command-config ccloud.cfg --list --timeout 60000
_confluent-ksql-pksqlc-kwvq6query_CTAS_TEST_COLLECT_LIST_267
_confluent-ksql-pksqlc-kwvq6query_CTAS_TEST_COLLECT_SET_269
connect-lcc-qj20g2
_confluent-ksql-pksqlc-kwvq6query_CSAS_CUSTOMER_KNOWN_S_223
_confluent-ksql-pksqlc-kwvq6query_INSERTQUERY_307
_confluent-ksql-pksqlc-kwvq6query_CTAS_CUSTOMER_T_185
_confluent-ksql-pksqlc-kwvq6query_INSERTQUERY_309
_confluent-ksql-pksqlc-kwvq6query_CSAS_CUSTOMER_UNKNOWN_S_225
_confluent-ksql-pksqlc-kwvq6query_CSAS_ORDERS_ENRICHED_321
_confluent-ksql-pksqlc-kwvq6query_CTAS_TEST_COLLECT_LIST3_287
_confluent-ksql-pksqlc-kwvq6query_CSAS_MJ_ORDERS_ENRICHED_253
```

###  check current lag
#### Cloud
```
kafka-consumer-groups --bootstrap-server pkc-ymrq7.us-east-2.aws.confluent.cloud:9092 --command-config ccloud.cfg --describe --group connect-lcc-qj20g2 --timeout 60000
GROUP              TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID                                                          HOST            CLIENT-ID
connect-lcc-qj20g2 perf-test       4          -               608162          -               connector-consumer-lcc-qj20g2-0-fdb25a1d-b0a1-47a7-97b3-e90ee8fb8aaf /10.2.67.196    connector-consumer-lcc-qj20g2-0
connect-lcc-qj20g2 perf-test       3          -               608555          -               connector-consumer-lcc-qj20g2-0-fdb25a1d-b0a1-47a7-97b3-e90ee8fb8aaf /10.2.67.196    connector-consumer-lcc-qj20g2-0
connect-lcc-qj20g2 perf-test       0          -               598653          -               connector-consumer-lcc-qj20g2-0-fdb25a1d-b0a1-47a7-97b3-e90ee8fb8aaf /10.2.67.196    connector-consumer-lcc-qj20g2-0
connect-lcc-qj20g2 perf-test       5          -               599752          -               connector-consumer-lcc-qj20g2-0-fdb25a1d-b0a1-47a7-97b3-e90ee8fb8aaf /10.2.67.196    connector-consumer-lcc-qj20g2-0
connect-lcc-qj20g2 perf-test       1          -               621571          -               connector-consumer-lcc-qj20g2-0-fdb25a1d-b0a1-47a7-97b3-e90ee8fb8aaf /10.2.67.196    connector-consumer-lcc-qj20g2-0
connect-lcc-qj20g2 perf-test       2          -               591492          -               connector-consumer-lcc-qj20g2-0-fdb25a1d-b0a1-47a7-97b3-e90ee8fb8aaf /10.2.67.196    connector-consumer-lcc-qj20g2-0
```
### Dump topic log segments
#### CP
```
kafka-run-class kafka.tools.DumpLogSegments --deep-iteration --files 00000000000000000000.log
Dumping 00000000000000000000.log
Log starting offset: 0
baseOffset: 23 lastOffset: 23 count: 1 baseSequence: -1 lastSequence: -1 producerId: -1 producerEpoch: -1 partitionLeaderEpoch: 53 isTransactional: false isControl: false deleteHorizonMs: OptionalLong.empty position: 0 CreateTime: 1684431608579 size: 578 magic: 2 compresscodec: none crc: 2469842181 isvalid: true
| offset: 23 CreateTime: 1684431608579 keySize: 19 valueSize: 489 sequence: -1 headerKeys: []
```

### Logging
#### Get current log levels
kafka-configs --bootstrap-server localhost:9092 --describe \
--entity-type broker-loggers --entity-name 0

#### Set log level to DEBUG for the broker request logger for broker with id 0:
```
kafka-configs --bootstrap-server <bootstrap-server:port> --alter \
  --add-config "kafka.request.logger=DEBUG" \
  --entity-type broker-loggers --entity-name 0
```
#### Set root log level to DEBUG for the broker logger for broker with id 0:
```
kafka-configs --bootstrap-server <bootstrap-server:port> --alter \
--add-config "root=DEBUG" \
--entity-type broker-loggers --entity-name 0
```
#### Remove dynamic logging level setting for broker with id 0:
```
kafka-configs --bootstrap-server <bootstrap-server:port> --alter \
--delete-config kafka.request.logger \
--entity-type broker-loggers --entity-name 0
```

### Performance Test
#### CP ( 1ms latency )
```
> kafka-producer-perf-test --topic perf-test --record-size 5000 --throughput 1000 --num-records 1000000 --producer-props bootstrap.servers=localhost:9092 acks=all linger.ms=0 compression.type=lz4
4999 records sent, 999.8 records/sec (4.77 MB/sec), 21.8 ms avg latency, 727.0 ms max latency.
5003 records sent, 1000.4 records/sec (4.77 MB/sec), 0.8 ms avg latency, 19.0 ms max latency.
5000 records sent, 1000.0 records/sec (4.77 MB/sec), 0.7 ms avg latency, 17.0 ms max latency.
5001 records sent, 1000.2 records/sec (4.77 MB/sec), 0.7 ms avg latency, 18.0 ms max latency.

```
#### CC
```
kafka-producer-perf-test --topic perf-test --record-size 1000 --throughput 100000 --num-records 1000000 --print-metrics --producer-props bootstrap.servers=pkc-ymrq7.us-east-2.aws.confluent.cloud:9092 acks=all linger.ms=100 --producer.config java.config

156017 records sent, 31203.4 records/sec (29.76 MB/sec), 672.1 ms avg latency, 1560.0 ms max latency.
218080 records sent, 43616.0 records/sec (41.60 MB/sec), 703.5 ms avg latency, 2215.0 ms max latency.
. . .
1000000 records sent, 45945.325063 records/sec (43.82 MB/sec), 586.13 ms avg latency, 2912.00 ms max latency, 393 ms 50th, 2696 ms 95th, 2865 ms 99th, 2903 ms 99.9th.

Metric Name                                                                                                                     Value
app-info:commit-id:{client-id=perf-producer-client}                                                                           : c70f323bfaccf78e
app-info:start-time-ms:{client-id=perf-producer-client}                                                                       : 1696533320147
app-info:version:{client-id=perf-producer-client}                                                                             : 7.1.1-ce
. . .
```

```
kafka-producer-perf-test --topic perf-test --record-size 1000 --throughput 100000 --num-records 1000000 --print-metrics --producer-props bootstrap.servers=pkc-ymrq7.us-east-2.aws.confluent.cloud:9092 acks=all linger.ms=100 batch.size=300000 compression.type=lz4 --producer.config java.config

225670 records sent, 45116.0 records/sec (43.03 MB/sec), 144.9 ms avg latency, 1144.0 ms max latency.
291712 records sent, 58330.7 records/sec (55.63 MB/sec), 31.6 ms avg latency, 206.0 ms max latency.
292030 records sent, 58324.3 records/sec (55.62 MB/sec), 23.5 ms avg latency, 131.0 ms max latency.
1000000 records sent, 54653.768377 records/sec (52.12 MB/sec), 54.72 ms avg latency, 1144.00 ms max latency, 21 ms 50th, 288 ms 95th, 607 ms 99th, 663 ms 99.9th.

Metric Name                                                                                                                     Valueo
. . .
producer-topic-metrics:record-send-rate:{client-id=perf-producer-client, topic=perf-test}                                     : 21134.053
producer-topic-metrics:record-send-total:{client-id=perf-producer-client, topic=perf-test}                                    : 1000000.000
```
#### When the record size is larger than max.request.size
```
kafka-producer-perf-test --topic perf-test --record-size 1020000 --throughput 100000 --num-records 1000000 --print-metrics --producer-props acks=all linger.ms=100 batch.size=10000 compression.type=lz4 max.request.size=5000 --producer.config java.config
org.apache.kafka.common.errors.RecordTooLargeException: The message is 1020087 bytes when serialized which is larger than 5000, which is the value of the max.request.size configuration.
org.apache.kafka.common.errors.RecordTooLargeException: The message is 1020087 bytes when serialized which is larger than 5000, which is the value of the max.request.size configuration.
org.apache.kafka.common.errors.RecordTooLargeException: The message is 1020087 bytes when serialized which is larger than 5000, which is the value of the max.request.size configuration.
```

### Rebalance Cluster
#### Check Cluster Balancer Service
```
> kafka-rebalance-cluster --bootstrap-server localhost:9092 --status
Balancer status: ENABLED
Balancer is running on brokers: [0]
```
