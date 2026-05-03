### Kafka APIs
#### Query ORG
```
curl --request GET --url 'https://api.confluent.cloud/org/v2/environments' --header 'Authorization: Basic '$CLOUD_AUTH64''
```
#### Query Cluster
```
curl --request GET --url 'https://api.confluent.cloud/cmk/v2/clusters?environment=env-w1moj' --header 'Authorization: Basic '$CLOUD_AUTH64'' | jq '.'
```
<details>
  <summary>Output</summary>
  
  ```js 
  {
  "api_version": "cmk/v2",
  "data": [
    {
      "api_version": "cmk/v2",
      "id": "lkc-127p73",
      "kind": "Cluster",
      "metadata": {
        "created_at": "2022-10-04T22:08:16.296148Z",
        "resource_name": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-w1moj/cloud-cluster=lkc-127p73/kafka=lkc-127p73",
        "self": "https://api.confluent.cloud/cmk/v2/clusters/lkc-127p73",
        "updated_at": "2022-10-04T22:08:16.294491Z"
      },
      "spec": {
        "api_endpoint": "https://pkac-z32vd.us-west4.gcp.confluent.cloud",
        "availability": "SINGLE_ZONE",
        "cloud": "GCP",
        "config": {
          "kind": "Basic"
        },
        "display_name": "kc-101",
        "environment": {
          "api_version": "org/v2",
          "id": "env-w1moj",
          "kind": "Environment",
          "related": "https://api.confluent.cloud/org/v2/environments/env-w1moj",
          "resource_name": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-w1moj"
        },
        "http_endpoint": "https://pkc-6ojv2.us-west4.gcp.confluent.cloud:443",
        "kafka_bootstrap_endpoint": "SASL_SSL://pkc-6ojv2.us-west4.gcp.confluent.cloud:9092",
        "region": "us-west4"
      },
      "status": {
        "phase": "PROVISIONED"
      }
    },
    {
      "api_version": "cmk/v2",
      "id": "lkc-12x603",
      "kind": "Cluster",
      "metadata": {
        "created_at": "2022-09-22T21:38:28.46902Z",
        "resource_name": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-w1moj/cloud-cluster=lkc-12x603/kafka=lkc-12x603",
        "self": "https://api.confluent.cloud/cmk/v2/clusters/lkc-12x603",
        "updated_at": "2022-09-22T21:38:28.468711Z"
      },
      "spec": {
        "api_endpoint": "https://pkac-8m367.us-east-1.aws.confluent.cloud",
        "availability": "SINGLE_ZONE",
        "cloud": "AWS",
        "config": {
          "kind": "Standard"
        },
        "display_name": "anvesh-test",
        "environment": {
          "api_version": "org/v2",
          "id": "env-w1moj",
          "kind": "Environment",
          "related": "https://api.confluent.cloud/org/v2/environments/env-w1moj",
          "resource_name": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-w1moj"
        },
        "http_endpoint": "https://pkc-2396y.us-east-1.aws.confluent.cloud:443",
        "kafka_bootstrap_endpoint": "SASL_SSL://pkc-2396y.us-east-1.aws.confluent.cloud:9092",
        "region": "us-east-1"
      },
      "status": {
        "phase": "PROVISIONED"
      }
    },
    {
      "api_version": "cmk/v2",
      "id": "lkc-381350",
      "kind": "Cluster",
      "metadata": {
        "created_at": "2022-09-06T14:09:14.47704Z",
        "resource_name": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-w1moj/cloud-cluster=lkc-381350/kafka=lkc-381350",
        "self": "https://api.confluent.cloud/cmk/v2/clusters/lkc-381350",
        "updated_at": "2022-09-06T14:31:25.146613Z"
      },
      "spec": {
        "api_endpoint": "https://lkaclkc-381350-g02k06.us-central1.gcp.glb.confluent.cloud:443",
        "availability": "SINGLE_ZONE",
        "cloud": "GCP",
        "config": {
          "cku": 1,
          "kind": "Dedicated",
          "zones": [
            "us-central1-a"
          ]
        },
        "display_name": "gcp_psc_cluster",
        "environment": {
          "api_version": "org/v2",
          "id": "env-w1moj",
          "kind": "Environment",
          "related": "https://api.confluent.cloud/org/v2/environments/env-w1moj",
          "resource_name": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-w1moj"
        },
        "http_endpoint": "https://lkc-381350-g02k06.us-central1.gcp.glb.confluent.cloud:443",
        "kafka_bootstrap_endpoint": "lkc-381350-g02k06.us-central1.gcp.glb.confluent.cloud:9092",
        "network": {
          "api_version": "networking/v1",
          "id": "n-g02k06",
          "kind": "Network",
          "related": "https://api.confluent.cloud/networking/v1/networks/n-g02k06",
          "resource_name": "crn://confluent.cloud/network=n-g02k06"
        },
        "region": "us-central1"
      },
      "status": {
        "cku": 1,
        "phase": "PROVISIONED"
      }
    },
    {
      "api_version": "cmk/v2",
      "id": "lkc-6k0wvj",
      "kind": "Cluster",
      "metadata": {
        "created_at": "2022-09-21T15:00:19.823243Z",
        "resource_name": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-w1moj/cloud-cluster=lkc-6k0wvj/kafka=lkc-6k0wvj",
        "self": "https://api.confluent.cloud/cmk/v2/clusters/lkc-6k0wvj",
        "updated_at": "2022-09-23T16:51:52.3816Z"
      },
      "spec": {
        "api_endpoint": "https://pkac-l7pjj.us-east4.gcp.confluent.cloud",
        "availability": "SINGLE_ZONE",
        "cloud": "GCP",
        "config": {
          "kind": "Basic"
        },
        "display_name": "jclark_learning_cluster",
        "environment": {
          "api_version": "org/v2",
          "id": "env-w1moj",
          "kind": "Environment",
          "related": "https://api.confluent.cloud/org/v2/environments/env-w1moj",
          "resource_name": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-w1moj"
        },
        "http_endpoint": "https://pkc-419q3.us-east4.gcp.confluent.cloud:443",
        "kafka_bootstrap_endpoint": "SASL_SSL://pkc-419q3.us-east4.gcp.confluent.cloud:9092",
        "region": "us-east4"
      },
      "status": {
        "phase": "PROVISIONED"
      }
    },
    {
      "api_version": "cmk/v2",
      "id": "lkc-6k70xj",
      "kind": "Cluster",
      "metadata": {
        "created_at": "2022-06-30T15:16:18.538164Z",
        "resource_name": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-w1moj/cloud-cluster=lkc-6k70xj/kafka=lkc-6k70xj",
        "self": "https://api.confluent.cloud/cmk/v2/clusters/lkc-6k70xj",
        "updated_at": "2022-08-08T13:56:04.000436Z"
      },
      "spec": {
        "api_endpoint": "https://pkac-03nxq.us-west4.gcp.confluent.cloud",
        "availability": "SINGLE_ZONE",
        "cloud": "GCP",
        "config": {
          "cku": 1,
          "kind": "Dedicated",
          "zones": [
            "us-west4-b"
          ]
        },
        "display_name": "abe_oauth_test",
        "environment": {
          "api_version": "org/v2",
          "id": "env-w1moj",
          "kind": "Environment",
          "related": "https://api.confluent.cloud/org/v2/environments/env-w1moj",
          "resource_name": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-w1moj"
        },
        "http_endpoint": "https://pkc-2172m.us-west4.gcp.confluent.cloud:443",
        "kafka_bootstrap_endpoint": "SASL_SSL://pkc-2172m.us-west4.gcp.confluent.cloud:9092",
        "region": "us-west4"
      },
      "status": {
        "cku": 1,
        "phase": "PROVISIONED"
      }
    },
    {
      "api_version": "cmk/v2",
      "id": "lkc-g6pom",
      "kind": "Cluster",
      "metadata": {
        "created_at": "2022-01-24T20:13:26.559232Z",
        "resource_name": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-w1moj/cloud-cluster=lkc-g6pom/kafka=lkc-g6pom",
        "self": "https://api.confluent.cloud/cmk/v2/clusters/lkc-g6pom",
        "updated_at": "2022-09-14T17:24:21.220265Z"
      },
      "spec": {
        "api_endpoint": "https://pkac-z32vd.us-west4.gcp.confluent.cloud",
        "availability": "SINGLE_ZONE",
        "cloud": "GCP",
        "config": {
          "kind": "Standard"
        },
        "display_name": "abe_cluster_for_cool_projects",
        "environment": {
          "api_version": "org/v2",
          "id": "env-w1moj",
          "kind": "Environment",
          "related": "https://api.confluent.cloud/org/v2/environments/env-w1moj",
          "resource_name": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-w1moj"
        },
        "http_endpoint": "https://pkc-6ojv2.us-west4.gcp.confluent.cloud:443",
        "kafka_bootstrap_endpoint": "SASL_SSL://pkc-6ojv2.us-west4.gcp.confluent.cloud:9092",
        "region": "us-west4"
      },
      "status": {
        "phase": "PROVISIONED"
      }
    },
    {
      "api_version": "cmk/v2",
      "id": "lkc-nvqnj6",
      "kind": "Cluster",
      "metadata": {
        "created_at": "2022-09-12T15:29:40.878359Z",
        "resource_name": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-w1moj/cloud-cluster=lkc-nvqnj6/kafka=lkc-nvqnj6",
        "self": "https://api.confluent.cloud/cmk/v2/clusters/lkc-nvqnj6",
        "updated_at": "2022-09-14T17:24:21.220265Z"
      },
      "spec": {
        "api_endpoint": "https://pkac-4nd3z.us-west4.gcp.confluent.cloud",
        "availability": "SINGLE_ZONE",
        "cloud": "GCP",
        "config": {
          "kind": "Basic"
        },
        "display_name": "CapstoneProject",
        "environment": {
          "api_version": "org/v2",
          "id": "env-w1moj",
          "kind": "Environment",
          "related": "https://api.confluent.cloud/org/v2/environments/env-w1moj",
          "resource_name": "crn://confluent.cloud/organization=4c8541f7-cc3f-44af-a366-ad4de432fe24/environment=env-w1moj"
        },
        "http_endpoint": "https://pkc-lzvrd.us-west4.gcp.confluent.cloud:443",
        "kafka_bootstrap_endpoint": "SASL_SSL://pkc-lzvrd.us-west4.gcp.confluent.cloud:9092",
        "region": "us-west4"
      },
      "status": {
        "phase": "PROVISIONED"
      }
    }
  ],
  "kind": "ClusterList",
  "metadata": {
    "first": "https://api.confluent.cloud/cmk/v2/clusters",
    "total_size": 7
  }
}
```
</details>

