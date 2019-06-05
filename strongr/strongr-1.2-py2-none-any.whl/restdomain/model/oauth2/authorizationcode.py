from authlib.flask.oauth2.sqla import OAuth2AuthorizationCodeMixin

from strongr.core import gateways

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from strongr.core.sqlalchemydatatypes.uuidtype import UUIDType

Base = gateways.Gateways.sqlalchemy_base()

class AuthorizationCode(Base, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth_auth_code'

    authorizationcode_id = Column(Integer, primary_key=True)
    user_id = Column(String(64), ForeignKey('oauth_users.user_id', ondelete='CASCADE'))
