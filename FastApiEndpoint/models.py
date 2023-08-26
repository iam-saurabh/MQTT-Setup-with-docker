from mongoengine import Document, StringField, IntField, DateTimeField

# schema of our Database
class Sensor_readings(Document):
    sensor_id = StringField()
    value = IntField()
    timestamp = StringField()