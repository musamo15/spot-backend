from pydantic import BaseModel, Field
from .genericModels import *

class AddressModel(BaseModel):
    street: str = Field(...)
    city: str = Field(...)
    zip: str = Field(...)
    state: str = Field(...)
    

class ListingRequestModel(ListingModel):
    address : AddressModel = Field(...)
    