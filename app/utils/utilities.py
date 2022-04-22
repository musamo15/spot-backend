import jwt
from decouple import config
from fastapi import HTTPException
from http import HTTPStatus
from datetime import datetime
from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
from auth0.v3.management import Users

from app.db.models import *


def decode_bson(document, model):
    listing_id = str(document["_id"])
    document["listing_id"] = listing_id
    listing = model.parse_obj(document)

    return listing

def decode_sortedbson(document,keys):
    newDict = dict()
    newDict["listing_id"] = str(document["_id"])
    
    for key in keys:
        newDict[key] = document[key]

    return newDict

def listing_active(start_date, end_date):
    current = datetime.today().date()
    start = start_date.date()
    end = end_date.date()

    return current <= start <= end

def get_users_api():
    token = __generate_mgmt_token__()
    return Users(config("DOMAIN"), token)


def __generate_mgmt_token__():
    domain = config("DOMAIN")
    client_id = config("CLIENT_ID")
    client_secret = config("CLIENT_SECRET")

    # Returns the token based on the domain, (Could be multiple tokens)
    get_token = GetToken(domain)

    # Uses the client id and secret to retrieve the associated token
    token = get_token.client_credentials(client_id,
                                        client_secret, 'https://{}/api/v2/'.format(domain))

    mgm_api_token = token['access_token']
    
    return mgm_api_token


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
