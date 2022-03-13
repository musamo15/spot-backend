
import jwt
from decouple import config

def set_up():
    """ Sets up the configuration for the app"""
    conf = {
        "DOMAIN": config("DOMAIN"),
        "API_AUDIENCE": config("API_AUDIENCE"),
        "ISSUER": config("ISSUER"),
        "ALGORITHMS": config("ALGORITHMS")
    }
    return conf


class VerifyToken():
    """ Verifies the JWT (JSON Web Token) using PyJWT"""
    
    def __init__(self,token,permissions=None,scopes=None):
        self.token = token
        self.permissions = permissions
        self.scopes = scopes
        self.config = set_up()
        
        # Returns the json web key set from auth0 domain
        jwks_url = f'https://{self.config["DOMAIN"]}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)
    
    def verify(self):
        
        try:
            # Signing key
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(
                self.token
            ).key
        except (jwt.exceptions.PyJWKClientError,jwt.exceptions.DecodeError)  as error:
            return {"status":"error","msg":str(error)}
        
        try:
            # Decode JWT Token
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=self.config["ALGORITHMS"],
                audience=self.config["API_AUDIENCE"],
                issuer=self.config["ISSUER"])
        except Exception as exception:
            return {"status":"error","message":str(exception)}

        
        if self.scopes:
            result = self._check_claims(payload,'scope',str,self.scopes.split(' '))
            if result.get("error"):
                return result
        
        if self.permissions:
            result = self._check_claims(payload,'permissions',list,self.permissions)
            if result.get("error"):
                return result

        return payload
    def _check_claims(self, payload, claim_name, claim_type, expected_value):

        instance_check = isinstance(payload[claim_name], claim_type)
        result = {"status": "success", "status_code": 200}

        payload_claim = payload[claim_name]

        if claim_name not in payload or not instance_check:
            result["status"] = "error"
            result["status_code"] = 400

            result["code"] = f"missing_{claim_name}"
            result["msg"] = f"No claim '{claim_name}' found in token."
            return result

        if claim_name == 'scope':
            payload_claim = payload[claim_name].split(' ')

        for value in expected_value:
            if value not in payload_claim:
                result["status"] = "error"
                result["status_code"] = 403

                result["code"] = f"insufficient_{claim_name}"
                result["msg"] = (f"Insufficient {claim_name} ({value}). You "
                                  "don't have access to this resource")
                return result
        return result
