# KCP client switchover runbook

This runbook documents an end-to-end workflow for Confluent Platform to Confluent Cloud migration with **Confluent Kafka Proxy (KCP)** : 
High Level workflow
- Deploy a Single Node Kafka server in Docker 
- Deploy a Kafka cluster in Confluent Cloud
- Deploy 2 gateways on Kubernetes
- Expose gateways with MetalLB
- Validate with console clients
- Configure a **cluster link**
- Switchover LoadBalancer from Confluent Platform to Confluent CLoud with `kcp` CLI.  

For upstream product context and releases, see the official repository: [confluentinc/kcp README](https://github.com/confluentinc/kcp/blob/main/README.md).

---

## Contents

1. [Prerequisites](#prerequisites)
2. [Create a Local Kind k8s Cluster](#create-a-Local-Kind-k8s-Cluster)
3. [Install the KCP binary](#install-the-kcp-binary)
4. [Deploy Kafka](#deploy-kafka)
5. [Provision Confluent Cloud Cluster](#provision-confluent-cloud-cluster)
6. [Deploy Confluent Platform and Confluent Cloud gateways](#deploy-confluent-platform-and-confluent-cloud-gateways)
7. [MetalLB and load balancer (VM / kind clusters)](#metallb-and-load-balancer-vm--kind-clusters)
8. [Sanity test: produce and consume via CP gateway](#sanity-test-produce-and-consume-via-cp-gateway)
9. [Create Cluster link](#create-cluster-link)
10. [KCP migration workflow](#kcp-migration-workflow)
11. [Validate Client Switchover ](#validate-client-switchover)
12. [Tear Down](#tear-down)

---

## Prerequisites

- Linux host (this demo uses Ubuntu on AWS EC2).
- **Docker** for Kafka containers.
- **Kubernetes** cluster with `kubectl` configured (example included `kindest/node` control plane and Confluent Operator).
- **Confluent CLI** where `confluent kafka link` / `confluent kafka topic` are used.
- Kafka client tools: `kafka-console-producer`, `kafka-console-consumer`, `kafka-cluster`.

---

## Create a Local Kind k8s Cluster
:information_source: You can provision a Cloud Native K8s Cluster on EKS/AKS/GKE instead

```bash
> helm repo add confluentinc https://packages.confluent.io/helm
"confluentinc" already exists with the same configuration, skipping

> helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "confluentinc" chart repository
...Successfully got an update from the "grafana" chart repository
...Successfully got an update from the "prometheus-community" chart repository
Update Complete. ⎈Happy Helming!⎈

> kind create cluster -n confluent
Creating cluster "confluent" ...
 ✓ Ensuring node image (kindest/node:v1.27.1) 🖼
 ✓ Preparing nodes 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
Set kubectl context to "kind-confluent"
You can now use your cluster with:

kubectl cluster-info --context kind-confluent

Thanks for using kind! 😊

> docker ps
CONTAINER ID   IMAGE                           COMMAND                  CREATED          STATUS          PORTS                                                                                                                                               NAMES
3f89c6b1c14e   kindest/node:v1.27.1            "/usr/local/bin/entr…"   10 minutes ago   Up 10 minutes   127.0.0.1:41551->6443/tcp                                                                                                                           confluent-control-plane
```

Create confluent namespace
```bash
> kubectl  create namespace confluent
namespace/confluent created
```

## Install the latest KCP binary

Download the Linux amd64 archive [confluentinc/kcp ](https://github.com/confluentinc/kcp/releases), extract it, and install `kcp` on your `PATH`:

```bash
> tar -xzf kcp_linux_amd64.tar.gz && sudo cp ./kcp/kcp /usr/local/bin

> kcp version
Executing kcp with build version=0.7.2 commit=4ef9d5712187a9eefbd77bc948ed5923ce9e2e0b date=2026-04-07T17:36:35Z
Version: 0.7.2
Commit:  4ef9d5712187a9eefbd77bc948ed5923ce9e2e0b
Date:    2026-04-07T17:36:35Z
```

---

## Deploy Kafka

:information_source: Before you start, update the EXTERNAL advertised listener. Need to provide a routable IP for the Gateway to reach.

```bash
> grep KAFKA_ADVERTISED_LISTENERS  kafka-compose.yaml
      KAFKA_ADVERTISED_LISTENERS: 'INTERNAL://kafka-1:44444,EXTERNAL://18.220.31.188:33333'
```

```bash
> ./start-kafka.sh
Starting Kafka containers...
[+] Building 0.0s (0/0)
[+] Running 2/2
 ✔ Network kcp_default  Created                                                                                                   0.1s
 ✔ Container kafka-1    Started                                                                                                   0.4s
Kafka containers started. You can now start the Gateway with: ./start-gateway.sh

> docker ps
CONTAINER ID   IMAGE                           COMMAND                  CREATED          STATUS          PORTS                                                                                                                                               NAMES
e72ab89690d5   kindest/node:v1.27.1            "/usr/local/bin/entr…"   19 minutes ago   Up 19 minutes   127.0.0.1:33189->6443/tcp                                                                                                                           confluent-control-plane
3ce0cbfbc9ce   confluentinc/cp-server:latest   "/etc/confluent/dock…"   3 seconds ago    Up 2 seconds    0.0.0.0:9093->9093/tcp, :::9093->9093/tcp, 0.0.0.0:33333->33333/tcp, :::33333->33333/tcp, 9092/tcp, 0.0.0.0:44444->44444/tcp, :::44444->44444/tcp   kafka-1
```

You should see a container such as `kafka-1` exposing broker ports (example mapping included `9093`, `33333`, `44444`).

---
## Provision Confluent Cloud Cluster
Follow the instructions [here](https://docs.confluent.io/cloud/current/clusters/create-cluster.html#create-ak-clusters) to create one.

```bash
> confluent kafka cluster describe lkc-86p6xm
+----------------------+----------------------------------------------------------+
| Current              | true                                                     |
| ID                   | lkc-86p6xm                                               |
| Name                 | test1                                                    |
| Type                 | DEDICATED                                                |
| Cluster Size         | 2                                                        |
| Ingress Limit (MB/s) | 120                                                      |
| Egress Limit (MB/s)  | 360                                                      |
| Storage              | Unlimited                                                |
| Cloud                | aws                                                      |
| Region               | us-east-1                                                |
| Availability         | multi-zone                                               |
| Status               | UP                                                       |
| Endpoint             | SASL_SSL://pkc-09zmdp.us-east-1.aws.confluent.cloud:9092 |
| REST Endpoint        | https://pkc-09zmdp.us-east-1.aws.confluent.cloud:443     |
| Topic Count          | 51                                                       |
+----------------------+----------------------------------------------------------+
```
Create a Key/Secret for the Kafka cluster. This will be used by cluster-link and kcp tool.

```bash
> confluent api-key create --resource lkc-86p6xm --service-account sa-wy876j
+---------+------------------------------------------------------------------+
| API Key | XXXXXXX                                                          |
| Secret  | XXXXXXXXXX                                                       |
+---------+------------------------------------------------------------------+
```
---

## Deploy Confluent Gateways

Deploy Confluent CFK Operator
```bash
> helm upgrade --install confluent-operator confluentinc/confluent-for-kubernetes -n confluent
Release "confluent-operator" does not exist. Installing it now.
NAME: confluent-operator
LAST DEPLOYED: Thu Apr  2 18:22:37 2026
NAMESPACE: confluent
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
The Confluent Operator

The Confluent Operator brings the component (Confluent Services) specific controllers for kubernetes by providing components specific Custom Resource
Definition (CRD) as well as managing other Confluent Platform services
```
Deploy Confluent Platform & Confluent Cloud Gateways
```bash
> ./start-gateway-k8s.sh
gateway.platform.confluent.io/confluent-gateway-cp created
gateway.platform.confluent.io/confluent-gateway-cc created

> kubectl get services -n confluent
NAME                              TYPE           CLUSTER-IP      EXTERNAL-IP    PORT(S)                                                                                                                         AGE
confluent-operator                ClusterIP      10.96.51.125    <none>         7778/TCP                                                                                                                        3m31s
confluent-gateway-cp              ClusterIP      10.96.152.20    <none>         9595/TCP,9596/TCP,9597/TCP,9598/TCP,9190/TCP                                                                                    2m7s
confluent-gateway-cc              ClusterIP      10.96.3.205     <none>         9595/TCP,9596/TCP,9597/TCP,9598/TCP,9599/TCP,9600/TCP,9601/TCP,9602/TCP,9603/TCP,9604/TCP,9605/TCP,9606/TCP,9607/TCP,9190/TCP   2m6s
```

---

## MetalLB and load balancer (VM / kind clusters)

On a VM or **kind**-style cluster, gateway `ClusterIP` services typically do not get a stable **external** IP. **MetalLB** provides a load-balancer implementation so clients outside the cluster can reach the gateway on a known IP.

1. Install MetalLB (native manifest example):

   ```bash
   > kubectl apply -f metallb-native.yaml
   ```
2. Get the IP Address range for your Kind cluster

   Kind runs in Docker, so you need IPs that Docker understands. Run this on your host to get the address range.
   ```bash
   docker network inspect -f '{{.IPAM.Config}}' kind
   [{172.19.0.0/16  172.19.0.1 map[]} {fc00:f853:ccd:e793::/64  fc00:f853:ccd:e793::1 map[]}]
   ```
   Use the above range in your metallb-config.yaml
   ```bash
   > grep addresses -A 1 metallb-config.yaml
     addresses:
     - 172.19.0.200-172.19.0.250 # Change to your actual network range
   ```

3. Configure an address pool and L2 advertisement:

   ```bash
   > kubectl apply -f metallb-config.yaml

   ipaddresspool.metallb.io/first-pool created
   l2advertisement.metallb.io/l2-adv created
   ```

4. Expose the switchover entrypoint with a `LoadBalancer` service:

   Initially points to CP .... `spec.selector.app: confluent-gateway-cp`
   ```bash
   > grep spec -A 3 loadbalancer-service.yaml
     spec:
       type: LoadBalancer
       selector:
         app: confluent-gateway-cp
   ```
   ```bash
   > kubectl apply -f loadbalancer-service.yaml
   service/confluent-gateway-switchover-lb created
   ```

5. Confirm the service has an `EXTERNAL-IP`:

   ```bash
   > kubectl get services -n confluent
   NAME                              TYPE           CLUSTER-IP      EXTERNAL-IP    PORT(S)                                                                                                                         AGE
   confluent-operator                ClusterIP      10.96.51.125    <none>         7778/TCP                                                                                                                        3m31s
   confluent-gateway-cc              ClusterIP      10.96.3.205     <none>         9595/TCP,9596/TCP,9597/TCP,9598/TCP,9599/TCP,9600/TCP,9601/TCP,9602/TCP,9603/TCP,9604/TCP,9605/TCP,9606/TCP,9607/TCP,9190/TCP   2m6s
   confluent-gateway-cp              ClusterIP      10.96.152.20    <none>         9595/TCP,9596/TCP,9597/TCP,9598/TCP,9190/TCP                                                                                    2m7s
   confluent-gateway-switchover-lb   LoadBalancer   10.96.204.148   172.19.0.200   9595:30444/TCP,9596:31421/TCP,9597:31630/TCP,9598:30913/TCP
   ```

6. Point your client bootstrap hostname (e.g. `gateway.example.com`) at the external IP.
   ```bash
   > grep -i gateway /etc/hosts
   # Gateway
   172.19.0.200 gateway.example.com
   ```

---

## Sanity test: produce and consume via CP gateway

Use the CP client config and the gateway bootstrap (host and port from your MetalLB / DNS setup). Example topic: `gateway-client-switchover-test`.

**Produce:**

```bash
> kafka-console-producer --bootstrap-server gateway.example.com:9595 --producer.config cp-client.config --topic gateway-client-switchover-test
>Test message 1
[2026-04-09 18:26:20,030] WARN [Producer clientId=console-producer] Error while fetching metadata with correlation id 5 : {gateway-client-switchover-test=UNKNOWN_TOPIC_OR_PARTITION} (org.apache.kafka.clients.NetworkClient)
>Test message 2
>Test message 3
```

:warning: You may see a one-time metadata warning (`UNKNOWN_TOPIC_OR_PARTITION`) until the topic exists; subsequent sends can succeed.

**Consume:**

```bash
> kafka-console-consumer --bootstrap-server gateway.example.com:9595 --consumer.config cp-client.config --topic gateway-client-switchover-test --from-beginning
Test message 1
Test message 2
Test message 3
^CProcessed a total of 3 messages
```

---

## Create Cluster link

**Source CP cluster ID** :

```bash
> kafka-cluster cluster-id --bootstrap-server 18.220.31.188:33333 --config cp-client.config
Cluster ID: 4L6g3nShT-eMCtK--X86sw
```

Create a **destination-initiated** cluster link in Confluent Cloud / CLI as appropriate for your environment, using the same bootstrap server you used for the cluster ID.

Describe the link :

```bash
> confluent kafka link describe my_cp_cc_link
+-------------------------------+---------------------------------+
| Name                          | my_cp_cc_link                   |
| Source Cluster                | 4L6g3nShT-eMCtK--X86sw          | 
| Destination Cluster           |                                 |
| Remote Cluster                | 4L6g3nShT-eMCtK--X86sw          |
| State                         | ACTIVE                          |
| Mirror Partition States Count | IN_ERROR: 0, UNKNOWN: 0,        |
|                               | PENDING: 0, ACTIVE: 0, PAUSED: 0|
+-------------------------------+---------------------------------+
```

After the link is **ACTIVE**, produce additional messages through the gateway and confirm they appear when consuming from the cloud side (example used `confluent kafka topic consume`).

```bash
> kafka-console-producer   --bootstrap-server gateway.example.com:9595   --producer.config cp-client.config --topic gateway-client-switchover-test
>Test message 4 after cluster link
>Test message 5 after cluster link
>Test message 6 after cluster link
```
These messages should now appear on the destination cluster
```bash
> confluent kafka topic consume --from-beginning -b gateway-client-switchover-test
Starting Kafka Consumer. Use Ctrl-C to exit.
Test message 1
Test message 2
Test message 3
Test message 4 after cluster link
Test message 5 after cluster link
Test message 6 after cluster link 
```
---

## KCP migration workflow

### Initialize

```bash
> ./kcp_init.sh
Executing kcp with build version=0.7.2 commit=4ef9d5712187a9eefbd77bc948ed5923ce9e2e0b date=2026-04-07T17:36:35Z
2026/04/09 18:49:41 WARN gateway CR validation not yet implemented, skipping
   ✔ Gateway CRs validated
   ✔ Cluster link validated (1 mirror topics active)
✅ Migration initialized: migration-729f6ecd-f4bb-4d78-b3c5-8d2d2f48eb8f
```
:information_source: Creates a migration-state.json and logs the activities in kcp.log

### List migrations

```bash
> kcp migration  list
Executing kcp with build version=0.7.2 commit=4ef9d5712187a9eefbd77bc948ed5923ce9e2e0b date=2026-04-07T17:36:35Z

Migration State: migration-state.json
Last Updated: 2026-04-09 18:49:42

Migrations (1):

[1] Migration ID: migration-729f6ecd-f4bb-4d78-b3c5-8d2d2f48eb8f
    Status: initialized
    Gateway: confluent/confluent-gateway-cp
    Cluster Link: my_cp_cc_link
    Topics (1): gateway-client-switchover-test
```

### Monitor mirror lag

```bash
> ./kcp_lag-check.sh
Executing kcp with build version=0.7.2 commit=4ef9d5712187a9eefbd77bc948ed5923ce9e2e0b date=2026-04-07T17:36:35Z
 Mirror Topic Lag Monitor

  REST Endpoint: https://pkc-09zmdp.us-east-1.aws.confluent.cloud:443
     Cluster ID: lkc-86p6xm
      Link Name: my_cp_cc

  ● Refreshing every 1s  |  Last updated: 18:53:38

  TOPIC NAME                      STATUS  TOTAL LAG  LAG TREND
  ──────────────────────────────  ──────  ─────────  ──────────────────────────────
  gateway-client-switchover-test  ACTIVE          0  ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁

  q quit  •  p partitions  •  r refresh  •  +/- interval  •  ↑↓ scroll
```

Interactive TUI: topic lag, refresh interval, quit/scroll keys (as printed by the tool).

### Migrate (fence → promote → switchover)

Before migrate, you can confirm the load balancer still selects the CP gateway (example inspection):

```bash
> ./kcp_migrate.sh
Executing kcp with build version=0.7.2 commit=4ef9d5712187a9eefbd77bc948ed5923ce9e2e0b date=2026-04-07T17:36:35Z
2026/04/09 18:59:23 WARN SASL/PLAIN without TLS: credentials will be transmitted in cleartext over the network

⏳ Checking replication lags...

⏳ Checking replication lag across 1 topics (threshold: 1)


✔ All topic lags below threshold (1)
✅ Done

🚧 Fencing gateway...
   ✔ Fenced gateway CR applied
   ↳ Waiting for pod rollout (0/3 pods replaced)...
   ↳ 2/3 new pods ready...
   ↳ 3/3 new pods ready, waiting for existing pods to terminate...
   ↳ 3/3 new pods ready, waiting for existing pods to terminate...
   ↳ 3/3 new pods ready, waiting for existing pods to terminate...
   ↳ 3/3 new pods ready, waiting for existing pods to terminate...
   ↳ 3/3 new pods ready, waiting for existing pods to terminate...
   ↳ 3/3 new pods ready, waiting for existing pods to terminate...
   ↳ 3/3 new pods ready...
   ✔ All 3 pods rolled out  
✅ Done

📤 Promoting mirror topics...
   ✔ 1/1 topics confirmed at zero lag
   ↳ gateway-client-switchover-test  lag: 0
   ↳ Promoting 1 mirror topics...
   ✔ gateway-client-switchover-test promoted
✅ Done

🔄 Switching gateway to Confluent Cloud...
   ✔ Switchover gateway CR applied
   ↳ Waiting for pod rollout (0/3 pods replaced)...
   ↳ 2/3 new pods ready...
   ↳ 3/3 new pods ready, waiting for existing pods to terminate...
   ↳ 3/3 new pods ready, waiting for existing pods to terminate...
   ↳ 3/3 new pods ready, waiting for existing pods to terminate...
   ↳ 3/3 new pods ready...
   ✔ All 3 pods rolled out
✅ Done

✅ Migration complete!
✅ Migration completed: migration-729f6ecd-f4bb-4d78-b3c5-8d2d2f48eb8f
```

---

## Validate Client Switchover

### Confirm Produce and Consume are happenning on Confluent Cloud
```bash
> kafka-console-producer   --bootstrap-server gateway.example.com:9595   --producer.config cc-client.config   --topic gateway-client-switchover-test
>Produce to cloud after switchover msg1
>Produce to cloud after switchover msg2
>Produce to cloud after switchover msg3
```

```bash
> confluent kafka topic consume --from-beginning -b gateway-client-switchover-test
Starting Kafka Consumer. Use Ctrl-C to exit.
Test message 1
Test message 2
Test message 3
Test message 4 after cluster link
Test message 5 after cluster link
Test message 6 after cluster link
Test again
Test message to cp1
Test message to cp2
produce locally
Produce to cloud after switchover msg1
Produce to cloud after switchover msg2
Produce to cloud after switchover msg3
```
---

## Tear Down

```bash
> kind delete cluster -n confluent

> docker compose -f kafka-compose.yaml down
```