# Exalens Coding Challenge

**Challenge Overview:**

- **Purpose**: Simulate the behaviour of sensors, monitor their readings, and provide APIs to retrieve data based on specific criteria.
1. **MQTT Broker Setup**: Deploy a Mosquitto MQTT broker using Docker.
2. **MQTT Publisher**: Create a Python MQTT client to mimic multiple sensor readings, publishing to topics like sensors/temperature and sensors/humidity.
    1. 
        
        Structure of the JSON payload
        
        - `{ "sensor_id": "unique_sensor_id", "value": "<reading_value>", "timestamp": "ISO8601_formatted_date_time" }`:
3. **MQTT Subscriber**: Construct a Python MQTT subscriber to store the received messages in a MongoDB collection.
4. **Data Storage**: Initiate a MongoDB instance using Docker and save the incoming MQTT messages.
5. **In-Memory Data Management**: Implement Redis using Docker to store the latest ten sensor readings.
6. **FastAPI Endpoint**: Design an API with the following endpoints:
    - An endpoint that allows users to fetch sensor readings by specifying a start and end range.
    - An endpoint to retrieve the last ten sensor readings for a specific sensor.
7. **Docker Integration**: Integrate all services using Docker Compose.

## Setup for Debian-Linux

Install docker and docker compose plugins.

```bash
#apt list update
$ sudo apt-get update
# Install Docker 
$ sudo apt-get install docker.io
# Install Docker Compose
$ sudo apt-get install docker-compose-plugin
# check installation
$ docker compose version

```

## Quick Giude

```bash
docker compose up

# Endpoints
0.0.0.0/ # Implementation documentation.
/startoenddate # range of dates
/latestten # latest ten entry
/latestten/{sensor_id} #latest ten entry by sensor_id
0.0.0.0/docs #can be used for endpoint testing.
```

## MQTT Publisher

Using ‘paho.mqtt’ python library to connect to the ‘mqtt-broker’ and publish the desired payload

Two sensors are emulated ‘humidity_sensor’ and ‘temperature_sensor ’, the python script keeps running until a keyboard interrupt is detected, with the help of the docker file build container which works as a publisher for a broker.

```bash
#Dockerfile for publisher
FROM python:3.8-alpine
WORKDIR /code
COPY MQTTPublisher/requirement.txt .
RUN pip install -r requirement.txt
CMD ["python","publisher.py"]
```

```bash
# docker-compose.yml
services:
  publisher:
    build:
      context: .
      dockerfile: DockerFiles/publisher.Dockerfile
    container_name: mqtt_publisher
    tty: true
    restart: unless-stopped
    volumes:
      - ./MQTTPublisher:/code
```

python:3.8-alpine from docker-hub is a small image good for a single task with fewer requirements.

## MQTT Broker

Using docker official image ‘eclipse-mosquitto’ at default port 1883 is mapped with port 1883 of localhost.

volumes for config and logs are created and configured in the docker-compose.yml file

Note: To connect within the docker network container name can be used 

```bash
#example 
broker_address = "mqtt_broker"  # Instead of any IP or localhost containr name is used.
broker_port = 1883
```

```bash
#compose file
mqtt-broker:
    image: eclipse-mosquitto
    container_name: mqtt_broker
    tty: true
    restart: unless-stopped
    volumes:
      - ./config:/mosquitto/config # local path and container path 
      - ./log:/mosquitto/log
    ports:
      - 1883:1883 # local port to container port
```

## MQTT Subscriber / DataBase

Like in the publisher case we Use ‘paho.mqtt’ python library to connect to the ‘mqtt-broker’ and subscribe to the desired topic

Two topics are subscribed ‘humidity_sensor’ and ‘temperature_sensor ’, the python script keeps running until a keyboard interrupt is detected, with the help of the docker file build container which works as a subscriber for the broker.

The subscriber in this case also stores the received message into the MongoDB which is running in a container that is created by using docker official image Mongo, deployed at the default port, here we can also pass the container name for docker intra-net connections.

```bash
# example to connect to MOngoDB
uri = "mongodb://mongodb:27017/"
db_name = "sensor_data"
collection_name = "sensor_readings"
```

```bash
# Docker compose file for subscriber and DB
subscriber:
    build:
      context: .
      dockerfile: DockerFiles/subscriber.Dockerfile
    container_name: mqtt_subscriber
    tty: true
    restart: unless-stopped
    volumes:
      - ./MQTTSubscriber:/code
  db:
    image:  mongo
    container_name: mongodb
    tty: true
    restart: unless-stopped 
    ports:
      - 27017:27017
    volumes:
      - ./data:/data/db
```

To make data persistent i.e. data cannot be deleted after removal of the container then /data/db of the container is connected with ./data on a local machine by using volumes. 

## FastAPI / Redis

Endpoints created and are cached using the Redis server which is deployed as container by using the docker official image  ‘redis’

FastAPI is running on uvicorn server on port 8000 but to showcase how we can map the port of the container to any available port of the local network.

 

```bash
# Docker composer for redis and FastAPI
fastapi:
    build:
      context: .
      dockerfile: DockerFiles/fastapi.Dockerfile
    container_name: fastapi
    tty: true
    restart: unless-stopped
    volumes:
      - ./FastApiEndpoint:/code
    ports:
      - 80:8000
  redis:
    image: redis
    tty: true
    container_name: redis
    restart: unless-stopped
    ports:
      - 6379:637
```

```bash
# Endpoints
/starttoenddate  #"http://0.0.0.0/starttoenddate" can be querryied by putting startdate

# and enddate 
#exmple  "http://0.0.0.0/startoenddate?startDate=2023-08-25T22%3A25%3A02.819517&endDate=2023-08-25T23%3A53%3A33.850691"

/latestten # This endpoint gives the latest ten readings from all the sensors, this endpoint is cached with Redis server, and the key expiry time is set to 10 sec.

/latestten/{sensor_id} # a string containing sensor_id is passed to the latest ten entries of a specific sensor, this endpoint is also cached with Redis.

/allData # fetches all data stored in DB and is also cashed with redis with an expiry of 30 sec.
 0.0.0.0/ # Implementation documentation.

0.0.0.0/docs #can be used for endpoint testing.
```

## Some Important Commands

```bash
docker compose up # in same directory as docker-compose.yml
# you can start a specific service by using its name in compose file
docker compose up db # it will only start or build only DB
ctrl+c # used for stopping running containers 
docker compose down  # stop and remove containers
docker compose build # to rebuild or build container after change.
docker rm $(docker ps -aq) # removing all containers
docker image rm $(docker images) # removing all Images

```

## Challenges Faced

During the occurrence of any error in containers, they tend to just exit and I have to start them again like when the MQTT-Broker container was not started and the other containers that were dependent upon it just gave that it couldn't connect to the broker exit after adding ‘restart: ’ it helped and restarts the container.

Not able to look at the error log at the terminal itself then tty: True helped a lot it kept the terminal running container and kept popping their messages.

During Mosquitto config it gave some error because of not using volumes correctly but after some time it sorted out.
