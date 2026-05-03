# Testing methodology

### Integration Test
#### Run the consumer
```
> ./smartconsumer_v2.sh
```
#### Run the producer
```
> ./smartproducer_v2.sh
```
#### Run the DR failover tool
```
> ./dr_mgr.py -o failover -t force
```
#### Observation

#### Metrics

### Unit Test
#### Run the consumer
```
> ./smartconsumer_v2.sh
```
#### Run the producer
```
> ./smartproducer_v2.sh
```
#### Run a tool to introduce a event in traffic_cutover topic
```
> ./smartproducer_v2.sh
```
