from sqlalchemy import Column
from sqlalchemy import Integer, String
from vortex.Tuple import addTupleType, Tuple

from peek_plugin_docdb._private.PluginNames import docDbTuplePrefix
from .DeclarativeBase import DeclarativeBase


@addTupleType
class DocDbModelSet(Tuple, DeclarativeBase):
    __tablename__ = 'DocDbModelSet'
    __tupleType__ = docDbTuplePrefix + __tablename__

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)

    comment = Column(String)
    propsJson = Column(String)

