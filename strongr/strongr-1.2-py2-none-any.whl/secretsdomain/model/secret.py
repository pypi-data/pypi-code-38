import strongr.core.gateways as gateways
from sqlalchemy import Column, String

from strongr.core.sqlalchemydatatypes.uuidtype import UUIDType

import uuid

Base = gateways.Gateways.sqlalchemy_base()

class Secret(Base):
    __tablename__ = 'secrets'

    secret_id = Column(UUIDType, default=uuid.uuid4, primary_key=True)
    key = Column(String(512), unique=True)
    value = Column(String(2048))
