from authlib.specs.rfc7009 import RevocationEndpoint as _RevocationEndpoint

from strongr.core.gateways import Gateways
from strongr.restdomain.model.oauth2 import Token


class RevocationEndpoint(_RevocationEndpoint):
    def query_token(self, token, token_type_hint, client):
        q = Token.query.filter_by(client_id=client.client_id)
        if token_type_hint == 'access_token':
            return q.filter_by(access_token=token).first()
        elif token_type_hint == 'refresh_token':
            return q.filter_by(refresh_token=token).first()
        # without token_type_hint
        item = q.filter_by(access_token=token).first()
        if item:
            return item
        return q.filter_by(refresh_token=token).first()

    def invalidate_token(self, token):
        session = Gateways.sqlalchemy_session()
        session.delete(token)
        session.commit()
