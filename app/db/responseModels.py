from typing import Optional, Union,List
from pydantic import BaseModel, Field

from .requestModels import ListingRequestModel

from app.db.genericModels import *

class ListingResponseModel(ListingModel):
    listing_id: str = Field(...)
    rentals: List[RentalsModel] = Field(...)

    
    
   
 