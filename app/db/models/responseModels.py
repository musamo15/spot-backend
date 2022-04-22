from typing import List
from pydantic import Field

from app.db.models.genericModels import *

class ListingResponseModel(ListingModel):
    listing_id: str = Field(...)
    rentals: List[RentalsModel] = Field(...)
    locationLONG: str = Field(...)
    locationLAT: str = Field(...)
    active: bool = Field(...)
    deleted: bool = Field(...)
    
    def __eq__(self, other):
        return self.listing_id == other.listing_id
    
    def __hash__(self) -> int:
        return hash(self.listing_id)

class UsersModel(BaseModel):
    name: str = Field(...)
    email: str = Field(...)
    phone: str = Field(...)
    nickname: str = Field(...)
    picture: str = Field(...)
    address: AddressModel = Field(...) 
    listings: List[ListingResponseModel] = Field(...)
    rentals: List[ListingResponseModel] = Field(...)
    
    @staticmethod
    def get_meta_data_keys():
        return list(('address','phone',))