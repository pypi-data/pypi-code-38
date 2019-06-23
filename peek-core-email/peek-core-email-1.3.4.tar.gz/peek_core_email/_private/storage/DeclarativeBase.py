
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.schema import MetaData

metadata = MetaData(schema="core_email")
DeclarativeBase = declarative_base(metadata=metadata)


def loadStorageTuples():

    from . import Setting
    Setting.__unused = False
