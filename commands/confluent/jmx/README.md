## JMX configuration
```
-Dcom.sun.management.jmxremote \
-Dcom.sun.management.jmxremote.port=9090 \
-Dcom.sun.management.jmxremote.rmi.port=9090 \
-Dcom.sun.management.jmxremote.authenticate=false \
-Dcom.sun.management.jmxremote.ssl=false \
-Djava.rmi.server.hostname=$(/usr/bin/curl -s --connect-timeout 2 http://169.254.169.254/latest/meta-data/public-ipv4)
```

#### Enable JMX on local connect service
```
[ubuntu@awst2x ~/confluent-7.6.0/bin]# diff connect-distributed.orig connect-distributed
75a76,78
> export KAFKA_JMX_OPTS="-Dcom.sun.management.jmxremote=true -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -Djava.rmi.server.hostname=18.220.31.188 -Dcom.sun.management.jmxremote.port=9876 -Dcom.sun.management.jmxremote.rmi.port=9876"


[ubuntu@awst2x ~/confluent-7.6.0/bin]# ps -ef | grep connect | grep properties  | tr ' ' '\n' | egrep -i "jmx|host"
-Dcom.sun.management.jmxremote=true
-Dcom.sun.management.jmxremote.authenticate=false
-Dcom.sun.management.jmxremote.ssl=false
-Dcom.sun.management.jmxremote.port=9876
-Dcom.sun.management.jmxremote.rmi.port=9876
-Djava.rmi.server.hostname=18.220.31.188
```

#### Kafka Jmx tool (https://support.confluent.io/hc/en-us/articles/360030135351-How-to-use-Kafka-s-JMXTool-to-Collect-Metrics)
```
[ubuntu@awst2x ~/confluent-7.6.0]# bin/kafka-run-class kafka.tools.JmxTool \
--object-name "kafka.connect:type=connect-worker-metrics" \
--attributes task-count  \
--jmx-url service:jmx:rmi:///jndi/rmi://18.220.31.188:9876/jmxrmi   \
--reporting-interval 1000 
WARNING: The 'kafka.tools' package is deprecated and will change to 'org.apache.kafka.tools' in the next major release.
Trying to connect to JMX url: service:jmx:rmi:///jndi/rmi://18.220.31.188:9876/jmxrmi
"time","kafka.connect:type=connect-worker-metrics:task-count"
1717509275253,2.0
1717509276253,2.0
1717509277254,2.0
1717509278254,2.0

[ubuntu@awst2x ~/confluent-7.6.0]# bin/kafka-run-class kafka.tools.JmxTool \
--object-name "kafka.connect:type=connector-metrics,connector=*" \
--attributes status  \
--jmx-url service:jmx:rmi:///jndi/rmi://18.220.31.188:9876/jmxrmi \
--reporting-interval 1000 
WARNING: The 'kafka.tools' package is deprecated and will change to 'org.apache.kafka.tools' in the next major release.
Trying to connect to JMX url: service:jmx:rmi:///jndi/rmi://18.220.31.188:9876/jmxrmi
"time","kafka.connect:type=connector-metrics,connector=ch_conn:status","kafka.connect:type=connector-metrics,connector=simple:status"
1717517742399,running,running
1717517743400,running,running
1717517744399,running,running
1717517745399,running,running
1717517746398,running,running
```
