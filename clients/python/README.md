## Troubleshooting Clients

Producer - In the client configuration set 
```
debug=broker,topic,msg
```
This will provide information on handling the broker connection, topic metadata, and message transmission.

Conumer - set
```
debug=cgrp,topic,fetch
```
This will provide information on consumer group state, topic metadata, and message fetching
