# Disaster Recovery Management Tools


## Disaster Recovery Manager
A tool to execute during failover/failback that handles promoting topics, deleting cluster link, create cluster link in reverse etc.
Imports clusterlink_mgr.py and mirror_topic_mgr.py libraries

```
usage: dr_mgr.py [-h] -o {status,failover,failback,prep_failover,prep_failback} [-t {force,validate_only}]

options:
  -o {status,failover,failback,prep_failover,prep_failback}
                        Operation e.g failover, failback or prepare for failover/failback
  -t {force,validate_only}
                        Use validate_only and verify before a force failover/failback
```

### DR Life Cycle

#### Stable State
```
> dr_mgr.py -o status

--------CLUSTER:lkc-p96zk2 (PRIMARY) --------   |   -------CLUSTER:lkc-3w6270 (SECONDARY) -------
---------------------------------------------   |   -----------LINK:cl-test-ps (ACTIVE)----------
-----------------SOURCE TOPIC----------------   |   ---------MIRROR TOPIC--------- -P#- --STATUS-
source_topic2                                  ==>> source_topic2                     1    ACTIVE
source_topic                                   ==>> source_topic                      1    ACTIVE
```

#### Failover to DR site
```
./dr_mgr.py -o failover -t force

!!!!!!!!!! This operation FAILOVER can break the data pipeline !!!!!!!
Do you want to continue (y/n): y
======== FAILOVER -VALIDATE CLUSTER LINK
{
  "kind": "KafkaLinkDataList",
  "metadata": {
    "self": "https://pkc-ryzn9.westus3.azure.confluent.cloud/kafka/v3/clusters/lkc-3w6270/links",
    "next": null
  },
  "data": [
    {
      "kind": "KafkaLinkData",
      "metadata": {
        "self": "https://pkc-ryzn9.westus3.azure.confluent.cloud/kafka/v3/clusters/lkc-3w6270/links/cl-test-ps"
      },
      "source_cluster_id": "lkc-p96zk2",
      "destination_cluster_id": null,
      "remote_cluster_id": "lkc-p96zk2",
      "link_name": "cl-test-ps",
      "link_id": "a66e98f2-a403-4b54-bc3f-04227fdc3660",
      "cluster_link_id": "pm6Y8qQDS1S8PwQif9w2YA",
      "topic_names": [
        "source_topic2",
        "source_topic"
      ],
      "link_error": "NO_ERROR",
      "link_error_message": "",
      "link_state": "ACTIVE"
    }
  ]
}
Total ClusterLinks :1 Active ClusterLInks :1
======== FAILOVER - MIRROR TOPICS
Promoting the following mirror topics : ['source_topic2', 'source_topic']
{
  "kind": "KafkaAlterMirrorsDataList",
  "metadata": {
    "self": "https://pkc-ryzn9.westus3.azure.confluent.cloud/kafka/v3/clusters/lkc-3w6270/links/cl-test-ps/mirrors",
    "next": null
  },
  "data": [
    {
      "kind": "AlterMirrorsData",
      "metadata": {
        "self": "https://pkc-ryzn9.westus3.azure.confluent.cloud/kafka/v3/clusters/lkc-3w6270/links/cl-test-ps/mirrors/source_topic"
      },
      "mirror_topic_name": "source_topic",
      "error_code": null,
      "error_message": null,
      "mirror_lags": [
        {
          "partition": 0,
          "lag": 0,
          "last_source_fetch_offset": -1
        }
      ]
    },
    {
      "kind": "AlterMirrorsData",
      "metadata": {
        "self": "https://pkc-ryzn9.westus3.azure.confluent.cloud/kafka/v3/clusters/lkc-3w6270/links/cl-test-ps/mirrors/source_topic2"
      },
      "mirror_topic_name": "source_topic2",
      "error_code": null,
      "error_message": null,
      "mirror_lags": [
        {
          "partition": 0,
          "lag": 0,
          "last_source_fetch_offset": -1
        }
      ]
    }
  ]
}
======== FAILOVER -INSERT A EVENT IN TRAFFIC-ROUTER TOPIC TO TRIGGER A SWITCH TO SECONDARY SITE
% Waiting for 1 deliveries
% Message delivered to primary traffic-router [0] @ 115, value: b'{"EVENT": "switch site", "LAG": "N/A", "SITE": "secondary" }', timestamp: (1, 1705440334641)
``` 

