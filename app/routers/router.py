from fastapi import APIRouter,Depends
from fastapi.security import HTTPBearer
from typing import List
from app.db.models.requestModels import ListingRequestModel
from app.db.models.responseModels import ListingResponseModel
from app.db.database import (get_all_categories)
from app.db.listings import (create_listing,get_listing, modify_listing,delete_listing,get_all_listings,get_listing_item_from_query)
from app.utilities.utilities import VerifyToken


rout = APIRouter()
# Scheme for the Authorization header, lets us require an authentication token for a route
token_auth_scheme = HTTPBearer()

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

   
