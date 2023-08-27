import uvicorn
import json
from fastapi import FastAPI
from fastapi.responses import FileResponse
from models import Sensor_readings
from mongoengine import connect
from fastapi import Query
from datetime import datetime
import redis

# connect to resis server 
rd=redis.Redis(host="redis", port=6379, db=0)

api = FastAPI() #FastAPI intilisation app name api

connect(db="sensor_data", host="mongodb", port= 27017) # connect to MongoDB where databse name is sensor_data 

# Endpoint '/' response index.html consisting of implemantation documentation
@api.get("/")
def home():
    return FileResponse('index.html')

#Endpoint '/alldata' fetches all results from DB to redis Key allData and provide all data as response
@api.get("/alldata")
def allData():
    cache=rd.get("allData")
    if cache:
       allData=json.loads(cache)
    else:
        allData = json.loads(Sensor_readings.objects().to_json())
        rd.set("allData", json.dumps(allData))
        rd.expire("allData", 30)
    return {"alldata":allData}

#Endpoint '/startoenddate' fetches all results from DB range : startdate and enddate provided and output all data in that range.
@api.get("/startoenddate")
def starToEndDate(startDate: datetime = Query(..., description="Start date of range"),
                  endDate: datetime = Query(..., description="End date of range")):
    startDateString = startDate.isoformat()
    endDateString = endDate.isoformat()
    dateRangeData=json.loads(Sensor_readings.objects(timestamp__gte=startDateString,timestamp__lte=endDateString).to_json())
    return {f"From {startDate} to {endDate}":dateRangeData}

# Endpoint fetches latest ten data from DB and put into redis key latesTen and provide data as response
@api.get("/latestten")
def latestTen():
    cache=rd.get("latestTen")
    if cache:
        latestData = json.loads(cache)
    else:
        latestData = json.loads(Sensor_readings.objects.order_by("-timestamp").limit(10).to_json())
        rd.set("latestTen",json.dumps(latestData))
        rd.expire("latestTen", 10)
    return {"latestten":latestData}

# ENdpoint take sensor_id as input and provide latest ten entry of that sensor_id via redis.
@api.get("/latestten/{sensor_id}")
def latestTenBySensorID(sensor_id: str):
    cache = rd.get("latestTenBySensorID")
    if cache:
        latestData = json.loads(cache)
    else:
        latestData = json.loads(Sensor_readings.objects(sensor_id=sensor_id).order_by("-timestamp").limit(10).to_json())
        rd.set("latestTenBySensorID", json.dumps(latestData))
        rd.expire("latestTenBySensorID", 10)
    return {"latestTenBySensorID":latestData}
# main function running uvicorn server at 0.0.0.0:8000 of container.
if __name__ == "__main__":
    uvicorn.run(api, host="fastapi", port=8000)