#### Post Failover State : Mirroring is Stopped
```
./dr_mgr.py -o status

--------CLUSTER:lkc-p96zk2 (PRIMARY) --------   |   -------CLUSTER:lkc-3w6270 (SECONDARY) -------
---------------------------------------------   |   -----------LINK:cl-test-ps (ACTIVE)----------
-----------------SOURCE TOPIC----------------   |   ---------MIRROR TOPIC--------- -P#- --STATUS-
linked-topic                                   ==>> linked-topic                      3   STOPPED
source_topic                                   ==>> source_topic                      1   STOPPED
```

#### Prepare for Failback to Primary Site
```
./dr_mgr.py -o prep_failback -t force

!!!!!!!!!! This operation PREP_FAILBACK can break the data pipeline !!!!!!!
Do you want to continue (y/n): y
======== PREP_FAILBACK -IDENTIFY MIRROR TOPICS
Total Topics :2 Active Topics :0
======== PREP_FAILBACK -DELETING TOPICS IN PRIMARY
HTTP:404{"error_code":404,"message":"The cluster link doesn't exist: "}
SUCCESS : Deleted Topic source_topic
HTTP:404{"error_code":404,"message":"The cluster link doesn't exist: "}
SUCCESS : Deleted Topic source_topic2
Sleeping 15s to allow the topic deletions to complete, before cluster link creation
======== PREP_FAILBACK -CREATING CLUSTERLINK cl-test-ps IN PRIMARY
SUCCESS: Cluster Link: cl-test-ps created
======== PREP_FAILBACK -DELETING CLUSTERLINK cl-test-ps IN SECONDARY
SUCCESS: Deleted the Cluster link cl-test-ps in secondary site
```

#### Ready to failback State : Mirroring is enabled Secondary -> Primary
```
./dr_mgr.py -o status

--------CLUSTER:lkc-p96zk2 (PRIMARY) --------   |   -------CLUSTER:lkc-3w6270 (SECONDARY) -------
-----------LINK:cl-test-ps (ACTIVE)----------   |   ---------------------------------------------
---------MIRROR TOPIC--------- -P#- --STATUS-   |   -----------------SOURCE TOPIC----------------
source_topic                      1    ACTIVE  <<== source_topic
source_topic2                     1    ACTIVE  <<== source_topic2
```
> Note: After prep_failover / prep_failback step, it will take ~5m for the mirroring to show up. Wait for the topics to show up before you run failover/failback.

