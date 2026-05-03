## Contents
- [CP Local](#CP-Local)
    - [CP Local Schema Exporter ](#CP-Local-Schema-Exporter)
- [CP Docker](#CP-Docker)

 
## CP Local
### Start
```
[ubuntu@awst2x ~/confluent-7.7.1/bin]# ./confluent local services start
The local commands are intended for a single-node development environment only, NOT for production usage. See more: https://docs.confluent.io/current/cli/index.html
As of Confluent Platform 8.0, Java 8 will no longer be supported.

Using CONFLUENT_CURRENT: /tmp/confluent.192827
ZooKeeper is [UP]
Starting Kafka
Kafka is [UP]
Starting Schema Registry
Schema Registry is [UP]
Starting Kafka REST
Kafka REST is [UP]
Starting Connect
Connect is [UP]
Starting ksqlDB Server
ksqlDB Server is [UP]
Starting Control Center
Control Center is [UP]
```
### Logs
```
[ubuntu@awst2x ~/confluent-7.7.1/bin]# ./confluent local  current
/tmp/confluent.192827
```
```
[ubuntu@awst2x /tmp/confluent.192827]# ls
connect  control-center  kafka  kafka-rest  ksql-server  schema-registry  zookeeper
```
### Status
```
[ubuntu@awst2x ~/confluent-7.7.1/bin]# ./confluent local services status
Using CONFLUENT_CURRENT: /tmp/confluent.192827
Connect is [UP]
Control Center is [UP]
Kafka is [UP]
Kafka REST is [UP]
ksqlDB Server is [UP]
Schema Registry is [UP]
ZooKeeper is [UP]
```
```
[ubuntu@awst2x ~/confluent-7.7.1/bin]# ./confluent local services schema-registry status
Using CONFLUENT_CURRENT: /tmp/confluent.192827
Schema Registry is [UP]
```
### Create Topic, Produce, Delete Topic 
```
[ubuntu@awst2x ~/customer/marchex]# kafka-topics --bootstrap-server localhost:9092 --create --topic test_topic
WARNING: Due to limitations in metric names, topics with a period ('.') or underscore ('_') could collide. To avoid issues it is best to use either, but not both.
Created topic test_topic.
```
```
[ubuntu@awst2x ~/customer/marchex]# kafka-avro-console-producer --broker-list localhost:9092 --topic test_topic --property value.schema='{"type":"record","name":"myrecord","fields":[{"name":"name","type":"string"}, {"name":"price","type":"float"}, {"name":"quantity","type":"int"}]}'
. . .
{"name": "hat", "price": 15.00, "quantity": 3}
{"name": "shoes", "price": 72.00, "quantity": 1}
{"name": "jacket", "price": 250.00, "quantity": 1}
```
```
[ubuntu@awst2x ~/customer/marchex]# kafka-topics --bootstrap-server localhost:9092 --delete --topic test_topic
```
### Register Schema ( with ruleSet )
Ref: https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html#data-quality-rules
```
[ubuntu@awst2x ~/customer/marchex]# curl -X POST http://localhost:8081/subjects/topic2-value/versions \
-H "Content-Type: application/vnd.schemaregistry.v1+json" \
-d '{"subject":"topic2-value","schemaType":"JSON","schema":"{\"$schema\":\"http://json-schema.org/draft-07/schema#\",\"title\":\"User\",\"type\":\"object\",\"additionalProperties\":false,\"properties\":{\"name\":{\"oneOf\":[{\"type\":\"null\",\"title\":\"Not included\"},{\"type\":\"string\"}]}}}",
     "ruleSet": {"domainRules": [{
         "name": "checkNameLength",
         "kind": "CONDITION",
         "mode": "WRITE",
         "type": "CEL",
         "expr": "size(message.name) < 2",
         "disabled": false
      }]}}'

{"id":3}
```

### List Schemas
```
[ubuntu@awst2x ~/customer/marchex]# curl -s http://localhost:8081/subjects
["test_topic-value","topic2-value"]
```
### Stop
```
[ubuntu@awst2x ~/confluent-7.7.1/bin]# ./confluent local services stop
Using CONFLUENT_CURRENT: /tmp/confluent.192827
Stopping Control Center
Control Center is [DOWN]
Stopping ksqlDB Server
ksqlDB Server is [DOWN]
Stopping Connect
Connect is [DOWN]
Stopping Kafka REST
Kafka REST is [DOWN]
Stopping Schema Registry
Schema Registry is [DOWN]
Stopping Kafka
Kafka is [DOWN]
```

## CP Local Schema Exporter
### Start Exporter
```
[ubuntu@awst2x ~/customer/marchex]# schema-exporter --create --name cp-to-cloud-expoter --subjects ":*:" --context-type "DEFAULT" --config-file exporter_config.txt --schema.registry.url http://localhost:8081
Successfully created exporter cp-to-cloud-expoter
```
List running exporters
```
[ubuntu@awst2x ~/customer/marchex]# schema-exporter --list  --schema.registry.url http://localhost:8081
[cp-to-cloud-expoter]
```
#### Troubleshoot
If you get this error during create or list
```
io.confluent.kafka.schemaregistry.client.rest.exceptions.RestClientException: HTTP 404 Not Found; error code: 404
```
Update schema-registry.properties as below and restart

Ref: https://docs.confluent.io/platform/current/schema-registry/schema-linking-cp.html#configuration-snapshot-preview
```
[ubuntu@awst2x ~/confluent-7.7.1/etc/schema-registry]# tail -7 schema-registry.properties

#resource.extension.class=io.confluent.dekregistry.DekRegistryResourceExtension

#Added by Srinivas ( to enable schema linking ) - commented above
resource.extension.class=io.confluent.schema.exporter.SchemaExporterResourceExtension
kafkastore.update.handlers=io.confluent.schema.exporter.storage.SchemaExporterUpdateHandler
password.encoder.secret=mysecret
```

```
confluent local services restart
```

### Delete Exporter
```
[ubuntu@awst2x ~/customer/marchex]# schema-exporter --delete  --name cp-to-cloud-expoter --schema.registry.url http://localhost:8081
Successfully deleted exporter cp-to-cloud-expoter
```
## CP Docker
### Git clone
```
[ubuntu@awst2x ~/cp-all-in-one]# git clone https://github.com/confluentinc/cp-all-in-one.git
[ubuntu@awst2x ~/cp-all-in-one]# cd cp-all-in-one 
```
### Deploy
```
[ubuntu@awst2x ~/cp-all-in-one/cp-all-in-one]# docker compose up -d
[+] Running 78/7
 ✔ control-center 16 layers [⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿]      0B/0B      Pulled                                          109.5s
 ✔ rest-proxy 2 layers [⣿⣿]      0B/0B      Pulled                                                             105.3s
 ✔ schema-registry 2 layers [⣿⣿]      0B/0B      Pulled                                                        124.4s
 ✔ connect 14 layers [⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿]      0B/0B      Pulled                                                   137.6s
 ✔ prometheus 12 layers [⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿]      0B/0B      Pulled                                                    9.2s
 ✔ alertmanager 10 layers [⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿]      0B/0B      Pulled                                                   42.7s
 ✔ broker 15 layers [⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿]      0B/0B      Pulled                                                   126.0s
[+] Building 0.0s (0/0)
[+] Running 8/8
 ✔ Network cp-all-in-one_default  Created                                                                        0.4s
 ✔ Container prometheus           Started                                                                        7.2s
 ✔ Container broker               Started                                                                        7.2s
 ✔ Container alertmanager         Started                                                                        1.6s
 ✔ Container schema-registry      Started                                                                        1.4s
 ✔ Container connect              Started                                                                        2.1s
 ✔ Container rest-proxy           Started                                                                        2.0s
 ✔ Container control-center       Started                                                                        2.6s
```
### Launch ControlCenter
```
http://18.220.31.188:9021/
```
### List Schemas
```
#After creating topics & connector for mock data in c3  
[ubuntu@awst2x ~/cp-all-in-one/cp-all-in-one]# docker exec schema-registry curl -s http://localhost:8081/subjects
["pageviews-value","users-value"]
```
### Cleanup
```
[ubuntu@awst2x ~/cp-all-in-one/cp-all-in-one]# docker compose stop
[+] Stopping 7/7
 ✔ Container rest-proxy       Stopped                                                                            0.6s
 ✔ Container control-center   Stopped                                                                            1.7s
 ✔ Container connect          Stopped                                                                            1.7s
 ✔ Container alertmanager     Stopped                                                                            0.2s
 ✔ Container prometheus       Stopped                                                                            0.2s
 ✔ Container schema-registry  Stopped                                                                            0.9s
 ✔ Container broker           Stopped                                                                            4.4s
```
```
[ubuntu@awst2x ~/cp-all-in-one/cp-all-in-one]# docker system prune -a --volumes --filter "label=io.confluent.docker"
WARNING! This will remove:
  - all stopped containers
  - all networks not used by at least one container
  - all volumes not used by at least one container
  - all images without at least one container associated to them
  - all build cache

  Items to be pruned will be filtered with:
  - label=io.confluent.docker

Are you sure you want to continue? [y/N] y
Deleted Containers:
. . .
Total reclaimed space: 10.3GB
```
