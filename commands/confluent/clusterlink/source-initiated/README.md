## Source Initiated Cluster Link

Motiviation: 
1. Customers who have private-linked Cloud clusters - Privately linked CC doesnt allow connections from a CC that is on public internet.
2. on-prem CP behind firewall - Customers do not want to open on-prem clusters to enable clients from cloud to establish connections to on-prem that is behind a firewall. This is particularly significant when Cloud brokers don’t have stable IPs, making it hard to set up firewalls that restrict connections originating from specific host IPs. Even though this restriction is being addressed in  https://confluentinc.atlassian.net/wiki/spaces/~778906221/blog/2020/09/02/1547960632/Stable+Public+Internet+IP+Execution+Plan, customers may still be unwilling to open up on-prem clusters.

Source initiated cluster link has two halves, one that is created on source side and other that is created on destination side. Both should be created with the same cluster link name.

### Environment where the cluster link is being created
```
> confluent env list  
  Current |     ID     |       Name       | Stream Governance Package
----------+------------+------------------+----------------------------
  *       | env-6wqqo2 | CCell            | ESSENTIALS
```

### Private & Public clusters being linked
> confluent kafka cluster list
  Current |     ID     |   Name    |   Type    | Provider |  Region   | Availability | Network  | Status
----------+------------+-----------+-----------+----------+-----------+--------------+----------+---------
  *       | lkc-d8pqjd | inventory | DEDICATED | azure    | centralus | multi-zone   | n-1lp8l4 | UP
          | lkc-w60k9j | public    | DEDICATED | azure    | centralus | multi-zone   |          | UP

### Create two Service Account for Cluster Linking
```
> confluent iam service-account create sa-cl-src  --description "source initiated outbound link"
+-------------+--------------------------------------+
| ID          | sa-31y700                            |
| Name        | sa-cl-src                            |
| Description | source initiated outbound link       |
+-------------+--------------------------------------+
>  confluent iam service-account create sa-cl-dst  --description "source initiated inbound link"
+-------------+--------------------------------------+
| ID          | sa-og0kyj                            |
| Name        | sa-cl-dst                            |
| Description | source initiated inbound link        |
+-------------+--------------------------------------+
```
### Create RBAC CloudClusterAdmin for the above service accounts
```
> confluent iam rbac role-binding create --role CloudClusterAdmin --principal User:sa-31y700 --environment env-6wqqo2 --cloud-cluster lkc-d8pqjd
+-----------+-------------------+
| ID        | rb-ZXeD0y         |
| Principal | User:sa-31y700    |
| Role      | CloudClusterAdmin |
+-----------+-------------------+

> confluent iam rbac role-binding create --role CloudClusterAdmin --principal User:sa-og0kyj --environment env-6wqqo2 --cloud-cluster lkc-w60k9j
+-----------+-------------------+
| ID        | rb-9P1g8k         |
| Principal | User:sa-og0kyj    |
| Role      | CloudClusterAdmin |
+-----------+-------------------+
```
### Create API Keys for each service accounrt
```
> confluent api-key create --resource lkc-d8pqjd  --service-account  sa-31y700 --description "source initiated outbound key"
Save the API key and secret. The secret is not retrievable later.
+------------+------------------------------------------------------------------+
| API Key    | LZXXXXXXXXXXXSAZ                                                 |
| API Secret | JPa7WDTlznCiaP7aXXXXXXXXXXXXXXXXXXXXXXJJCj9lv3bqK+W0xpmCYFAfTodP |
+------------+------------------------------------------------------------------+
> confluent api-key create --resource lkc-w60k9j  --service-account  sa-og0kyj  --description "source initiated inbound key"
It may take a couple of minutes for the API key to be ready.
Save the API key and secret. The secret is not retrievable later.
+------------+------------------------------------------------------------------+
| API Key    | KT5CXXXXXXXXX4RV                                                 |
| API Secret | QW04U00pXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXTDy15wPtQU5s/r9 |
+------------+------------------------------------------------------------------+
```
### Create Cluster Link
#### export env vars
```
export PVTENV=env-6wqqo2
export PVTCLUSTER=lkc-d8pqjd
export PVTBOOTSTRAP=lkc-d8pqjd.dom6pk7lzzg.centralus.azure.confluent.cloud:9092
export PUBENV=env-6wqqo2
export PUBCLUSTER=lkc-w60k9j
export PUBBOOTSTRAP=pkc-w5o6pg.centralus.azure.confluent.cloud:9092
export PUBAPIKEY=KT5CXXXXXXXXX4RV
export PUBAPISECRET=QW04U00pXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXTDy15wPtQU5s/r9 
```