#### Failback to Primary Site
```
./dr_mgr.py -o failback -t force

!!!!!!!!!! This operation FAILBACK can break the data pipeline !!!!!!!
Do you want to continue (y/n): y
======== FAILBACK -VALIDATE CLUSTER LINK
{
  "kind": "KafkaLinkDataList",
  "metadata": {
    "self": "https://pkc-6583q.eastus2.azure.confluent.cloud/kafka/v3/clusters/lkc-p96zk2/links",
    "next": null
  },
  "data": [
    {
      "kind": "KafkaLinkData",
      "metadata": {
        "self": "https://pkc-6583q.eastus2.azure.confluent.cloud/kafka/v3/clusters/lkc-p96zk2/links/cl-test-ps"
      },
      "source_cluster_id": "lkc-3w6270",
      "destination_cluster_id": null,
      "remote_cluster_id": "lkc-3w6270",
      "link_name": "cl-test-ps",
      "link_id": "2a57d13f-cf96-4f84-a544-1a99207ac7ff",
      "cluster_link_id": "KlfRP8-WT4SlRBqZIHrH_w",
      "topic_names": [
        "source_topic",
        "source_topic2"
      ],
      "link_error": "NO_ERROR",
      "link_error_message": "",
      "link_state": "ACTIVE"
    }
  ]
}
Total ClusterLinks :1 Active ClusterLInks :1
======== FAILBACK -FAILOVER / PROMOTE
Promoting the following mirror topics : ['source_topic', 'source_topic2']
{
  "kind": "KafkaAlterMirrorsDataList",
  "metadata": {
    "self": "https://pkc-6583q.eastus2.azure.confluent.cloud/kafka/v3/clusters/lkc-p96zk2/links/cl-test-ps/mirrors",
    "next": null
  },
  "data": [
    {
      "kind": "AlterMirrorsData",
      "metadata": {
        "self": "https://pkc-6583q.eastus2.azure.confluent.cloud/kafka/v3/clusters/lkc-p96zk2/links/cl-test-ps/mirrors/source_topic"
      },
      "mirror_topic_name": "source_topic",
      "error_code": null,
      "error_message": null,
      "mirror_lags": [
        {
          "partition": 0,
          "lag": 0,
          "last_source_fetch_offset": -1
        }
      ]
    },
    {
      "kind": "AlterMirrorsData",
      "metadata": {
        "self": "https://pkc-6583q.eastus2.azure.confluent.cloud/kafka/v3/clusters/lkc-p96zk2/links/cl-test-ps/mirrors/source_topic2"
      },
      "mirror_topic_name": "source_topic2",
      "error_code": null,
      "error_message": null,
      "mirror_lags": [
        {
          "partition": 0,
          "lag": 0,
          "last_source_fetch_offset": -1
        }
      ]
    }
  ]
}
======== FAILBACK -INSERT A EVENT IN TRAFFIC-ROUTER TOPIC TO TRIGGER A SWITCH TO PRIMARY SITE
% Waiting for 1 deliveries
% Message delivered to secondary traffic-router [0] @ 116, value: b'{"EVENT": "switch site", "LAG": "N/A", "SITE": "primary" }', timestamp: (1, 1705441367547)
```

#### Post Failback State : Mirroring is Stopped
```
./dr_mgr.py -o status

--------CLUSTER:lkc-p96zk2 (PRIMARY) --------   |   -------CLUSTER:lkc-3w6270 (SECONDARY) -------
-----------LINK:cl-test-ps (ACTIVE)----------   |   ---------------------------------------------
---------MIRROR TOPIC--------- -P#- --STATUS-   |   -----------------SOURCE TOPIC----------------
linked-topic                      3   STOPPED  <<== linked-topic
source_topic                      1   STOPPED  <<== source_topic
```

#### Prepare for Failover to DR site
```
./dr_mgr.py -o prep_failover -t force

!!!!!!!!!! This operation PREP_FAILOVER can break the data pipeline !!!!!!!
Do you want to continue (y/n): y
			       ======== PREP_FAILOVER -IDENTIFY MIRROR TOPICS
Total Topics :2 Active Topics :0
======== PREP_FAILOVER -DELETING TOPICS IN SECONDARY
HTTP:404{"error_code":404,"message":"The cluster link doesn't exist: "}
SUCCESS : Deleted Topic source_topic
HTTP:404{"error_code":404,"message":"The cluster link doesn't exist: "}
SUCCESS : Deleted Topic source_topic2
Sleeping 15s to allow the topic deletions to complete, before cluster link creation
======== PREP_FAILOVER -CREATING CLUSTERLINK cl-test-ps IN SECONDARY
SUCCESS: Cluster Link: cl-test-ps created
======== PREP_FAILOVER -DELETING CLUSTERLINK cl-test-ps IN PRIMARY
SUCCESS: Deleted the Cluster link cl-test-ps in secondary site
```

#### Ready to failover State : Mirroring is enabled Primary -> Secondary
```
./dr_mgr.py -o status

--------CLUSTER:lkc-p96zk2 (PRIMARY) --------   |   -------CLUSTER:lkc-3w6270 (SECONDARY) -------
---------------------------------------------   |   -----------LINK:cl-test-ps (ACTIVE)----------
-----------------SOURCE TOPIC----------------   |   ---------MIRROR TOPIC--------- -P#- --STATUS-
source_topic2                                  ==>> source_topic2                     1    ACTIVE
source_topic                                   ==>> source_topic                      1    ACTIVE
```
> Note: After prep_failover / prep_failback step, it will take ~5m for the mirroring to show up. Wait for the topics to show up before you run failover/failback.
>