#### Create topic
```
curl --request POST \
--url "https://pkc-6ojv2.us-west4.gcp.confluent.cloud/kafka/v3/clusters/${CLUSTER_ID}/topics" \
--header 'Authorization: Basic '$CLUSTER_AUTH64'' \
--header 'content-type: application/json' \
--data '{ "topic_name": "transactions2", "partitions_count": 6, "replication_factor": 3 }' | jq '.'
```
<details>
  <summary>Output</summary>
  
  ```js 
  {
    "kind": "KafkaTopic",
    "metadata": {
      "self": "https://pkc-6ojv2.us-west4.gcp.confluent.cloud/kafka/v3/clusters/lkc-127p73/topics/transactions",
      "resource_name": "crn:///kafka=lkc-127p73/topic=transactions"
    },
    "cluster_id": "lkc-mv0817",
    "topic_name": "transactions2",
    "is_internal": false,
    "replication_factor": 3,
    "partitions_count": 0,
    "partitions": {
      "related": "https://pkc-6ojv2.us-west4.gcp.confluent.cloud/kafka/v3/clusters/lkc-127p73/topics/transactions/partitions"
    },
    "configs": {
      "related": "https://pkc-6ojv2.us-west4.gcp.confluent.cloud/kafka/v3/clusters/lkc-127p73/topics/transactions/configs"
    },
    "partition_reassignments": {
      "related": "https://pkc-6ojv2.us-west4.gcp.confluent.cloud/kafka/v3/clusters/lkc-127p73/topics/transactions/partitions/-/reassignment"
    },
    "authorized_operations": []
  }
  ```
