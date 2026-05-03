kubectl apply -f gateway-cp.yaml -n confluent
kubectl apply -f gateway-cc.yaml -n confluent
#kubectl wait --for=condition=Ready pod -l 'app in (confluent-cp, confluent-cc)' --timeout=600s -n confluent

