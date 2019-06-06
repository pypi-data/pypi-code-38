import logging

import enum
from requests.auth import HTTPBasicAuth

AUTHORIZATION_HEADER = 'Authorization'


class AuthType(enum.Enum):
    """The enumeration of supported OAuth2 Authorization Types"""
    CLIENT_GRANT = 1
    NO_AUTH = 2
    BYO_TOKEN = 3


class Auth(object):
    """Provides authentication logic for Sequoia API requests, support
    potentially a range of authentication schemes depending upon the
    provided credentials."""

    def __init__(self, grant_client_id=None, grant_client_secret=None, auth_type=AuthType.CLIENT_GRANT, byo_token=None):
        if auth_type == AuthType.CLIENT_GRANT and grant_client_id is not None and grant_client_secret is not None:
            logging.debug('Client credential grant scheme used')
            self.grant_client_id = grant_client_id
            self.grant_client_secret = grant_client_secret
            self.auth_style = AuthType.CLIENT_GRANT
            self.auth = HTTPBasicAuth(
                self.grant_client_id, self.grant_client_secret)
        elif auth_type == AuthType.NO_AUTH:
            logging.debug('No auth schema used')
            self.auth_style = AuthType.NO_AUTH
            self.auth = None
        elif auth_type == AuthType.BYO_TOKEN:
            logging.debug('BYO token scheme used')
            self.auth_style = AuthType.BYO_TOKEN
            self.auth = byo_token
        else:
            raise ValueError('No valid authentication sources found')

    def __call__(self, r):
        """
        Intercept the request and apply any custom logic to the request.
        Useful for applying custom authorization logic such as HMACs.

        :param r: the request
        :return: the updated request
        """
        return r
