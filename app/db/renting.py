from fastapi import HTTPException
from http import HTTPStatus
from bson.objectid import ObjectId
from app.db.models.responseModels import *

from app.db.database import (listingsCollections)
from app.db.listings import *
from app.utils.utilities import *
from twilio.rest import Client
from app.db.users import get_user
from datetime import datetime

twilio = Client(config("TWILIO_ACCOUNT_SID"), config("TWILIO_KEY"))


async def add_rental(listing_id, lessee_id, category: str, start_date, end_date):

    listing = await get_listing(listing_id, category)

    listing = listing.dict()

    # Validate listing availability
    try:
        if not listing_active(start_date, end_date, listing['start_date'].date()):
            raise Exception
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Invalid Rental Days")

    listingCollection = listingsCollections.get(category)

    objectId = ObjectId(listing_id)

    if not listing["active"] or listing["deleted"]:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Listing no longer available")

    if listing["host_id"] == lessee_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="You can't rent your own item!")

    try:
        lessee = dict(**await get_user(lessee_id))["user_metadata"]
        host = dict(**await get_user(listing["host_id"]))["user_metadata"]
    except Exception:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="Invalid User Id")

    rentalDict = RentalsModel(host_id=listing["host_id"],
                              leasse_id=lessee_id,
                              start_date=start_date,
                              end_date=end_date)

    listing["rentals"].append(rentalDict.dict())

    await listingCollection.update_one({"_id": objectId}, {"$set": {"rentals": listing["rentals"]}})

    updated_listing = await listingCollection.find_one({"_id": objectId})

    if "phone" in host and host["phone"] != "" and "phone" in lessee and lessee["phone"] != "":
        try:
            # Message to buyer
            twilio.messages.create(
                body=("You have successfully submitted a rental for item: " +
                      listing["item_name"] + " \nfrom: " + start_date.strftime("%d/%m/%Y") + " \nto: " + end_date.strftime("%d/%m/%Y")),
                from_='+16067280487',
                to=lessee["phone"])

            # Message to seller
            twilio.messages.create(
                body=("Your item \"" + listing["item_name"] + "\" has been rented \nfrom: " +
                      start_date.strftime("%d/%m/%Y") + " \nto: " + end_date.strftime("%d/%m/%Y")),
                from_='+16067280487',
                to=host["phone"])
        except:
            pass

    return decode_bson(updated_listing, ListingResponseModel)