</details>

#### Query Topic 
```
curl --request GET \
--url 'https://lkc-97pgvm-g4xj36.us-east-2.aws.glb.confluent.cloud:9092/kafka/v3/clusters/lkc-97pgvm/topics' \
--header 'Authorization: Basic '$CLUSTER_AUTH64'' | jq '.'
```

<details>
  <summary>Output</summary>
  
  ```js
  {
    "kind": "KafkaTopicList",
    "metadata": {
      "self": "https://pkc-6ojv2.us-west4.gcp.confluent.cloud/kafka/v3/clusters/lkc-127p73/topics",
      "next": null
    },
    "data": [
      {
        "kind": "KafkaTopic",
        "metadata": {
          "self": "https://pkc-6ojv2.us-west4.gcp.confluent.cloud/kafka/v3/clusters/lkc-127p73/topics/transactions",
          "resource_name": "crn:///kafka=lkc-127p73/topic=transactions"
        },
        "cluster_id": "lkc-mv0817",
        "topic_name": "transactions",
        "is_internal": false,
        "replication_factor": 3,
        "partitions_count": 6,
        "partitions": {
          "related": "https://pkc-6ojv2.us-west4.gcp.confluent.cloud/kafka/v3/clusters/lkc-127p73/topics/transactions/partitions"
        },
        "configs": {
          "related": "https://pkc-6ojv2.us-west4.gcp.confluent.cloud/kafka/v3/clusters/lkc-127p73/topics/transactions/configs"
        },
        "partition_reassignments": {
          "related": "https://pkc-6ojv2.us-west4.gcp.confluent.cloud/kafka/v3/clusters/lkc-127p73/topics/transactions/partitions/-/reassignment"
        },
        "authorized_operations": []
      }
    ] 
  }
  ```
