from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import UUIDType, JSONType
from sqlalchemy import Column, DateTime, Unicode, BigInteger, Integer
from sqlalchemy.sql import func
from sqlalchemy.dialects import sqlite, postgresql
from sqlalchemy.orm.attributes import flag_modified

BigIntegerType = BigInteger()
BigIntegerType = BigIntegerType.with_variant(postgresql.BIGINT(), 'postgresql')
BigIntegerType = BigIntegerType.with_variant(sqlite.INTEGER(), 'sqlite')

DeclarativeBase = declarative_base()
PkType = BigIntegerType
ExtPkType = UUIDType(binary=False)

import uuid

class Base(DeclarativeBase):

    __abstract__ = True

    id = Column(PkType, primary_key=True)
    ext_id = Column(ExtPkType, default=lambda : uuid.uuid4(), nullable=False, unique=True)
    created_at = Column(DateTime,
                        server_default=func.now())
    updated_at = Column(DateTime,
                        server_onupdate=func.current_timestamp(),
                        server_default=func.now())
    data = Column(JSONType, index=False, nullable=True)

    def set_data(self, key, value):
        if self.data is None:
            self.data = {}
        self.data[key] = value
        flag_modified(self, 'data')

    def get_data(self, key):
        if self.data is None:
            return None
        return self.data.get(key)
