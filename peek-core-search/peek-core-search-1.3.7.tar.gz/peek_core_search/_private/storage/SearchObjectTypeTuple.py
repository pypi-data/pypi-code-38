from sqlalchemy import Column, Index
from sqlalchemy import Integer, String

from peek_core_search._private.PluginNames import searchTuplePrefix
from peek_core_search._private.storage.DeclarativeBase import DeclarativeBase
from vortex.Tuple import Tuple, addTupleType


@addTupleType
class SearchObjectTypeTuple(Tuple, DeclarativeBase):
    __tupleType__ = searchTuplePrefix + 'SearchObjectTypeTuple'
    __tablename__ = 'SearchObjectType'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    title = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_ObjType_name", name, unique=True),
        Index("idx_ObjType_title", title, unique=True),
    )
