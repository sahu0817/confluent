# Smart Producer

A producer tool with following capabilities
1. Produce to the primary cluster on initial boot
2. Write to a local cache along with producing - Used to replay the events during DR from a certain timestamp based on lag data. ( WIP )
3. Stick to the same cluster during reboot
4. Switch cluster based on a event in a topic (traffic-router) in secondary cluster

## Version 1: RPO=0 with duplicates ( current state ) 

  The messages that did not make it to the DR (via ClusterLink) site during a Disaster, need to be identified and replayed from cache based on TIMESTAMP  
  This approach could lead to some events re-produced that already exist on DR site.


[![Smart Producer V1](../../images/SmartProducerV1.jpeg)]()

> Note: the producer is not in the same region/zone as Confluent cloud cluster

## Version 2: RPO=0 with NO duplicates ( future state )

  The messages that did not make it to the DR (via ClusterLink) site during a Disaster, need to be identified and replayed from cache based on OFFSET  
  This approach will avoid re-producing of duplicates to DR site.

[![Smart Producer V2](../../images/SmartProducerV2.jpeg)]()

> Note: the producer is not in the same region/zone as Confluent cloud cluster

