import uuid

from sqlalchemy.orm import synonym

import strongr.core.gateways as gateways
from sqlalchemy import Column, String

from strongr.core.sqlalchemydatatypes.uuidtype import UUIDType
import strongr.restdomain.model.gateways

Base = gateways.Gateways.sqlalchemy_base()

class User(Base):
    __tablename__ = 'oauth_users'

    user_id = Column(String(64), primary_key=True, nullable=False, default=uuid.uuid4)
    username = Column(String(64), nullable=False)
    _password = Column('password', String(93)) # werkzeug generate_password_hash method='pbkdf2:sha256:80000' == 93 chars
    email = Column(String(250), nullable=False)

    @property
    def password(self):
        return self._password

    # update password-field using proper hash function
    @password.setter
    def password(self, value):
        self._password = strongr.restdomain.model.gateways.Gateways.generate_password_hash(password=value)

    def check_password(self, password):
        return strongr.restdomain.model.gateways.Gateways.check_password_hash(pwhash=self.password, password=password)


    # create a synonym so that _password and password are considered the same field by the mapper
    password = synonym('_password', descriptor=password)
