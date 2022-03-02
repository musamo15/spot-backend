from fastapi import APIRouter,Request,Response,Depends,status
from fastapi.security import HTTPBearer
from typing import Union,List
from app.db.requestModels import ListingRequestModel
from app.db.responseModels import ListingResponseModel, UserResponseModel
from app.db.crud import (create_listing,get_listing, get_user, modify_listing,delete_listing,get_all_listings)
from app.core.utils import VerifyToken


rout = APIRouter()
# Scheme for the Authorization header, lets us require an authentication token for a route
token_auth_scheme = HTTPBearer()


@rout.get("/")
async def root():
    return {"SPOT RENTAL Platform" : "Welcome to our page!!"}

@rout.get("/private")
async def private_route(response : Response, token: str = Depends(token_auth_scheme)):
    result = VerifyToken(token.credentials).verify()
    
    if result.get(status):
        response.status_code = status.HTTP_400_BAD_REQUEST
       
    return result


"""
    LISTINGS
"""
@rout.get("/getListing", response_model= ListingResponseModel)
async def user_get_listing(listingId: str,category: str):
    return  await get_listing(listingId,category)

@rout.get("/getAllListings",response_model=List[ListingResponseModel])
async def user_get_all_listings(category: str):
    return await get_all_listings(category)

@rout.post("/createListing",response_model=ListingResponseModel)
async def user_create_listing(listing:ListingRequestModel):
   return await create_listing(listing)

@rout.put("/modifyListing",response_model=ListingResponseModel)
async def user_modify_listing(listingId: str, listing:ListingRequestModel):
    validListing = {key: value for key, value in listing.dict().items() if value != ""}
    
    return await modify_listing(listingId,validListing)

@rout.delete("/deleteListing")
async def user_delete_listing(listingId: str, category: str):
   return await delete_listing(listingId,category)





"""
    Users
"""
@rout.get("/getUser", response_model = UserResponseModel)
async def user_get_user(userId: str):
    return await get_user(userId)
