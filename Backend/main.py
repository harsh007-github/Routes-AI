from fastapi import FastAPI,HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from datetime import date, time, datetime
import requests
from enum import Enum
from dotenv import load_dotenv

# Backend se data kis kis form me aayega ya jaayega
# Home, {User Details, saved trips, past trips}, Trip save hogi via post request,
# Delete hogi via delete request when user requests to delete saved trip
# past trip, saved trip, temporarily kaise trip store hogi?

# Initial Configuration
app = FastAPI()
load_dotenv()
MONGO_DETAILS = 'mongodb://localhost:27017'
client:AsyncIOMotorClient = None
db = None

# Data Validation Models(User & Trip Namely)
class User(BaseModel):
    user_id:int
    user_name:str
    user_age:int

# class Trip_Preference(Enum):
#     Train:1
#     Bus:2
#     Flight:3

# Train Trip
class TrainTrip(BaseModel):
    source:str
    destination:str
    date_time:datetime
    classCode:str
    # trip_preference:str


# Setup and close database client
@app.on_event('startup')
def startup_db_client():
    global client,db
    client = AsyncIOMotorClient(MONGO_DETAILS)
    db = client.get_database('RoutesAI')
    print('DB Connected Successfully!')

@app.on_event('shutdown')
def shutdown_db_client():
    global client, db
    client.close()
    print('Closed DB Connection')



# Routes
@app.get('/')
def home():
    return {
        'Message': 'Home Route'
    }

# get trip details from the api for now based on entered data
@app.get('/trip')
def get_trip(trip:TrainTrip = Depends()):
    params = trip.model_dump()
    return {
        'Message': 'This endpoint will get train trip details from the rail road api',
        'InputData': params
    }


@app.get('/user/{user_id}')
def get_user(user_id:int):
    if user_id > 5:
        return {
            'id': user_id,
            'Message': 'The data you require is as follows'
        }
    else:
        return {
            'Messaage': 'Invalid User Request'
        }

# Create new user in DB
@app.post('/user/')
async def create_user(user:User):
    user_dict = user.model_dump()
    existing_user = await db.user.find_one({'user_id':user.user_id})
    if existing_user:
        raise HTTPException (
            status_code = 400,
            detail = 'User already exists in the system, try logging in'
        )
    result = await db.user.insert_one(user_dict)
    created_user = await db.user.find_one({"_id": result.inserted_id})
    created_user["id"] = str(created_user["_id"])
    del created_user["_id"]
    return {
        "Message": "User Posted Successfully",
        "Details": created_user
    }

# Create new Trip in DB
@app.post('/trips/')
async def create_trip(trip: TrainTrip):
    trip_dict = trip.model_dump()
    
    result = await db.trip.insert_one(trip_dict)

    created_trip = await db.trip.find_one({'_id': result.inserted_id})
    
    created_trip["id"] = str(created_trip["_id"])
    del created_trip["_id"]

    return {
        'Message': 'Trip Posted Successfully',
        'Details': created_trip
    }