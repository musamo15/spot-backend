import asyncio
from decouple import config
import motor.motor_asyncio
from geopy.geocoders import GoogleV3

from app.db.models.responseModels import ListingResponseModel
from app.db.models.requestModels import ListingRequestModel, AddressModel
from app.utilities.utilities import (decode_bson)

# Database Init
client = motor.motor_asyncio.AsyncIOMotorClient(config("DATABASE_URI"))
client.get_io_loop =  asyncio.get_running_loop
db = client.SPOT

# A dictionary that correlates the db collections to each category
listingsCollections = {
    "tests": db.TestListings,
    "cars": db.CarListings
}

async def get_all_categories():

    categories = await db.Categories.find({}, {"name": 1, "_id":0}).to_list(100)
    
    categoryList = list()
    
    for category in categories:
        categoryList.append(category.get("name"))
    
    return categoryList


# **********************Commented out to not spam API calls for google maps UNCOMMENT FOR FINAL PRODCUT THANK YOU********************
# def getGPS(address: AddressModel):
#     # Convert address to long & lat and add it to the dict
#     geolocator = GoogleV3(api_key=config("MAPS"))

#     address = address.street + " " + address.city + " " + address.zip + " " + address.state

#     location = geolocator.geocode(address)

#     return location
