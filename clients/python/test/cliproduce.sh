#!/usr/bin/bash
#--- A test tool to produce events to primary/secondary clusters to test the consumer_switch.py consumer.
#
USAGE="cliproduce.sh <primary|secondary> <event|switch>"

if [[ "$1" != "secondary" && "$1" != "primary" ]];then
    echo $USAGE
    exit
fi
if [[ "$2" != "event" && "$2" != "switch" ]];then
    echo $USAGE
    exit
fi

config="primary_java.config"
server="pkc-6583q.eastus2.azure.confluent.cloud:9092"
topic="common-topic"
if [ "$1" = "secondary" ]; then
    config="secondary_java.config"
    server="pkc-ryzn9.westus3.azure.confluent.cloud:9092"
fi
if [ "$2" = "switch" ]; then
    topic="traffic-router"
fi

echo "Sample events"
echo '{ "EVENT": "event - consume", "LAG": "10", "SITE": "secondary" }'
echo '{ "EVENT": "yyyymmddhhmm", "LAG": "10", "SITE": "secondary" }'

kafka-console-producer --bootstrap-server $server --topic $topic --producer.config $config
