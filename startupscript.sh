#!/bin/bash

echo "Starting docker compose ..."
cd "$(dirname "$0")"
docker-compose up -d



echo "Waiting for broker container to start and is healthy..."

while [[ "$(docker inspect -f '{{.State.Health.Status}}' "broker")" != "healthy" ]]; do
    echo "Container is not healthy. Checking again in 30 seconds..."
    sleep 30
done

echo "broker container is healthy."



if [ -f .env ]; then
    set -a
    . .env
    set +a
else
    echo ".env file not found!"
    exit 1
fi

export TOPIC_NAME=weather_now


check_kafkatopic_exists(){
    docker exec -it broker kafka-topics --bootstrap-server localhost:9092 --list | grep -w $TOPIC_NAME
}

check_cassandra_healthy(){
    docker exec cassandra cqlsh -e "SELECT now() FROM system.local;" > /dev/null 2>&1
    return $?
}

while ! check_kafkatopic_exists; do
    echo "Topic '$TOPIC_NAME' not found on $(date +'%H:%M'). Checking again in 1 minute..."
    sleep 60
done

while ! check_cassandra_healthy; do
    echo "Cassandra db not ready on $(date +'%H:%M'). Checking again in 1 minute..."
    sleep 60
done

echo "Kafka topic found and Cassandra ready. Executing sparkstream."

.venv/bin/python main/sparkstream.py