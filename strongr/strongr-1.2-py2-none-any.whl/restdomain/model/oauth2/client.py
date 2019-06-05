from sqlalchemy.orm import relationship

import strongr.core.gateways as gateways
from sqlalchemy import Column, ForeignKey, Integer, String

from authlib.flask.oauth2.sqla import OAuth2ClientMixin

from strongr.core.sqlalchemydatatypes.uuidtype import UUIDType

Base = gateways.Gateways.sqlalchemy_base()

class Client(Base, OAuth2ClientMixin):
    __tablename__ = 'oauth_client'

    id = Column(Integer, primary_key=True) # client_id is provided by authlib, can't use it here
    user_id = Column(String(64), ForeignKey('oauth_users.user_id', ondelete='CASCADE'))

    @classmethod
    def get_by_client_id(cls, client_id): # this method in OAuth2ClientMixin is bugged in authlib, thus we must patch it
        client = gateways.Gateways.sqlalchemy_session().query(Client).filter_by(client_id=client_id).first()
        return client

