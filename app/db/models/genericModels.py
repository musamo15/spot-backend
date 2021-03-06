from pydantic import BaseModel, Field
from typing import Optional,List
from datetime import datetime

class ListingModel(BaseModel):
    # Field(...) means the field is required
    # Union lets u specify multiple types, but matches by the order of types within the list
    host_id: str = Field(...)
    category: str = Field(...)
    item_name: str = Field(...)
    item_price: float = Field(...)
    start_date: datetime = Field(...)
    end_date: datetime = Field(...)
    attributes: dict = Field(...)
    images: List[str] = Field(...)
    
    @staticmethod
    def get_keys():
        return list(('host_id','category','item_name','item_price','start_date','end_date','attributes','distance','images'))

class RentalsModel(BaseModel):
    host_id: str = Field(...)
    leasse_id: str = Field(...)
    start_date: datetime = Field(...)
    end_date: datetime = Field(...)

class AddressModel(BaseModel):
    street1: str = Field(...)
    street2: Optional[str]
    city: str = Field(...)
    state: str = Field(...)
    zip: str = Field(...)
    country: str = Field(...)
     