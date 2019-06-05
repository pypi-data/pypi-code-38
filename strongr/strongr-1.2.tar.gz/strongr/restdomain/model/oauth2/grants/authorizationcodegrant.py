from authlib.specs.rfc6749.grants import (
    AuthorizationCodeGrant as _AuthorizationCodeGrant
)
from authlib.common.security import generate_token

from strongr.core.gateways import Gateways
from strongr.restdomain.model.oauth2 import Token
from strongr.restdomain.model.oauth2.authorizationcode import AuthorizationCode


class AuthorizationCode(_AuthorizationCodeGrant):
    def create_authorization_code(self, client, grant_user, **kwargs):
        # you can use other method to generate this code
        code = generate_token(48)
        item = AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=kwargs.get('redirect_uri', ''),
            scope=kwargs.get('scope', ''),
            user_id=grant_user,
        )
        session = Gateways.sqlalchemy_session()
        session.add(item)
        session.commit()
        return code

    def parse_authorization_code(self, code, client):
        item = AuthorizationCode.query.filter_by(
            code=code, client_id=client.client_id).first()
        if item and not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        session = Gateways.sqlalchemy_session()
        session.delete(authorization_code)
        session.commit()

    def create_access_token(self, token, client, authorization_code):
        item = Token(
            client_id=client.client_id,
            user_id=authorization_code.user_id,
            **token
        )
        session = Gateways.sqlalchemy_session()
        session.add(item)
        session.commit()
        # we can add more data into token
        token['user_id'] = authorization_code.user_id