#### Create the inbound cluster link on the PUBLIC cluster
```
> confluent kafka env use $PUBENV
Using environment "env-6wqqo2".

> confluent kafka cluster use $PUBCLUSTER
Set Kafka cluster "lkc-w60k9j" as the active cluster for environment "env-6wqqo2".

> confluent kafka link create pvt-pub-link --cluster $PUBCLUSTER --source-cluster $PVTCLUSTER --config inbound.cfg
Created cluster link "pvt-pub-link" with configs:
"connection.mode"="INBOUND"
"link.mode"="DESTINATION"

> confluent kafka link list --cluster $PUBCLUSTER
      Name     | Source Cluster | Destination Cluster | Remote Cluster | State  | Error | Error Message
---------------+----------------+---------------------+----------------+--------+-------+----------------
  pvt-pub-link | lkc-d8pqjd     |                     | lkc-d8pqjd     | ACTIVE |       |
```

#### Create the outbound cluster link on the PRIVATE cluster
```
> confluent environment use $PVTENV
Using environment "env-6wqqo2".

> confluent kafka cluster use $PVTCLUSTER
Set Kafka cluster "lkc-d8pqjd" as the active cluster for environment "env-6wqqo2".

> confluent kafka link create pvt-pub-link --cluster $PVTCLUSTER --destination-cluster $PUBCLUSTER --destination-bootstrap-server $PUBBOOTSTRAP --config outbound.cfg
Created cluster link "pvt-pub-link" with configs:
"bootstrap.servers"="pkc-w5o6pg.centralus.azure.confluent.cloud:9092"
"connection.mode"="OUTBOUND"
"link.mode"="SOURCE"
"local.sasl.mechanism"="PLAIN"
"local.security.protocol"="SASL_SSL"
"sasl.mechanism"="PLAIN"
"security.protocol"="SASL_SSL"

> confluent kafka link list --cluster $PVTCLUSTER
      Name     | Source Cluster | Destination Cluster | Remote Cluster | State  | Error | Error Message
---------------+----------------+---------------------+----------------+--------+-------+----------------
  pvt-pub-link |                | lkc-w60k9j          | lkc-w60k9j     | ACTIVE |       |
```
### Validate
#### Create topic in source (pvt)
```
> confluent kafka topic create cl-topic --cluster $PVTCLUSTER
Created topic "cl-topic".
```
#### Create mirror topic in destination (pub)
```
> confluent kafka mirror create cl-topic --link pvt-pub-link --cluster $PUBCLUSTER
Created mirror topic "cl-topic".
```
#### Produce events at the source cluster (pvt)
```
> kafka-console-producer --bootstrap-server lkc-d8pqjd.dom6pk7lzzg.centralus.azure.confluent.cloud:9092 --topic cl-topic --producer.config java.config
>{"name": "hat", "price": 15.00, "quantity": 3}
>{"name": "shoes", "price": 72.00, "quantity": 1}
>{"name": "jacket", "price": 250.00, "quantity": 1}
```
#### consume events at the destination cluster (pub)
```
> kafka-console-consumer --bootstrap-server pkc-w5o6pg.centralus.azure.confluent.cloud:9092 --topic cl-topic --consumer.config java.config --from-beginning
{"name": "hat", "price": 15.00, "quantity": 3}
{"name": "shoes", "price": 72.00, "quantity": 1}
{"name": "jacket", "price": 250.00, "quantity": 1}
``` 
