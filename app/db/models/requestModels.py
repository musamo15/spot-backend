from pydantic import BaseModel, Field
from app.db.models.genericModels import *

class AddressModel(BaseModel):
    street: str = Field(...)
    city: str = Field(...)
    zip: str = Field(...)
    state: str = Field(...)
    

class ListingRequestModel(ListingModel):
    address : AddressModel = Field(...)
    