read -p "Do you want to delete the connector (y/n) : " choice
if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
    echo "===== Deleting Connector"
    read -p "Enter connector Name : " connector_name
    curl --request DELETE --url "$CLOUD_URL/connect/v1/environments/${ENV_ID}/clusters/${CLUSTER_ID}/connectors/${connector_name}" --header 'Authorization: Basic '$CLOUD_AUTH'' --header 'content-type: application/json'
    printf "\n"
else
    echo "Not deleting container"
fi

read -p "Do you want to shutdown & remove the container (y/n) : " choice
if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
    echo "===== Shuttting Docker"
    docker-compose stop
    docker-compose rm
    docker volume prune
else
    echo "Not deleting docker"
fi

read -p "Do you want to delete the topic & schema (y/n) : " choice
if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
    read -p "Enter topic Name : " topic
    echo "===== Deleting Topic"

    CLUSTER_AUTH=$(echo -n $CLUSTER_KEY:$CLUSTER_SECRET | base64 -w0)
    curl --request DELETE --url "$CLUSTER_URL/kafka/v3/clusters/${CLUSTER_ID}/topics/${topic}" --header 'Authorization: Basic '$CLUSTER_AUTH''
    printf "\n"

    echo "===== Deleting Schemas"
    SR_AUTH=$(echo -n $SR_KEY:$SR_SECRET | base64 -w0)

    subject="${topic}-key"
    printf "\nHard Deleting Topic Schemas for Key : ${subject}\n"

    curl -X DELETE $SR_URL/subjects/${subject} --header 'Authorization: Basic '$SR_AUTH'' --header 'Content-Type: application/vnd.schemaregistry.v1+json'
    printf "\n"
    curl -X DELETE $SR_URL/subjects/${subject}?permanent=true --header 'Authorization: Basic '$SR_AUTH'' --header 'Content-Type: application/vnd.schemaregistry.v1+json'

    subject="${topic}-value"
    printf "\nHard Deleting Topic Schemas for Value: ${subject}\n"

    printf "\n"
    curl -X DELETE $SR_URL/subjects/${subject} --header 'Authorization: Basic '$SR_AUTH'' --header 'Content-Type: application/vnd.schemaregistry.v1+json'
    curl -X DELETE $SR_URL/subjects/${subject}?permanent=true --header 'Authorization: Basic '$SR_AUTH'' --header 'Content-Type: application/vnd.schemaregistry.v1+json'
else
    echo "Not deleting topic"
fi
