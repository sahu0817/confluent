# Quotas
- Service Quota
- Rate Quota
- Client Quota
- 
## Service Quota
### Scopes
- organization
- network
- environment
- kafka_cluster
- user_account
- service_account

```
> confluent service-quota list kafka_cluster --cluster lkc-3w6270
                Quota Code               |              Name                        |     Scope     | Applied Limit | Usage |             Organization             | Environment | Kafka Cluster | Network | User
-----------------------------------------+------------------------------------------+---------------+---------------+-------+--------------------------------------+-------------+---------------+---------+---
  iam.max_rbac_role_bindings.per_cluster | Max RBAC role bindings per Kafka cluster | kafka_cluster |          5000 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kgwrwm  | lkc-3w6270    |         |
  kafka.max_api_keys.per_cluster         | Max API Keys Per Kafka Cluster           | kafka_cluster |          2000 | 11    | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kgwrwm  | lkc-3w6270    |         |
  kafka.max_ckus.per_cluster             | Max CKUs Per Kafka Cluster               | kafka_cluster |             4 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kgwrwm  | lkc-3w6270    |         |
  kafka.max_private_links.per_cluster    | Max Private Links Per Kafka Cluster      | kafka_cluster |            10 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kgwrwm  | lkc-3w6270    |         |
```