</details>

#### Delete Topic 
```
curl --request DELETE \
--url "https://pkc-6ojv2.us-west4.gcp.confluent.cloud/kafka/v3/clusters/${CLUSTER_ID}/topics/transactions2" \
--header 'Authorization: Basic '$CLUSTER_AUTH64'' \
```
<details>
  <summary>Output</summary>
  
  ```js
  {
    "kind": "KafkaTopic",
    "metadata": {
      "self": "https://pkc-6ojv2.us-west4.gcp.confluent.cloud/kafka/v3/clusters/lkc-127p73/topics/transactions",
      "resource_name": "crn:///kafka=lkc-127p73/topic=transactions"
    },
    "cluster_id": "lkc-mv0817",
    "topic_name": "transactions",
    "is_internal": false,
    "replication_factor": 3,
    "partitions_count": 0,
    "partitions": {
      "related": "https://pkc-6ojv2.us-west4.gcp.confluent.cloud/kafka/v3/clusters/lkc-127p73/topics/transactions/partitions"
    },
    "configs": {
      "related": "https://pkc-6ojv2.us-west4.gcp.confluent.cloud/kafka/v3/clusters/lkc-127p73/topics/transactions/configs"
    },
    "partition_reassignments": {
      "related": "https://pkc-6ojv2.us-west4.gcp.confluent.cloud/kafka/v3/clusters/lkc-127p73/topics/transactions/partitions/-/reassignment"
    },
    "authorized_operations": []
  }  
  ```
</details>

#### Partition throughput - Identify hot partition

```
curl --request POST \
--url 'https://api.telemetry.confluent.cloud/v2/metrics/cloud/query' \
--header 'Authorization: Basic '$CLOUD_AUTH64'' \
--header 'content-type: application/json' \
--data '{
  "aggregations": [
    {
      "metric": "io.confluent.kafka.server/sent_bytes",
      "op": "SUM"
    }
  ],
  "filter": {
    "op": "AND",
    "filters": [
      {
        "field": "resource.kafka.id",
        "op": "EQ",
        "value": "lkc-p96zk2"
      },
      {
        "field": "metric.topic",
        "op": "EQ",
        "value": "linked-topic"
      },
      {
        "field": "metric.partition",
        "op": "EQ",
        "value": "0"
      }
    ]
  },
  "granularity": "PT1M",
  "group_by": ["metric.topic", "metric.partition"],
  "intervals": ["2024-05-06T11:00:00-00:00/2024-05-06T16:36:00-00:00"]
}'
```
<details>
  <summary>Output</summary>
  
```js 

{
  "data": [
    {
      "timestamp": "2024-05-06T16:31:00Z",
      "value": 3055,
      "metric.topic": "linked-topic",
      "metric.partition": "0"
    },
    {
      "timestamp": "2024-05-06T16:32:00Z",
      "value": 0,
      "metric.topic": "linked-topic",
      "metric.partition": "0"
    },
    {
      "timestamp": "2024-05-06T16:33:00Z",
      "value": 315,
      "metric.topic": "linked-topic",
      "metric.partition": "0"
    },
    {
      "timestamp": "2024-05-06T16:34:00Z",
      "value": 0,
      "metric.topic": "linked-topic",
      "metric.partition": "0"
    },
    {
      "timestamp": "2024-05-06T16:35:00Z",
      "value": 0,
      "metric.topic": "linked-topic",
      "metric.partition": "0"
    }
  ]
}
```
</details>


