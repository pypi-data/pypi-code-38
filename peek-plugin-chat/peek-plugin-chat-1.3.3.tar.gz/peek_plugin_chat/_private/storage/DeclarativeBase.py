from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.schema import MetaData

metadata = MetaData(schema="pl_chat")
DeclarativeBase = declarative_base(metadata=metadata)