UserAccount Quota
```
> confluent service-quota list user_account
             Quota Code             |             Name              |    Scope     | Applied Limit | Usage |             Organization             | Environment | Kafka Cluster | Network |   User
------------------------------------+-------------------------------+--------------+---------------+-------+--------------------------------------+-------------+---------------+---------+-----------
  iam.max_cloud_api_keys.per_user   | Max Cloud API Keys Per User   | user_account |            10 | 2     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         | u-1jqq8v
  iam.max_cluster_api_keys.per_user | Max Cluster API Keys Per User | user_account |            10 | 10    | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         | u-1jqq8v
```
ServiceAccount Quota
```
> confluent service-quota list service_account
                   Quota Code                  |              Name              |      Scope      | Applied Limit | Usage |             Organization             | Environment | Kafka Cluster | Network |   User
-----------------------------------------------+--------------------------------+-----------------+---------------+-------+--------------------------------------+-------------+---------------+---------+------------
  iam.max_cloud_api_keys.per_service_account   | Max Cloud API Keys Per Service | service_account |           100 | 1     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         | sa-wy876j
                                               | Account                        |                 |               |       |                                      |             |               |         |
  iam.max_cluster_api_keys.per_service_account | Max Cluster API Keys Per       | service_account |           100 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         | sa-0kw3pq
                                               | Service Account                |                 |               |       |                                      |             |
```
Network Quota
```
confluent service-quota list network
                  Quota Code                 |              Name              |  Scope  | Applied Limit | Usage |             Organization             | Environment | Kafka Cluster | Network  | User
---------------------------------------------+--------------------------------+---------+---------------+-------+--------------------------------------+-------------+---------------+----------+-------
  networking.max_peering.per_network         | Max peering per network        | network |            25 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-381qyj  |               | n-gjex1n |
  networking.max_peering.per_network         | Max peering per network        | network |            25 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-381qyj  |               | n-gokvmk |
  networking.max_peering.per_network         | Max peering per network        | network |            25 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-381qyj  |               | n-p5zyqp |
  networking.max_peering.per_network         | Max peering per network        | network |            25 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-6o71w2  |               | n-61x1rq |
  networking.max_peering.per_network         | Max peering per network        | network |            25 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kg2knp  |               | n-61x84d |
  networking.max_peering.per_network         | Max peering per network        | network |            25 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kg2knp  |               | n-6x0xwj |
  networking.max_private_link.per_network    | Max private link per network   | network |            10 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-381qyj  |               | n-gokvmk |
  networking.max_private_link.per_network    | Max private link per network   | network |            10 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-6o71w2  |               | n-61x1rq |
  networking.max_private_link.per_network    | Max private link per network   | network |            10 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kg2knp  |               | n-61x84d |
  networking.max_private_link.per_network    | Max private link per network   | network |            10 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kg2knp  |               | n-6x0xwj |
  networking.max_private_link.per_network    | Max private link per network   | network |            10 | 0     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-381qyj  |               | n-gjex1n |
  networking.max_private_link.per_network    | Max private link per network   | network |            10 | 0     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-381qyj  |               | n-p5zyqp |
  networking.max_transit_gateway.per_network | Max transit gateway per        | network |             1 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-381qyj  |               | n-gjex1n |
                                             | network                        |         |               |       |                                      |             |               |          |
  networking.max_transit_gateway.per_network | Max transit gateway per        | network |             1 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-381qyj  |               | n-gokvmk |
                                             | network                        |         |               |       |                                      |             |               |          |
  networking.max_transit_gateway.per_network | Max transit gateway per        | network |             1 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-381qyj  |               | n-p5zyqp |
                                             | network                        |         |               |       |                                      |             |               |          |
  networking.max_transit_gateway.per_network | Max transit gateway per        | network |             1 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-6o71w2  |               | n-61x1rq |
                                             | network                        |         |               |       |                                      |             |               |          |
  networking.max_transit_gateway.per_network | Max transit gateway per        | network |             1 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kg2knp  |               | n-61x84d |
                                             | network                        |         |               |       |                                      |             |               |          |
  networking.max_transit_gateway.per_network | Max transit gateway per        | network |             1 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kg2knp  |               | n-6x0xwj |
                                             | network                        |         |               |       |                                      |             |               |          |
```
Organization Quota
```
confluent service-quota list organization
                    Quota Code                    |              Name              |    Scope     | Applied Limit | Usage |             Organization             | Environment | Kafka Cluster | Network | User
--------------------------------------------------+--------------------------------+--------------+---------------+-------+--------------------------------------+-------------+---------------+---------+-------
  byok.max_keys.per_org                           | Max BYOK keys per organization | organization |            20 | 7     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
  iam.max_audit_log_api_keys.per_org              | Max Audit Log API Keys Per     | organization |         10000 | 1     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
                                                  | Organization                   |              |               |       |                                      |             |               |         |
  iam.max_cloud_api_keys.per_org                  | Max Cloud API Keys Per         | organization |          1000 | 16    | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
                                                  | Organization                   |              |               |       |                                      |             |               |         |
  iam.max_environments.per_org                    | Max Environments Per           | organization |            25 | 9     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
                                                  | Organization                   |              |               |       |                                      |             |               |         |
  iam.max_group_mappings.per_org                  | Max Group Mappings Per         | organization |            12 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
                                                  | Organization                   |              |               |       |                                      |             |               |         |
  iam.max_identity_providers.per_organization     | Max identity providers per     | organization |             5 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
                                                  | organization                   |              |               |       |                                      |             |               |         |
  iam.max_jwks.per_identity_provider              | Max jwks per identity provider | organization |            15 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
  iam.max_kafka_clusters.per_org                  | Max Kafka Clusters Per         | organization |           400 | 10    | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
                                                  | Organization                   |              |               |       |                                      |             |               |         |
  iam.max_pending_invitations.per_organization    | Max pending invitations per    | organization |           150 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
                                                  | organization                   |              |               |       |                                      |             |               |         |
  iam.max_rbac_role_bindings.per_org_plus_envs    | Max RBAC role bindings at the  | organization |          1000 | 41    | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
                                                  | Organization or Environment    |              |               |       |                                      |             |               |         |
                                                  | level with Kafka access        |              |               |       |                                      |             |               |         |
  iam.max_rbac_role_bindings_all_roles.per_org    | Max RBAC Rolebindings allowed  | organization |        250000 | 107   | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
                                                  | on an individual organization  |              |               |       |                                      |             |               |         |
  iam.max_service_accounts.per_org                | Max Service Accounts Per       | organization |          1000 | 97    | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
                                                  | Organization                   |              |               |       |                                      |             |               |         |
  iam.max_users.per_org                           | Max Users Per Organization     | organization |          1000 | 14    | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
  kafka.max_kafka_creation.per_day                | Max Kafka Cluster Provisioning | organization |            20 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
                                                  | Requests Per Day               |              |               |       |                                      |             |               |         |
  notifications.max_integrations.per_organization | Maximum number of Integrations | organization |          1000 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
                                                  | per organization               |              |               |       |                                      |             |               |         |
  sd.max_pipelines.per_organization               | Max number of Stream Designer  | organization |           100 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 |             |               |         |
                                                  | pipelines per organization     |              |               |       |                                      |             |               |         |
```

