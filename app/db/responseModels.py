from typing import Optional, Union,List
from pydantic import BaseModel, Field

from .requestModels import ListingRequestModel, UserModel

from app.db.genericModels import *

class ListingResponseModel(ListingModel):
    listing_id: str = Field(...)
    rentals: List[RentalsModel] = Field(...)
    locationLONG: str = Field(...)
    locationLAT: str = Field(...)
    
    @staticmethod
    def get_keys():
        additionalKeys = list(('rentals','locationLONG','locationLAT'))
        
        for key in ListingModel.get_keys():
            additionalKeys.append(key)
        
        return additionalKeys
    



class UserResponseModel(UserModel):
    user_id: str = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    email: str = Field(...)
    phone_number: str = Field(...)
 