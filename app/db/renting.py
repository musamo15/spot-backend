from fastapi import HTTPException
from http import HTTPStatus
from bson.objectid import ObjectId
from app.db.models.responseModels import *

from datetime import datetime

from app.db.database import (listingsCollections)
from app.db.listings import *
from app.utils.utilities import *
from twilio.rest import Client
from app.db.users import get_user_data
from datetime import datetime



twilio = Client(config("TWILIO_ACCOUNT_SID"), config("TWILIO_KEY"))



async def add_rental(listing_id, lessee_id, category: str, start_date, end_date):

    listing = await get_listing(listing_id, category)

    listingCollection = listingsCollections.get(category)

    objectId = ObjectId(listing_id)


    listing = listing.dict()

    if not listing["active"] or listing["deleted"]:
                raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="Listing no longer available")



    if listing["host_id"] == lessee_id:
        raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="You can't rent your own item!")


    rentalDict = RentalsModel(host_id = listing["host_id"],
    leasse_id = lessee_id,
    start_date = start_date,
    end_date = end_date)

    listing["rentals"].append(rentalDict.dict())


    await listingCollection.update_one({"_id": objectId}, {"$set": {"rentals": listing["rentals"]}})

    updated_listing = await listingCollection.find_one({"_id": objectId})


    try:
        lessee = (await get_user_data(lessee_id)).dict()
        host = (await get_user_data(listing["host_id"])).dict()
        
    except Exception:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="Invalid User Id")


    if host["phone"] != "" and lessee["phone"] != "":
        
        #Message to buyer
        message = twilio.messages.create(
            body = ("You have successfully submitted a rental for item: " + listing["item_name"] + " \nfrom: " + start_date[0:10] + " \nto: " + end_date[0:10]),
            from_ = '+16067280487',
            to=lessee["phone"])

        #Message to seller

        message = twilio.messages.create(
            body = ("Your item \"" + listing["item_name"] + "\" has been rented \nfrom: " + start_date[0:10] + " \nto: " + end_date[0:10]),
            from_ = '+16067280487',
            to=host["phone"])
        





    


    return decode_bson(updated_listing, ListingResponseModel)
