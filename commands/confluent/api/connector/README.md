### Connector APIs
#### Get connect plugins
```
curl --request GET --url 'https://api.confluent.cloud/connect/v1/environments/env-w1moj/clusters/lkc-127p73/connector-plugins' --header 'Authorization: Basic '$CLOUD_BASIC'' | jq '.'
```
#### Create a DataGen Connector
```
curl --request POST \
--url 'https://api.confluent.cloud/connect/v1/environments/env-w1moj/clusters/lkc-127p73/connectors' \
--header 'Authorization: Basic '$CLOUD_BASIC'' \
--header 'content-type: application/json' \
--data '{ 
    "name": "DatagenSourceConnector_2",
    "config": {
      "connector.class": "DatagenSource", 
      "name": "DatagenSourceConnector_2", 
      "kafka.api.key": "RYP7XXXXV2OAJGQ",
      "kafka.api.secret": "qe+hVKqx/L4kNfv6C9HR82XXXXXXXX+e5jB2tzHKCtnHTrZ8tYCXUVDSe40wboW9",
      "topics": "transactions",
      "tasks.max": "1"
    }
}' | jq '.'
```
#### Create with PUT a MySQL Sink COnnector
```
curl --request PUT \
--url "https://api.confluent.cloud/connect/v1/environments/${ENV_ID}/clusters/${CLUSTER_ID}/connectors/MySqlSinkConnector_2/config" \
--header 'Authorization: Basic '$CLOUD_AUTH64'' \
--header 'content-type: application/json' \
--data '{ 
    "connector.class": "MySqlSink", 
    "name": "MySqlSinkConnector_2", 
    "topics": "transactions2",
    "input.data.format": "AVRO",
    "input.key.format": "STRING",
    "kafka.api.key": "'$CLUSTER_KEY'",
    "kafka.api.secret": "'$CLUSTER_SECRET'",
    "connection.host": "ec2-18-218-62-3.us-east-2.compute.amazonaws.com",
    "connection.port": "3306",
    "connection.user": "kc101user",
    "connection.password": "kc101pw",
    "db.name": "demo",
    "ssl.mode": "prefer",
    "pk.mode": "none",
    "auto.create": "true",
    "auto.evolve": "true",
    "tasks.max": "1"
}' | jq '.'
```

#### Get the config of a connector
```
curl --request GET \
--url "https://api.confluent.cloud/connect/v1/environments/${ENV_ID}/clusters/${CLUSTER_ID}/connectors/DatagenSourceConnector_2/config" \
--header 'Authorization: Basic '$CLOUD_AUTH64'' | jq '.'
```
#### Query specific connector status
```
curl --request GET \
--url "https://api.confluent.cloud/connect/v1/environments/${ENV_ID}/clusters/${CLUSTER_ID}/connectors/MySqlSinkConnector_2/status" \
--header 'Authorization: Basic '$CLOUD_AUTH64'' | jq '.'
```
#### Query all connectors status
```
curl --request GET \
--url "https://api.confluent.cloud/connect/v1/environments/${ENV_ID}/clusters/${CLUSTER_ID}/connectors?expand=status" \
--header 'Authorization: Basic '$CLOUD_AUTH64'' | jq '.'
```


#### List the connectors deployed
query params ?expand=status ?expand=info can be used for additional stte info or metatdta of each connector
```
curl --request GET \
--url 'https://api.confluent.cloud/connect/v1/environments/${ENV_ID}/clusters/${CLUSTER_ID}/connectors'
--header 'Authorization: Basic '${CLOUD_AUTH64}'' | jq '.'
```

#### Delete a connector
```
curl --request DELETE \
--url "https://api.confluent.cloud/connect/v1/environments/${ENV_ID}/clusters/${CLUSTER_ID}/connectors/DatagenSourceConnector_2" \
--header 'Authorization: Basic '$CLOUD_AUTH64''
```
#### Pause a connector
```
curl --request PUT \
--url "https://api.confluent.cloud/connect/v1/environments/${ENV_ID}/clusters/${CLUSTER_ID}/connectors/MySqlSinkConnector_2/pause" \
--header 'Authorization: Basic '$CLOUD_AUTH64'' | jq '.'
```

#### Resume a connector
```
curl --request PUT \
--url "https://api.confluent.cloud/connect/v1/environments/${ENV_ID}/clusters/${CLUSTER_ID}/connectors/MySqlSinkConnector_2/resume" \
--header 'Authorization: Basic '$CLOUD_AUTH64'' | jq '.'
```
#### Restart a connector task
```
curl --request POST \
--url "https://api.confluent.cloud/connect/v1/environments/${ENV_ID}/clusters/${CLUSTER_ID}/connectors/MySqlSinkConnector_2/tasks/0/restart" \
--header 'Authorization: Basic '$CLOUD_AUTH64'' | jq '.'
```

#### Query last offsets processed
```
curl --request GET \
--url "https://api.confluent.cloud/connect/v1/environments/env-yky2gk/clusters/lkc-m15rj2/connectors/event-call-person-identified-snowflake-sink/offsets" \
--header 'Authorization: Basic '$CLOUD_AUTH64'' | jq '.'


{
  "id": "lcc-pq1dwo",
  "name": "event-call-person-identified-snowflake-sink",
  "offsets": [
    {
      "partition": {
        "kafka_partition": 1,
        "kafka_topic": "event-call-person-identified"
      },
      "offset": {
        "kafka_offset": 0
      }
    },
    {
      "partition": {
        "kafka_partition": 3,
        "kafka_topic": "event-call-person-identified"
      },
      "offset": {
        "kafka_offset": 0
      }
    },
    {
      "partition": {
        "kafka_partition": 5,
        "kafka_topic": "event-call-person-identified"
      },
      "offset": {
        "kafka_offset": 1
      }
    }
  ],
  "metadata": {
    "observed_at": "2026-02-10T03:08:14.709515360Z"
  }
}
```

#### Trace a connector ( CP )
```
curl -s -X PUT -H "Content-Type:application/json" \
    http://localhost:8083/admin/loggers/io.debezium \
    -d '{"level": "TRACE"}' \
    | jq '.'
[
  "io.debezium",
  "io.debezium.connector.mysql.MySqlConnector",
  "io.debezium.connector.postgresql.PostgresConnector",
  "io.debezium.util.IoUtil"
]
```
Revert Tracing to INFO
```
curl -s -X PUT -H "Content-Type:application/json" \
    http://localhost:8083/admin/loggers/org.apache.kafka.connect.runtime.WorkerSourceTask \
    -d '{"level": "INFO"}' \
    | jq '.'
```
