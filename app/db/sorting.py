from typing import final
from fastapi import HTTPException
from http import HTTPStatus
from bson.objectid import ObjectId
from app.db.models.responseModels import *

from datetime import datetime

from app.db.database import (listingsCollections, getGPS)
from app.utils.utilities import *

from geopy import distance


async def get_filtered_listings(category: str, filters: dict, zip: str):

    listingCollection = listingsCollections.get(category)
    
    #Converting filter strings to dateTime to compare in the db
    start_date = datetime.fromisoformat(filters["start_date"])
    end_date = datetime.fromisoformat(filters["end_date"])


    #If we wanted to add attributes we can just add "attributes" to a field in $match
    query = [
        {
            "$match" : {
                "item_price": {
                    "$gte" : float(filters["price_min"]),
                    "$lte": float(filters["price_max"])
                },
                "active": True, 
                "deleted": False,
                "start_date": {
                    "$lte": start_date
                },
                "end_date": {
                    "$gte": end_date
                }       
            }
        }
    ]


    listings = listingCollection.aggregate(query)

    location = getGPS(zip)

    decoded_listings = list()

    if listings != None:
        async for listing in listings:

            listing["distance"] = format(distance.great_circle((listing["locationLAT"], listing["locationLONG"]), (float(location.latitude), float(location.longitude))).miles, '.2f')
            

            if float(listing["distance"]) <= float(filters["distance"]):
                decoded_listings.append(decode_sortedbson(listing,ListingResponseModel.get_keys()))
                    #Had to make a custom model to append the distance
    return decoded_listings


    

async def get_listings_sorted(category: str, filters: dict, sort: str, zip: str):

    listings = await get_filtered_listings(category, filters, zip)

    
    if sort == "None": 
        return listings

    elif sort == "distance":
        return sorted(listings, key = lambda listing: float(listing["distance"]))

    elif sort == "priceLowToHigh":
        return sorted(listings, key = lambda listing: float(listing["item_price"]))

    elif sort == "priceHighToLow":
        return sorted(listings, key= lambda listing: float(listing["item_price"]), reverse=True)



