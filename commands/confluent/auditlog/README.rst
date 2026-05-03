Cluster Link Audit logs with a longer retention period
======================================================

Guide to setup a cluster link to replicate audit log to your cluster with a longer retention period ( > 7 days ).

===================================
Source Cluster - Audit Log Cluster
===================================


Connect to the Audit log cluster and capture the cluster parameters
::

  confluent audit-log describe
  +-----------------+----------------------------+
  | Cluster         | lkc-0kqvp                  |
  | Environment     | env-q5yy6                  |
  | Service Account | sa-4jgq7w                  |
  | Topic Name      | confluent-audit-log-events |
  +-----------------+----------------------------+

  confluent environment use env-q5yy6

  confluent kafka cluster use lkc-0kqvp

  confluent kafka cluster describe lkc-0kqvp
  +---------------+---------------------------------------------------------+
  | ID            | lkc-0kqvp                                               |
  | Name          | _confluent_audit_log_cluster                            |
  | Type          | STANDARD                                                |
  | Ingress       |                                                     250 |
  | Egress        |                                                     750 |
  | Storage       | Infinite                                                |
  | Provider      | aws                                                     |
  | Availability  | single-zone                                             |
  | Region        | us-west-2                                               |
  | Status        | UP                                                      |
  | Endpoint      | SASL_SSL://pkc-4ywp7.us-west-2.aws.confluent.cloud:9092 |
  | REST Endpoint | https://pkc-4ywp7.us-west-2.aws.confluent.cloud:443     |
  +---------------+---------------------------------------------------------+ 

==========================================
Source Cluster - Create a API Key & Secret
==========================================
Setup a API Key & Secret and verify by consuming from the source Audit logs
::
 
  confluent api-key create --service-account sa-4jgq7w --resource lkc-0kqvp
  +---------+------------------------------------------------------------------+
  | API Key | TL7EDTV3XXXXXXXX                                                 |
  | Secret  | kq/cZw1NfIeYJ/JaqVMZPYiSMv9ZEIui6iVP+nQo1RvIAEkt+XXXXXXXXXXXXXXX |
  +---------+------------------------------------------------------------------+

  confluent api-key use TL7EDTV3MCWEWUYV --resource lkc-0kqvp

  confluent kafka topic consume --from-beginning confluent-audit-log-events | head -1


========================================================
Destination Cluster - Dedicated Confluent Cloud Cluster
========================================================

Connect to dedicated cluster

::

  confluent env use env-z3y7v3

  confluent kafka cluster list
       Id      |      Name       |   Type    | Provider |  Region   | Availability | Status
  ---------------+-----------------+-----------+----------+-----------+--------------+---------
    lkc-1w9gn5 | srini-basic     | BASIC     | aws      | us-east-2 | single-zone  | UP
  * lkc-jv9ndm | srini-dedicated | DEDICATED | aws      | us-east-2 | single-zone  | UP

  confluent kafka cluster use lkc-jv9ndm


===========================================
Destination Cluster - Create a cluster link
===========================================

Create a cluster link with custom topic.config.sync.include, Refer to cl.config

::

  confluent kafka link create srini-auditlog-ded --cluster lkc-jv9ndm  \
  --source-cluster-id lkc-0kqvp --source-bootstrap-server "SASL_SSL://pkc-4ywp7.us-west-2.aws.confluent.cloud:9092"  \
  --source-api-key TL7EDTV3XXXXXXXX --source-api-secret kq/cZw1NfIeYJ/JaqVMZPYiSMv9ZEIui6iVP+nQo1RvIAEkt+XXXXXXX  \
  --config-file cl.config

Confirm retention.bytes is not synced

::

  confluent kafka link describe srini-auditlog-ded | grep topic.config.sync.include
  topic.config.sync.include                   | min.compaction.lag.ms,max.compaction.lag.ms,message.timestamp.type,message.timestamp.difference.max.ms,cleanup.policy,max.message.bytes | false     | false     | DYNAMIC_CLUSTER_LINK_CONFIG | []


===========================================
Destination Cluster - Create a mirror topic
===========================================

Create a mirror topic with longer retention period, Refer to mirror.config

::

  confluent kafka mirror create confluent-audit-log-events --link srini-auditlog-ded --cluster lkc-jv9ndm --config-file mirror.config

Validate the mirrored topic has a longer retention period, as per your customization in mirror.config

::

  confluent kafka topic describe confluent-audit-log-events  | egrep "retention"
  retention.bytes                         |                                                       -1
  retention.ms                            |                                               7776000000
