import jwt
from decouple import config
from fastapi import HTTPException
from http import HTTPStatus
from datetime import datetime

from app.db.models import *


def decode_bson(document, model):
    listing_id = str(document["_id"])
    document["listing_id"] = listing_id
    listing = model.parse_obj(document)

    return listing

def listing_active(start_date, end_date):
    current = datetime.today().date()
    start = start_date.date()
    end = end_date.date()
    
    return current <= start <= end

class VerifyToken():
    """ Verifies the JWT (JSON Web Token) using PyJWT"""

    def __init__(self, token):
        self.token = token
        self.config = {
            "DOMAIN": config("DOMAIN"),
            "API_AUDIENCE": config("API_AUDIENCE")
        }

        # Returns the json web key set from auth0 domain
        jwks_url = f'https://{self.config["DOMAIN"]}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self):
        try:
            # Signing key
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(
                self.token
            ).key
        except (jwt.exceptions.PyJWKClientError, jwt.exceptions.DecodeError) as error:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail=str(error))
        try:
            header_data = jwt.get_unverified_header(self.token)
            # Decode JWT Token
            payload = jwt.decode(jwt=self.token, key=self.signing_key, algorithms=[
                                 header_data['alg'], ], audience=self.config["API_AUDIENCE"],)
        except Exception as exception:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail=str(exception))

        return payload
