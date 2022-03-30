from audioop import reverse
from logging import Filter
from fastapi import HTTPException
from http import HTTPStatus
from decouple import config
import motor.motor_asyncio

from app.db.responseModels import ListingResponseModel
from .requestModels import ListingRequestModel, AddressModel
from .genericModels import ListingModel
from bson.objectid import ObjectId
from geopy.geocoders import GoogleV3
from geopy import distance

# Database Init
client = motor.motor_asyncio.AsyncIOMotorClient(config("DATABASE_URI"))
db = client.SPOT

# Database Collections
userCollection = db.User
listingCollection = db.Listings

# A dictionary that correlates the db collections to each category
listingsCollections = {
    "Test": db.TestListings,
    "Car": db.CarListings
}

async def create_listing(listing: ListingRequestModel):
    
    updatedListing = listing.dict()

    
    # determine category
    listingCollection = listingsCollections.get(updatedListing.get("category"))
    
    if listingCollection == None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail="Invalid Category")
    
    # Check if listing exists
    found_listing = await listingCollection.find_one(updatedListing)   
    
    if found_listing != None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail="Listing already exists")
    
    #Inserting GPS cords into the dict

    #**********************Commented out to not spam API calls for google maps UNCOMMENT FOR FINAL PRODCUT THANK YOU********************


    # location = getGPS(listing.address)
    
    # if location == None:
    #     raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail="Invalid Address")
    
    # updatedListing["locationLONG"] = location.longitude
    # updatedListing["locationLAT"] = location.latitude

    updatedListing["locationLONG"] = -77.036560
    updatedListing["locationLAT"] = 38.897957

    
   
    # Remove address from dict
    updatedListing.pop('address')
    
    # Add rentals 
    updatedListing["rentals"] = list()
    
    # Insert listing onto db
    newListing = await listingCollection.insert_one(updatedListing)
    
    # Find the new listing in the db
    createdListing = await listingCollection.find_one({"_id":newListing.inserted_id})

    # Decode the listing to a dict
    decodedListing = decode_bson(createdListing,ListingResponseModel.get_keys())
    
    return decodedListing   
    
async def get_listing(listingId: str, category : str):
    #validate listing id input
    try:
        objectId = ObjectId(listingId)
    except Exception:
       raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail="Invalid Listing Id")
    
    # Check if category is valid
    listingCollection = listingsCollections.get(category)
    
    if listingCollection == None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail="Invalid category")
    
    # Find the listing in the db
    listing = await listingCollection.find_one({"_id":objectId})
   
    if listing == None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail="Listing does not exist")
    
    # Decode the listing to a dict
    decodedListing = decode_bson(listing,ListingResponseModel.get_keys())
    return decodedListing
    
async def sort_listing_by_location(category : str, zip: str):
    
    if len(zip) < 5:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail="Invalid Zip Code")
    
    listings = await get_all_listings(category)

    location = getGPS(zip)


    #Appending "distance" field to sort on and so the front end can display
    for listing in listings:
        listing["distance"] = format(distance.great_circle((listing["locationLAT"], listing["locationLONG"]), (float(location.latitude), float(location.longitude))).miles, '.2f')

    return sorted(listings, key = lambda listing: float(listing["distance"]))

async def get_all_filtered_listings(category: str, filters: dict):

    listings = await get_all_listings(category)
    newListings = []

    for listing in listings:
        if filters.items() <= listing["attributes"].items(): #<= checks if it is a subset of the other
            newListings.append(listing)

    
    return newListings

async def modify_listing(listingId:str, listing: dict):
    
    # If there are no none values withing the listing
    if len(listing) >= 1:
        try:
            objectId = ObjectId(listingId)
        except Exception:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail="Invalid Listing Id")
        
        listingCollection = listingsCollections.get(listing.get("category"))
        
        # Find the listing in the db
        found_listing = await listingCollection.find_one({"_id":objectId})
        if found_listing != None:
            
            #Updating listing address and gps coordinates
            if(listing["address"] != None):

                addressModel = AddressModel.parse_obj(listing["address"])
                

                #UNCOMMENT THIS WHEN FINAL PRODCUT OKAY
                #CURRENTLY JUST COORDS FOR THE WHITE HOUSE SO WE DONT SPAM GOOGLE API THANK YOU

                # location = getGPS(addressModel)

                # listing["locationLONG"] = location.longitude
                # listing["locationLAT"] = location.latitude

                listing["locationLONG"] = -77.036560
                listing["locationLAT"] = 38.897957
                
            # Remove address from dict
            #listing.pop('address')
            
            await listingCollection.update_one({"_id": objectId}, {"$set": listing})
            
            updated_listing = await listingCollection.find_one({"_id":objectId})
            return decode_bson(updated_listing,ListingResponseModel.get_keys())
        else:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail="Listing does not exist")
    else:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail="No Modifications")

async def delete_listing(listingId: str,category : str):
    try:
        objectId = ObjectId(listingId)
    except Exception:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail="Invalid Listing Id")
    
    # Check if category is valid
    listingCollection = listingsCollections.get(category)
    
    if listingCollection == None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail="Invalid category")
    
    found_listing = await listingCollection.find_one({"_id":objectId})
    
    if found_listing != None:
        await listingCollection.delete_one({"_id": objectId})
        raise HTTPException(status_code=HTTPStatus.OK,detail="Successfully Deleted Listing")
    else:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail="Listing Id Not Found")

async def get_all_listings_sorted(category : str, filters : dict, zip : str, sort: str):

    listings = await get_all_filtered_listings(category, filters)
    

    location = getGPS(zip)

    for listing in listings:
        listing["distance"] = format(distance.great_circle((listing["locationLAT"], listing["locationLONG"]), (float(location.latitude), float(location.longitude))).miles, '.2f')

    if sort == "distance":
        return sorted(listings, key = lambda listing: float(listing["distance"]))

    if sort == "priceLowToHigh":
        return sorted(listings, key = lambda listing: float(listing["item_price"]))

    if sort == "priceHighToLow":
        return sorted(listings, key= lambda listing: float(listing["item_price"]), reverse=True)


    


async def get_all_listings(category : str):
    
    # Check if category is valid
    listingCollection = listingsCollections.get(category)
    
    if listingCollection == None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,detail="Invalid category")
    
    # Finds the first 1000 results within the listing collection
    listings = await listingCollection.find().to_list(1000)
   
    decoded_listings = list()
    if listings != None:
        for listing in listings:
            decoded_listings.append(decode_bson(listing,ListingResponseModel.get_keys()))
        
    return decoded_listings


def decode_bson(document,keys):
    newDict = dict()
    newDict["listing_id"] = str(document["_id"])
    
    for key in keys:
        newDict[key] = document[key]

    return newDict


def getGPS(zip: str):
    # Convert address to long & lat and add it to the dict
    geolocator = GoogleV3(api_key=config("MAPS"))
  

    location = geolocator.geocode(zip)
    return location


# def computeDistance(listings, zip):

#     location = getGPS(zip)

#     for listing in listings:
#         listing["distance"] = format(distance.great_circle((listing["locationLAT"], listing["locationLONG"]), (float(location.latitude), float(location.longitude))).miles, '.2f')