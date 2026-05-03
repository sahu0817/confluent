# TimeScale - PostGres Sink Connector in Confluent Cloud
## Contents
- [Timescale Cloud Service](#Timescale-Cloud-Service)
- [Create topic in Confluent Cloud](#Create-topic-in-Confluent-Cloud-with-AVRO-Schema)
- [Configure Postgres sink connector in Confluent Cloud](#Configure-Postgres-sink-connector-in-Confluent-Cloud)
- [Produce data to topic](#Produce-data-to-topic)
- [Verify the connector sinking to timescale](#Verify-the-connector-sinking-to-timescale) 

## Timescale Cloud Service 
#### Subscribe to Timescale Cloud Trial
```
Service: ts-50641
username: tsdbadmin
password: das6********0758
Service URL: postgres://tsdbadmin@d8h2q63cyd.wf2bp5g6ly.tsdb.cloud.timescale.com:30337/tsdb?sslmode=require
Database name: tsdb
Host: postgres://tsdbadmin@d8h2q63cyd.wf2bp5g6ly.tsdb.cloud.timescale.com:30337/tsdb?sslmode=require
Port: 30337
```

[![TimeScale Subscription](../../images/timescale/timescale_subscription.png)]()

#### Connectivity test
> Install psql client: sudo apt-get install -y postgresql-client
>> > psql --version
>> psql (PostgreSQL) 12.16 (Ubuntu 12.16-0ubuntu0.20.04.1)
```
> psql "postgres://tsdbadmin:das6******0758@d8h2q63cyd.wf2bp5g6ly.tsdb.cloud.timescale.com:30337/tsdb?sslmode=require"
psql (12.16 (Ubuntu 12.16-0ubuntu0.20.04.1), server 16.3 (Ubuntu 16.3-1.pgdg22.04+1))
WARNING: psql major version 12, server major version 16.
         Some psql features might not work.
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
Type "help" for help.

tsdb=> quit
```

## Create topic in Confluent Cloud with AVRO Schema
```
ts_avro
```
[![TimeScale CC Topic](../../images/timescale/timescale_cc_topic.png)]()

## Configure Postgres sink connector in Confluent Cloud

```
{
  "name": "natus_timescale_sink",
  "tasks.max": "1",
  "topics": "ts_avro"
  "auto.create": "true",
  "auto.evolve": "true",
  "connection.host": "d8h2q63cyd.wf2bp5g6ly.tsdb.cloud.timescale.com",
  "connection.password": "****************",
  "connection.port": "30337",
  "connection.user": "tsdbadmin",
  "connector.class": "PostgresSink",
  "db.name": "tsdb",
  "input.data.format": "AVRO",
  "kafka.api.key": "3RHMLHYFDUW3GYY6",
  "kafka.api.secret": "****************"  
}

```
## Produce data to topic
```
> kafka-avro-console-producer --bootstrap-server pkc-921jm.us-east-2.aws.confluent.cloud:9092 --topic ts_avro --producer.config java.config  \
--property value.schema.file=./ts_avro.avsc \
--property schema.registry.url="https://psrc-mw0d1.us-east-2.aws.confluent.cloud" \
--property schema.registry.basic.auth.credentials.source="USER_INFO" \
--property schema.registry.basic.auth.user.info="*************:******************************"

{"name": "srinivas", "empid": 100, "city": "Dallas"}
{"name": "jesse", "empid": 101, "city": "NewYork"}
{"name": "vincent", "empid": 102, "city": "Paris"}
^C
```
## Verify the connector sinking to timescale
> Use PopSQL app (click on link on Timscale page) to query table

[![Timescale Data](../../images/timescale/timescale_data.png)]()


