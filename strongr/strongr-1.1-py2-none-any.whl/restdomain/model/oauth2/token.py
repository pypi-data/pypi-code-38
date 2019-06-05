import strongr.core.gateways as gateways
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from authlib.flask.oauth2.sqla import OAuth2TokenMixin

from strongr.core.sqlalchemydatatypes.uuidtype import UUIDType

Base = gateways.Gateways.sqlalchemy_base()

class Token(Base, OAuth2TokenMixin):
    __tablename__ = 'oauth_token'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(64), ForeignKey('oauth_users.user_id', ondelete='CASCADE'))
