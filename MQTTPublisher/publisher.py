import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# MQTT broker settings
broker_address = "mqtt_broker"  # Update this to your MQTT broker's address
broker_port = 1883
client_id = "sensor_simulator"

# Function to generate a random sensor reading
def generate_sensor_humidity_reading():
    return round(random.uniform(25, 100), 2)
def generate_sensor_temperature_reading():
    return round(random.uniform(15, 50), 2)
# Function to generate a JSON payload
def generate_payload(sensor_id, value):
    timestamp = datetime.now().isoformat()
    payload = {
        "sensor_id": sensor_id,
        "value": value,
        "timestamp": timestamp
    }
    return json.dumps(payload)

# Callback when the client is connected to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with code:", rc)

# Create MQTT client instance
client = mqtt.Client(client_id)

# Set the on_connect callback
client.on_connect = on_connect

# Connect to the broker
client.connect(broker_address, broker_port, keepalive=60)

# Start the MQTT loop
client.loop_start()

try:
    while True:
        # Generate sensor readings
        temperature_reading = generate_sensor_temperature_reading()
        humidity_reading = generate_sensor_humidity_reading()

        # Generate JSON payloads
        temperature_payload = generate_payload("temperature_sensor", temperature_reading)
        humidity_payload = generate_payload("humidity_sensor", humidity_reading)

        # Publish to MQTT topics
        client.publish("sensors/temperature", temperature_payload)
        client.publish("sensors/humidity", humidity_payload)

        print("Published temperature:", temperature_payload)
        print("Published humidity:", humidity_payload)

        time.sleep(5)  # Wait for 5 seconds before generating and publishing the next readings

except KeyboardInterrupt:
    print("Stopping the sensor simulator...")
    client.disconnect()
    client.loop_stop()
