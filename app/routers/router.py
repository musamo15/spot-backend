from datetime import date
from fastapi import APIRouter, Depends, UploadFile
from fastapi.security import HTTPBearer
from typing import List
from decouple import config
import boto3
import botocore
import uuid

from app.db.models.requestModels import ListingRequestModel
from app.db.models.responseModels import ListingResponseModel
from app.db.database import (get_all_categories)
from app.db.listings import (create_listing,get_listing, modify_listing,delete_listing,get_all_listings,get_listing_item_from_query)
from app.db.users import (get_user_data,update_user_data)
from app.utils.utilities import (VerifyToken)
from app.db.sorting import *
from app.db.renting import *


rout = APIRouter()
# Scheme for the Authorization header, lets us require an authentication token for a route
token_auth_scheme = HTTPBearer()

"""
    Users
"""
@rout.get("/users/{user_id}")
async def user_get_user_data(user_id: str, token: str = Depends(token_auth_scheme)):
    VerifyToken(token.credentials).verify()
    return await get_user_data(user_id)

@rout.put("/users/{users_id}")
async def user_update_user_data(users_id: str, updated_data: dict ,token: str = Depends(token_auth_scheme)):
    VerifyToken(token.credentials).verify()
    return await update_user_data(users_id,updated_data)

"""
    Categories
"""
@rout.get("/categories", response_model = List[str])
async def user_get_categories():
    return await get_all_categories()

"""
    LISTINGS
"""
@rout.get("/listings/{listing_id}", response_model= ListingResponseModel)
async def user_get_listing(listing_id,category: str):
    return await get_listing(listing_id,category)

@rout.put("/listingsSorted")
async def user_get_listings_sorted(category: str, filters: dict, sortedOn: str, zip):
    return await get_listings_sorted(category, filters, sortedOn, zip)

@rout.get("/listings",response_model=List[ListingResponseModel])
async def user_get_all_listings(category: str):
    return await get_all_listings(category)

# Search query
@rout.get("/search",response_model=List[ListingResponseModel])
async def user_get_listing_item_from_query(query: str):
    return await get_listing_item_from_query(query)

@rout.post("/listings",response_model=ListingResponseModel)
async def user_create_listing(listing:ListingRequestModel, token: str = Depends(token_auth_scheme)):
   VerifyToken(token.credentials).verify()
   return await create_listing(listing)

@rout.put("/listings/{listing_id}",response_model=ListingResponseModel)
async def user_modify_listing(listing_id, category: str, modifiedListing: dict,token: str = Depends(token_auth_scheme)):
    VerifyToken(token.credentials).verify()
    validListing = {key: value for key, value in modifiedListing.items() if value != ""}
    return await modify_listing(listing_id,category,validListing)

@rout.delete("/listings/{listing_id}", response_model=dict)
async def user_delete_listing(listing_id, category: str, token: str = Depends(token_auth_scheme)):
   VerifyToken(token.credentials).verify()
   return await delete_listing(listing_id,category)


@rout.put("/listings/{listing_id}/rent")
async def user_rent_listing(listing_id, lessee_id, category: str, start_date: datetime, end_date: datetime, token: str = Depends(token_auth_scheme)):
    VerifyToken(token.credentials).verify()
    return await add_rental(listing_id, lessee_id, category, start_date, end_date)
"""
    IMAGES
"""
s3_client = boto3.client('s3',
    aws_access_key_id=config("AWS_ACCESS_KEY"),
    aws_secret_access_key=config("AWS_SECRET_KEY")
)


@rout.post("/images")
async def upload_images(files: List[UploadFile], token: str = Depends(token_auth_scheme)):
    VerifyToken(token.credentials).verify()
    urls = []
    try:
        for file in files:
            ext = file.content_type.split("/")[-1]
            key = str(uuid.uuid4()) + "." + ext
            s3_client.upload_fileobj(file.file, "spotimagestorage", key)
            urls.append("https://spotimagestorage.s3.us-east-1.amazonaws.com/" + key)
    except botocore.exceptions.ClientError as e:
        print(e)
    return {"urls": urls}
