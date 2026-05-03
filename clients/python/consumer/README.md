# Smart Consumer

A consumer with following capabilities
1. Consume from the primary cluster on first boot
2. Ensure sticks to the same cluster during reboots
3. Switch cluster based on a event in a topic (traffic-router) in secondary cluster, with no restarts / config changes

smartconsumer.py is an Object Oriented version of consumer_switch.py to meet OAI needs

## Test tools
Produce a event to primary cluster
```
./cliproduce.sh primary event
'{ "EVENT": "event1", "LAG": "bla", "SITE": "primary" }'
'{ "EVENT": "event2", "LAG": "bla", "SITE": "primary" }'
'{ "EVENT": "event3", "LAG": "bla", "SITE": "primary" }'
```

Produce a event to secondary cluster
```
./cliproduce.sh secondary event
'{ "EVENT": "event1", "LAG": "bla", "SITE": "secondary" }'
'{ "EVENT": "event2", "LAG": "bla", "SITE": "secondary" }'
'{ "EVENT": "event3", "LAG": "bla", "SITE": "secondary" }'
```

Produce a event to trffic-router topic in secondary cluster to trigger a failover/failback
```
./cliproduce.sh secondary switch
'{ "EVENT": "event1", "LAG": "10", "SITE": "secondary" }'
'{ "EVENT": "event2", "LAG": "10", "SITE": "primary" }'
```

Note: The EVENT, LAG, SITE attributes are made up for some event consumption, the SITE attribute has to be primary / secondary in the traffic-router topic as the consumer switches cluster based on this attribute.
