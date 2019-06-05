from authlib.specs.rfc6749.grants import (
    ResourceOwnerPasswordCredentialsGrant as _PasswordGrant
)

from strongr.core.gateways import Gateways
from strongr.restdomain.model.oauth2 import User, Token


class PasswordGrant(_PasswordGrant):
    def authenticate_user(self, username, password):
        user = User.query.filter_by(username=username).first()
        if user.check_password(password):
            return user

    def create_access_token(self, token, client, user, **kwargs):
        item = Token(
            client_id=client.client_id,
            user_id=user.user_id,
            **token
        )
        session = Gateways.sqlalchemy_session()
        session.add(item)
        session.commit()
