from pydantic import BaseModel, Field
from app.db.models.genericModels import *


class ListingRequestModel(ListingModel):
    address : AddressModel = Field(...)
    