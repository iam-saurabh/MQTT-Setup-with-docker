import paho.mqtt.client as mqtt
import json
import pymongo 

# MQTT broker settings
broker_address = "mqtt_broker"  # Update this to your MQTT broker's address
broker_port = 1883
client_id = "mqtt_subscriber"

# MongoDB settings
uri = "mongodb://mongodb:27017/"
db_name = "sensor_data"
collection_name = "sensor_readings"

# Callback when a message is received on MQTT
def on_message(client,userdata, message):
    payload = json.loads(message.payload.decode('utf-8'))
    print("Received message:", payload)
    # Store the received message in MongoDB
    clientDb = pymongo.MongoClient(uri)
    db = clientDb[db_name]
    collection = db[collection_name]
    collection.insert_one(payload)
    clientDb.close()
    print("Stored in MongoDB")

# Create MQTT client instance
client = mqtt.Client(client_id)

# Set the on_message callback
client.on_message = on_message

# Connect to the broker
client.connect(broker_address, broker_port, keepalive=60)

# Subscribe to MQTT topics
client.subscribe("sensors/temperature")
client.subscribe("sensors/humidity")

# Start the MQTT loop
client.loop_forever()