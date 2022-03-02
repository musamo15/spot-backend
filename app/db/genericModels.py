from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime

class ListingModel(BaseModel):
    # Field(...) means the field is required
    # Union lets u specify multiple types, but matches by the order of types within the list
    host_id: str = Field(...)
    category: str = Field(...)
    start_date: datetime = Field(...)
    end_date: datetime = Field(...)
    attributes: dict = Field(...)
    
    @staticmethod
    def get_keys():
        return list(('host_id','category','start_date','end_date','attributes'))

class RentalsModel(BaseModel):
    host_id: str = Field(...)
    leasse_id: str = Field(...)
    start_date: datetime = Field(...)
    end_date: datetime = Field(...)
    


class UserModel(BaseModel):
    user_id: str = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    email: str = Field(...)
    phone_number: str = Field(...)
    #Address?


    @staticmethod
    def get_keys():
        return list(('first_name','last_name','email','phone_number'))