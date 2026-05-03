## Contents
- [Uni directional ClusterLink](#Uni-directional-ClusterLink)
- [Bi directional ClusterLink](#Bi-directional-ClusterLink)
  
## Uni directional ClusterLink
### confluent cluster link management
#### List cluster links
```
confluent kafka link list --cluster lkc-3w6270 --environment env-kgwrwm
    Link Name   | Source Cluster Id  
----------------+--------------------
  easttowest-cl | lkc-p96zk2         
```

#### Describe Cluster link
```
confluent kafka link describe easttowest-cl --cluster lkc-3w6270 --environment env-kgwrwm
                  Config Name                 |                                                                                       Config Value                                                                                       | Read Only | Sensitive |           Source            | Synonyms  
----------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------+-----------+-----------------------------+-----------
  dest.cluster.id                             | lkc-3w6270                                                                                                                                                                               | true      | true      |                             | []        
  acl.filters                                 |                                                                                                                                                                                          | false     | false     | DEFAULT_CONFIG              | []        
  acl.sync.enable                             | false                                                                                                                                                                                    | false     | false     | DEFAULT_CONFIG              | []        
  acl.sync.ms                                 |                                                                                                                                                                                     5000 | false     | false     | DEFAULT_CONFIG              | []        
  auto.create.mirror.topics.enable            | false                                                                                                                                                                                    | false     | false     | DEFAULT_CONFIG              | []        
  auto.create.mirror.topics.filters           |                                                                                                                                                                                          | false     | false     | DEFAULT_CONFIG              | []        
  bootstrap.servers                           | SASL_SSL://pkc-6583q.eastus2.azure.confluent.cloud:9092                                                                                                                                  | false     | false     | DYNAMIC_CLUSTER_LINK_CONFIG | []        
  client.dns.lookup                           | use_all_dns_ips
. . .
```

#### List Mirror Topics
```
confluent kafka mirror list --link easttowest-cl --cluster lkc-3w6270 --environment env-kgwrwm
  Link Name | Mirror Topic Name | Num Partition | Max Per Partition Mirror Lag | Source Topic Name | Mirror Status | Status Time Ms  
------------+-------------------+---------------+------------------------------+-------------------+---------------+-----------------
```

#### List cluster link task status
```
> confluent kafka link task list bd-link
      Task Name      |     State      | Errors  
---------------------+----------------+---------
  AclSync            | NOT_CONFIGURED |         
  AutoCreateMirror   | NOT_CONFIGURED |         
  ConsumerOffsetSync | NOT_CONFIGURED |         
  TopicConfigsSync   | ACTIVE         | 
  ```
## Bi directional ClusterLink
Cluster Linking bidirectional mode (a bidirectional cluster link) enables better Disaster Recovery and active/active architectures, with data and metadata flowing bidirectionally between two or more clusters.
### Create link in secondary
> Add the following to the config for auto creation of mirror topics and sync offsets & acl
```
auto.create.mirror.topics.filters={"topicFilters":[{"name": "some_topic_name","patternType": "PREFIXED","filterType": "INCLUDE"}]}
auto.create.mirror.topics.enable=true
consumer.offset.sync.enable=true
acl.sync.enable=true
```
```
> confluent kafka cluster list
  Current |     ID     |   Name    |   Type    | Provider | Region  | Availability | Network | Status  
----------+------------+-----------+-----------+----------+---------+--------------+---------+---------
  *       | lkc-3w6270 | secondary | DEDICATED | azure    | westus3 | multi-zone   |         | UP      
          | lkc-p96zk2 | primary   | DEDICATED | azure    | eastus2 | multi-zone   |         | UP  

> confluent kafka link create bd-link --remote-cluster lkc-p96zk2 --cluster lkc-3w6270 --remote-api-key WNSDXXXXXXXXSPIL --remote-api-secret Jjh3ZF9kXXXXXXXXLIVSPY --remote-bootstrap-server SASL_SSL://pkc-6583q.eastus2.azure.confluent.cloud:9092 --local-api-key DJSPXXXXXXA376V --local-api-secret WA/imJQlfTc94C0kGMX2XXXXXXXXXXXME94cnN --config-file bd-link-secondary.config
Created cluster link "bd-link" with configs:
"bootstrap.servers"="SASL_SSL://pkc-6583q.eastus2.azure.confluent.cloud:9092"
"link.mode"="BIDIRECTIONAL"
"local.sasl.mechanism"="PLAIN"
"local.security.protocol"="SASL_SSL"
"sasl.mechanism"="PLAIN"
"security.protocol"="SASL_SSL"

> confluent kafka link list
   Name   | Source Cluster | Destination Cluster | Remote Cluster | State  | Error | Error Message  
----------+----------------+---------------------+----------------+--------+-------+----------------
  bd-link |                |                     | lkc-p96zk2     | ACTIVE |       | 
```
### Create link in primary
```
> confluent kafka cluster list
  Current |     ID     |   Name    |   Type    | Provider | Region  | Availability | Network | Status  
----------+------------+-----------+-----------+----------+---------+--------------+---------+---------
          | lkc-3w6270 | secondary | DEDICATED | azure    | westus3 | multi-zone   |         | UP      
  *       | lkc-p96zk2 | primary   | DEDICATED | azure    | eastus2 | multi-zone   |         | UP  

> confluent kafka link create bd-link --remote-cluster lkc-3w6270 --cluster lkc-p96zk2 --remote-api-key DJSPXXXXX376V  --remote-api-secret WA/imJQlfTc94XXXXXXXME94cnN  --remote-bootstrap-server SASL_SSL://pkc-ryzn9.westus3.azure.confluent.cloud:9092 --local-api-key WNSDXXXXXXPIL --local-api-secret Jjh3ZF9kAXXXXXXXXLIVSPY --config-file bd-link-primary.config
Created cluster link "bd-link" with configs:
"bootstrap.servers"="SASL_SSL://pkc-ryzn9.westus3.azure.confluent.cloud:9092"
"link.mode"="BIDIRECTIONAL"
"local.sasl.mechanism"="PLAIN"
"local.security.protocol"="SASL_SSL"
"sasl.mechanism"="PLAIN"
"security.protocol"="SASL_SSL"

[ubuntu@awst2x ~/clusterlink/bidirectional]# confluent kafka link list
   Name   | Source Cluster | Destination Cluster | Remote Cluster | State  | Error | Error Message  
----------+----------------+---------------------+----------------+--------+-------+----------------
  bd-link |                |                     | lkc-3w6270     | ACTIVE |       |                
```

### Create topic in primary and mirror in secondary and vice-versa
```
> confluent kafka topic create bd-primary-topic  --cluster lkc-p96zk2
Created topic "bd-primary-topic".
> confluent kafka mirror create bd-primary-topic --link bd-link --cluster lkc-3w6270
Created mirror topic "bd-primary-topic".

> confluent kafka topic create bd-secondary-topic  --cluster lkc-3w6270
Created topic "bd-secondary-topic".
> confluent kafka mirror create bd-secondary-topic --link bd-link --cluster lkc-p96zk2
Created mirror topic "bd-secondary-topic".
```

### produce to both sites
```
> kafka-console-producer --bootstrap-server pkc-6583q.eastus2.azure.confluent.cloud:9092 --topic bd-primary-topic --producer.config primary.config
>{"name": "primary", "price": 15.00, "quantity": 3}
^C
> kafka-console-producer --bootstrap-server pkc-ryzn9.westus3.azure.confluent.cloud:9092 --topic bd-secondary-topic --producer.config secondary.config
>{"name": "secondary", "price": 15.00, "quantity": 3}
^C
```

### fetch from both sites
```
> kafka-console-consumer --bootstrap-server pkc-ryzn9.westus3.azure.confluent.cloud:9092 --topic bd-primary-topic --consumer.config secondary.config --from-beginning
{"name": "primary", "price": 15.00, "quantity": 3}
^C[2024-03-27 03:57:57,314] ERROR [Consumer clientId=console-consumer, groupId=console-consumer-65868] Unable to find FetchSessionHandler for node 2. Ignoring fetch response. (org.apache.kafka.clients.consumer.internals.AbstractFetch)
Processed a total of 1 messages

> kafka-console-consumer --bootstrap-server pkc-6583q.eastus2.azure.confluent.cloud:9092 --topic bd-secondary-topic --consumer.config primary.config --from-beginning
{"name": "secondary", "price": 15.00, "quantity": 3}
```

## Reverse the Source & Mirror Topic
The source topic -> mirror topic relationship can be reversed using the reverse-and-start or reverse-and-pause commands. 
These cause the source topic to become the mirror topic, and the mirror topic to become the source topic.
```
!!! Run the commands on the destination cluster !!!
> confluent kafka cluster list
  Current |     ID     |   Name    |   Type    | Provider | Region  | Availability | Network | Status
----------+------------+-----------+-----------+----------+---------+--------------+---------+---------
  *       | lkc-3w6270 | secondary | DEDICATED | azure    | westus3 | multi-zone   |         | UP
          | lkc-p96zk2 | primary   | DEDICATED | azure    | eastus2 | multi-zone   |         | UP

> confluent kafka mirror reverse-and-start bd-primary-topic --link bd-link
  Mirror Topic Name | Partition | Partition Mirror Lag | Last Source Fetch Offset | Error Message | Error Code
--------------------+-----------+----------------------+--------------------------+---------------+-------------
  bd-primary-topic  |         0 |                    0 |                       -1 |               |
  bd-primary-topic  |         1 |                    0 |                       -1 |               |
  bd-primary-topic  |         2 |                    0 |                       -1 |               |
  bd-primary-topic  |         3 |                    0 |                       -1 |               |
  bd-primary-topic  |         4 |                    0 |                       -1 |               |
  bd-primary-topic  |         5 |                    0 |                        1 |               |
```
## Link Administration
Reference: https://docs.confluent.io/cloud/current/multi-cloud/cluster-linking/cluster-links-cc.html#advanced-options-for-bidirectional-cluster-linking

### View a cluster link task status
```
> confluent kafka link task list  bd-link
      Task Name      |     State      | Errors  
---------------------+----------------+---------
  AclSync            | NOT_CONFIGURED |         
  AutoCreateMirror   | NOT_CONFIGURED |         
  ConsumerOffsetSync | NOT_CONFIGURED |         
  TopicConfigsSync   | ACTIVE         | 
```
