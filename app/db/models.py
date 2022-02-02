from lib2to3.pytree import Base
import uuid
from typing import Optional
from pydantic import BaseModel, Field


# class Address(BaseModel):
#     street: str
#     city: str
#     state: str
#     zip: str

class UserModel(BaseModel):
    # id: str = Field(default_factory=uuid.uuid4, alias="_id")
    first_name: str
    last_name: str
    email: str
    phone_number: str
    address: str

    class Config:
        allow_extra = True
        arbitrary_types_allowed = True
        
        
class TestModel(BaseModel):
    test: str
        

