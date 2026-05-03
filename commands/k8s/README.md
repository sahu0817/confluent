### Port forwarding 
#### on local host
```
> kubectl port-forward svc/keycloak 8080:8080 -n confluent
Forwarding from 127.0.0.1:8080 -> 8080
```

#### on all interfaces ( useful when hosted in cloud )
```
> kubectl port-forward --address 0.0.0.0 svc/keycloak 8080:8080 -n confluent
Forwarding from 0.0.0.0:8080 -> 8080
```