## Mirror Topic Manager
A comprehensive tool to do all things mirror topics e.g create,describe,list,lag,promote,failover,pause,resume,delete
Configuration is provided in mirror_topic_mgr_config.json, can be overridden with command line parms

```
usage: mirror_topic_mgr.py [-h] [-u REST_URL] [-k CLUSTER_API_KEY] [-s CLUSTER_API_SECRET] [-c CLUSTER_ID] [-l LINK_ID] 
                           -o {create,describe,list,lag,promote,failover,pause,resume,delete}
                           [-m {active,failed,paused,stopped,pending_stopped}] [-t TOPIC]
```

### Example
```
> ./mirror_topic_mgr.py -o list

{
  "kind": "KafkaMirrorDataList",
  "metadata": {
    "self": "https://pkc-ryzn9.westus3.azure.confluent.cloud/kafka/v3/clusters/lkc-3w6270/links/primary_secondary_link/mirrors",
    "next": null
  },
  "data": [
    {
      "kind": "KafkaMirrorData",
      "metadata": {
        "self": "https://pkc-ryzn9.westus3.azure.confluent.cloud/kafka/v3/clusters/lkc-3w6270/links/primary_secondary_link/mirrors/common-topic"
      },
      "link_name": "primary_secondary_link",
      "mirror_topic_name": "common-topic",
      "source_topic_name": "common-topic",
      "num_partitions": 1,
      "mirror_lags": [
        {
          "partition": 0,
          "lag": 0,
          "last_source_fetch_offset": 4
        }
      ],
      "mirror_status": "STOPPED",
      "mirror_topic_error": "NO_ERROR",
      "state_time_ms": 1702536103993
    },
    {
      "kind": "KafkaMirrorData",
      "metadata": {
        "self": "https://pkc-ryzn9.westus3.azure.confluent.cloud/kafka/v3/clusters/lkc-3w6270/links/primary_secondary_link/mirrors/part2-topic"
      },
      "link_name": "primary_secondary_link",
      "mirror_topic_name": "part2-topic",
      "source_topic_name": "part2-topic",
      "num_partitions": 2,
      "mirror_lags": [
        {
          "partition": 1,
          "lag": 0,
          "last_source_fetch_offset": 0
        },
        {
          "partition": 0,
          "lag": 0,
          "last_source_fetch_offset": -1
        }
      ],
      "mirror_status": "ACTIVE",
      "mirror_topic_error": "NO_ERROR",
      "state_time_ms": 1703285083428
    }
  ]
}

```

## Cluster Link Manager
A comprehensive tool to do all things cluster link e.g create,describe,list,lag,promote,failover,pause,resume,delete
Configuration is provided in mirror_topic_mgr_config.json

```
usage: clusterlink_mgr.py [-h] [-u REST_URL] [-k CLUSTER_API_KEY] [-s CLUSTER_API_SECRET] [-c CLUSTER_ID] [-l LINK_ID] [-g SOURCE_CLUSTER_ID] [-x SOURCE_API_KEY] [-i SOURCE_API_SECRET] [-b SOURCE_BOOTSTRAP_SERVER] -o
                          {create,describe,list,delete} [-d {force,validate_only}]
```

### Example
```
> ./clusterlink_mgr.py -o list

{
  "kind": "KafkaLinkDataList",
  "metadata": {
    "self": "https://pkc-ryzn9.westus3.azure.confluent.cloud/kafka/v3/clusters/lkc-3w6270/links",
    "next": null
  },
  "data": [
    {
      "kind": "KafkaLinkData",
      "metadata": {
        "self": "https://pkc-ryzn9.westus3.azure.confluent.cloud/kafka/v3/clusters/lkc-3w6270/links/cl-test-ps"
      },
      "source_cluster_id": "lkc-p96zk2",
      "destination_cluster_id": null,
      "remote_cluster_id": "lkc-p96zk2",
      "link_name": "cl-test-ps",
      "link_id": "66f747f2-801e-4afb-894e-1a4c80fdd42d",
      "cluster_link_id": "ZvdH8oAeSvuJThpMgP3ULQ",
      "topic_names": [
        "source_topic2",
        "source_topic"
      ],
      "link_error": "NO_ERROR",
      "link_error_message": "",
      "link_state": "ACTIVE"
    }
  ]
}
```