Environment Quota
```
confluent service-quota list environment
                 Quota Code                |              Name              |    Scope    | Applied Limit | Usage |             Organization             | Environment | Kafka Cluster | Network | User
-------------------------------------------+--------------------------------+-------------+---------------+-------+--------------------------------------+-------------+---------------+---------+-------
  flink.max_compute_pools.per_env          | Max Flink Compute Pools Per    | environment |            10 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-1968p5  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  flink.max_compute_pools.per_env          | Max Flink Compute Pools Per    | environment |            10 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-6o659j  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  flink.max_compute_pools.per_env          | Max Flink Compute Pools Per    | environment |            10 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-dgzxwd  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  flink.max_compute_pools.per_env          | Max Flink Compute Pools Per    | environment |            10 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kgwrwm  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  flink.max_compute_pools.per_env          | Max Flink Compute Pools Per    | environment |            10 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-pkyq9o  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  flink.max_compute_pools.per_env          | Max Flink Compute Pools Per    | environment |            10 | 0     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-6o71w2  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  flink.max_compute_pools.per_env          | Max Flink Compute Pools Per    | environment |            10 | 1     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-381qyj  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  flink.max_compute_pools.per_env          | Max Flink Compute Pools Per    | environment |            10 | 1     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kg2knp  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  flink.max_compute_pools.per_env          | Max Flink Compute Pools Per    | environment |            10 | 1     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-z3y7v3  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_ckus.per_env                   | Max Kafka Cluster CKUs Per     | environment |            50 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-dgzxwd  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_ckus.per_env                   | Max Kafka Cluster CKUs Per     | environment |            50 | 0     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-381qyj  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_ckus.per_env                   | Max Kafka Cluster CKUs Per     | environment |            50 | 0     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-6o659j  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_ckus.per_env                   | Max Kafka Cluster CKUs Per     | environment |            50 | 0     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-6o71w2  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_ckus.per_env                   | Max Kafka Cluster CKUs Per     | environment |            50 | 0     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kg2knp  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_ckus.per_env                   | Max Kafka Cluster CKUs Per     | environment |            50 | 0     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-pkyq9o  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_ckus.per_env                   | Max Kafka Cluster CKUs Per     | environment |            50 | 0     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-z3y7v3  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_ckus.per_env                   | Max Kafka Cluster CKUs Per     | environment |            50 | 2     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-1968p5  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_ckus.per_env                   | Max Kafka Cluster CKUs Per     | environment |            50 | 4     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kgwrwm  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_kafka_clusters.per_env         | Max Kafka Clusters Per         | environment |            20 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-dgzxwd  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_kafka_clusters.per_env         | Max Kafka Clusters Per         | environment |            20 | 1     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-1968p5  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_kafka_clusters.per_env         | Max Kafka Clusters Per         | environment |            20 | 1     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-381qyj  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_kafka_clusters.per_env         | Max Kafka Clusters Per         | environment |            20 | 1     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-6o659j  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_kafka_clusters.per_env         | Max Kafka Clusters Per         | environment |            20 | 1     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-6o71w2  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_kafka_clusters.per_env         | Max Kafka Clusters Per         | environment |            20 | 1     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kg2knp  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_kafka_clusters.per_env         | Max Kafka Clusters Per         | environment |            20 | 1     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-pkyq9o  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_kafka_clusters.per_env         | Max Kafka Clusters Per         | environment |            20 | 1     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-z3y7v3  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_kafka_clusters.per_env         | Max Kafka Clusters Per         | environment |            20 | 2     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kgwrwm  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_pending_kafka_clusters.per_env | Max Pending Kafka Clusters Per | environment |             3 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-1968p5  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_pending_kafka_clusters.per_env | Max Pending Kafka Clusters Per | environment |             3 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-381qyj  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_pending_kafka_clusters.per_env | Max Pending Kafka Clusters Per | environment |             3 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-6o659j  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_pending_kafka_clusters.per_env | Max Pending Kafka Clusters Per | environment |             3 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-6o71w2  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_pending_kafka_clusters.per_env | Max Pending Kafka Clusters Per | environment |             3 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-dgzxwd  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_pending_kafka_clusters.per_env | Max Pending Kafka Clusters Per | environment |             3 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kg2knp  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_pending_kafka_clusters.per_env | Max Pending Kafka Clusters Per | environment |             3 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kgwrwm  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_pending_kafka_clusters.per_env | Max Pending Kafka Clusters Per | environment |             3 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-pkyq9o  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  kafka.max_pending_kafka_clusters.per_env | Max Pending Kafka Clusters Per | environment |             3 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-z3y7v3  |               |         |
                                           | Environment                    |             |               |       |                                      |             |               |         |
  ksql.max_apps.per_env                    | Max Ksql Apps Per Environment  | environment |            15 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-1968p5  |               |         |
  ksql.max_apps.per_env                    | Max Ksql Apps Per Environment  | environment |            15 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-381qyj  |               |         |
  ksql.max_apps.per_env                    | Max Ksql Apps Per Environment  | environment |            15 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-6o659j  |               |         |
  ksql.max_apps.per_env                    | Max Ksql Apps Per Environment  | environment |            15 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-6o71w2  |               |         |
  ksql.max_apps.per_env                    | Max Ksql Apps Per Environment  | environment |            15 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-dgzxwd  |               |         |
  ksql.max_apps.per_env                    | Max Ksql Apps Per Environment  | environment |            15 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kg2knp  |               |         |
  ksql.max_apps.per_env                    | Max Ksql Apps Per Environment  | environment |            15 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kgwrwm  |               |         |
  ksql.max_apps.per_env                    | Max Ksql Apps Per Environment  | environment |            15 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-pkyq9o  |               |         |
  ksql.max_apps.per_env                    | Max Ksql Apps Per Environment  | environment |            15 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-z3y7v3  |               |         |
  networking.max_network.per_environment   | Max network per environment    | environment |             3 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-6o659j  |               |         |
  networking.max_network.per_environment   | Max network per environment    | environment |             3 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-dgzxwd  |               |         |
  networking.max_network.per_environment   | Max network per environment    | environment |             3 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kgwrwm  |               |         |
  networking.max_network.per_environment   | Max network per environment    | environment |             3 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-pkyq9o  |               |         |
  networking.max_network.per_environment   | Max network per environment    | environment |             3 |       | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-z3y7v3  |               |         |
  networking.max_network.per_environment   | Max network per environment    | environment |             3 | 0     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-1968p5  |               |         |
  networking.max_network.per_environment   | Max network per environment    | environment |             3 | 0     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-381qyj  |               |         |
  networking.max_network.per_environment   | Max network per environment    | environment |             3 | 0     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-6o71w2  |               |         |
  networking.max_network.per_environment   | Max network per environment    | environment |             3 | 0     | 4c8541f7-cc3f-44af-a366-ad4de432fe24 | env-kg2knp  |               |         |
```
