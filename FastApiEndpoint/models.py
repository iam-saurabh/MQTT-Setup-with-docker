from mongoengine import Document, StringField, IntField

# schema of our Database
class Sensor_readings(Document):
    sensor_id = StringField()
    value = IntField()
    timestamp = StringField()
