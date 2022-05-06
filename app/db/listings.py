from fastapi import HTTPException
from http import HTTPStatus
from bson.objectid import ObjectId

from app.db.models.responseModels import ListingResponseModel
from app.db.models.requestModels import ListingRequestModel, AddressModel
from app.utils.utilities import (decode_bson, listing_active)
from app.db.database import (listingsCollections)


async def create_listing(listing: ListingRequestModel):
    updatedListing = listing.dict()

    # determine category
    listingCollection = listingsCollections.get(updatedListing["category"])

    if listingCollection == None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="Invalid Category")

    # Check if listing exists
    found_listing = await listingCollection.find_one(updatedListing)

    if found_listing != None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="Listing already exists")

    # Inserting GPS cords into the dict

    # **********************Commented out to not spam API calls for google maps UNCOMMENT FOR FINAL PRODCUT THANK YOU********************

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

    # Add active
    updatedListing["active"] = listing_active(
        updatedListing.get("start_date"), updatedListing.get("end_date")
    )

    # Add deleted
    updatedListing["deleted"] = False

    # Insert listing onto db
    newListing = await listingCollection.insert_one(updatedListing)

    # Find the new listing in the db
    createdListing = await listingCollection.find_one({"_id": newListing.inserted_id})

    # Decode the listing to a dict
    decodedListing = decode_bson(
        createdListing, ListingResponseModel)

    return decodedListing


async def get_listing(listingId: str, category: str):
    # validate listing id input
    try:
        objectId = ObjectId(listingId)
    except Exception:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="Invalid Listing Id")

    # Check if category is valid
    listingCollection = listingsCollections.get(category)

    if listingCollection == None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="Invalid category")

    # Find the listing in the db
    listing = await listingCollection.find_one({"_id": objectId})

    if listing == None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="Listing does not exist")

    # Decode the listing to a dict
    decodedListing = decode_bson(listing, ListingResponseModel)
    return decodedListing


async def modify_listing(listingId: str, category: str, listing: dict):
    # If there are no none values withing the listing
    if len(listing) >= 1:
        try:
            objectId = ObjectId(listingId)
        except Exception:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="Invalid Listing Id")

        listingCollection = listingsCollections.get(category)


        # Find the listing in the db
        found_listing = await listingCollection.find_one({"_id": objectId})
        if found_listing != None:

            # Updating listing address and gps coordinates

            if("address" in listing):

                addressModel = AddressModel.parse_obj(listing["address"])

                # UNCOMMENT THIS WHEN FINAL PRODCUT OKAY
                # CURRENTLY JUST COORDS FOR THE WHITE HOUSE SO WE DONT SPAM GOOGLE API THANK YOU

                # location = getGPS(addressModel)

                # listing["locationLONG"] = location.longitude
                # listing["locationLAT"] = location.latitude

                listing["locationLONG"] = -77.036560
                listing["locationLAT"] = 38.897957
                # Remove address from dict
                listing.pop('address')

            await listingCollection.update_one({"_id": objectId}, {"$set": listing})

            updated_listing = await listingCollection.find_one({"_id": objectId})
            return decode_bson(updated_listing, ListingResponseModel)
        else:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="Listing does not exist")
    else:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="No Modifications")


async def delete_listing(listingId: str, category: str):
    try:
        objectId = ObjectId(listingId)
    except Exception:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="Invalid Listing Id")

    # Check if category is valid
    listingCollection = listingsCollections.get(category)

    if listingCollection == None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="Invalid category")

    found_listing = await listingCollection.find_one({"_id": objectId})

    if found_listing != None:
        deleteListing = {
            "active": "false",
            "deleted": "true"
        }
        try:
            await listingCollection.update_one({"_id": objectId}, {"$set": deleteListing})
            return {"message": "Successfully deleted listing"}
        except Exception:
            raise HTTPException(status_code=HTTPStatus.OK,
                                detail="Unable to delete listing")
    else:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="Listing Id Not Found")


async def get_all_listings(category: str, limit=50):

    # Check if category is valid
    listingCollection = listingsCollections.get(category)

    if listingCollection == None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="Invalid category")

    listings = listingCollection.find().limit(limit)


    decoded_listings = list()
    if listings != None:
        async for listing in listings:
            decoded_listings.append(decode_bson(
                listing, ListingResponseModel))

    return decoded_listings


async def get_listing_item_from_query(query: str):
    setListings = set()

    for category in listingsCollections:
        setListings = setListings.union(await get_matching_items(query, listingsCollections.get(category)))

    return setListings


async def get_matching_items(query: str, collection, limit=50):

    # Searches through the specified collection looking for items that match the following regex -> .*{item_name}.* (case insensitive)
    foundListings = collection.find(
        {"item_name": {'$regex': '.*{}.*'.format(query), '$options': 'i'}, "active": True, "deleted": False}).limit(limit)

    decoded_listings = list()
    async for listing in foundListings:
        decoded_listings.append(decode_bson(
            listing, ListingResponseModel))

    return decoded_listings


async def get_user_listings(user_id: str,limit=50):
    setListings = set()

    for category in listingsCollections:
        listings = listingsCollections.get(category).find({"host_id": user_id}).limit(limit)
        decoded_listings = list()
        async for listing in listings:
           
            decoded_listings.append(decode_bson(
            listing, ListingResponseModel))
        
        setListings = setListings.union(decoded_listings)
    return setListings

async def get_user_rentals(user_id: str,limit=50):
    setListings = set()

    for category in listingsCollections:
        listings = listingsCollections.get(category).find({"rentals.leasse_id": user_id}).limit(limit)
        decoded_listings = list()
        async for listing in listings:
           
            decoded_listings.append(decode_bson(
            listing, ListingResponseModel))
        
        setListings = setListings.union(decoded_listings)
    return setListings