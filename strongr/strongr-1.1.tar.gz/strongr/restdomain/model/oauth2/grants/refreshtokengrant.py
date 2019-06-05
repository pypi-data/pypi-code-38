from authlib.specs.rfc6749.grants import (
    RefreshTokenGrant as _RefreshTokenGrant
)

from strongr.core.gateways import Gateways
from strongr.restdomain.model.oauth2 import Token


class RefreshTokenGrant(_RefreshTokenGrant):
    def authenticate_token(self, refresh_token):
        item = Token.query.filter_by(refresh_token=refresh_token).first()
        # define is_refresh_token_expired by yourself
        if item and not item.is_refresh_token_expired():
            return item

    def create_access_token(self, token, authenticated_token):
        # issue a new token to replace the old one, you can also update
        # the ``authenticated_token`` instead of issuing a new one
        item = Token(
            client_id=authenticated_token.client_id,
            user_id=authenticated_token.user_id,
            **token
        )
        session = Gateways.sqlalchemy_session()
        session.add(item)
        session.delete(authenticated_token)
        session.commit()
