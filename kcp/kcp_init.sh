kcp migration init \
--k8s-namespace confluent \
--initial-cr-name confluent-gateway-cp \
--source-bootstrap 18.220.31.188:33333 \
--use-sasl-plain \
--sasl-plain-username admin \
--sasl-plain-password admin-secret \
--cluster-bootstrap pkc-09zmdp.us-east-1.aws.confluent.cloud:9092 \
--cluster-id lkc-86p6xm \
--cluster-rest-endpoint https://pkc-09zmdp.us-east-1.aws.confluent.cloud:443 \
--cluster-link-name my_cp_cc_link \
--cluster-api-key CHANGE_ME \
--cluster-api-secret CHANGE_ME \
--fenced-cr-yaml  /home/ubuntu/kcp/gateway-cp.yaml \
--switchover-cr-yaml /home/ubuntu/kcp/gateway-cc.yaml

