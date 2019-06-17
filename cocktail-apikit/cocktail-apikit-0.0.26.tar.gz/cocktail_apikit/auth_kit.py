import base64
import time
from typing import Optional

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_der_public_key

from cocktail_apikit import Authentication, request


class JwtAuthentication(Authentication):

    def __init__(self, jwks_url: str = None, issuer: str = None, jwks_reload_seconds: int = 300, **kwargs):
        self.jwks_url = jwks_url
        self.issuer = issuer
        self.__jwk = kwargs
        self.__jwks = None
        self.jwks_reload_seconds = jwks_reload_seconds
        self.jwks_loaded_at = 0

    def is_authenticated(self, *args, **kwargs):
        auth_header: str = request.headers.get('authorization')
        if not auth_header:
            return False
        token = auth_header.split(' ', 1)[-1]
        data = self.extract_credential(token)
        if not data:
            return False
        if self.issuer and self.issuer != data.get('iss'):
            return False
        if isinstance(data.get('exp'), (int, float)) and data['exp'] < time.time():
            return False
        request.user = data
        return True

    # pylint: disable=arguments-differ
    def extract_credential(self, token) -> Optional[dict]:
        data = self.__get_data(token=token, jwk=self.__jwk)
        if not data and self.__jwks:
            data = self.__get_data_from_jwks(self.__jwks, token)
        if data or not self.jwks_url:
            return data
        if time.time() - self.jwks_loaded_at < self.jwks_reload_seconds:
            return None
        try:
            jwks = requests.get(self.jwks_url).json()
            data = self.__get_data_from_jwks(jwks, token, set_jwk=True)
            if data:
                self.__jwks = jwks
                return data
        except Exception:
            return None
        finally:
            self.jwks_loaded_at = time.time()

    def __get_data_from_jwks(self, jwks, token: str, set_jwk: bool = False) -> Optional[dict]:
        for jwk in jwks['keys']:
            data = self.__get_data(token=token, jwk=jwk)
            if data:
                if set_jwk:
                    self.__jwk = jwk
                return data
        return None

    def __get_data(self, token: str, jwk: dict) -> Optional[dict]:
        if not jwk or not jwk.get('alg'):
            return None
        if jwk.get('key'):
            try:
                return jwt.decode(token, key=jwk['key'], algorithms=[jwk['alg']])
            except Exception:
                return None
        for x5c in jwk.get('x5c', []):
            key = base64.b64decode(x5c)
            if jwk['alg'].startswith('RS'):
                key = load_der_public_key(key, default_backend())
            try:
                data = jwt.decode(token, key=key, algorithms=[jwk['alg']])
                if data:
                    jwk['key'] = key
                    return data
            except Exception:
                pass
        return None
