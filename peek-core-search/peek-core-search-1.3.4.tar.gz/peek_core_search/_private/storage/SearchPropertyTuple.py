from sqlalchemy import Column, Index
from sqlalchemy import Integer, String

from peek_core_search._private.PluginNames import searchTuplePrefix
from peek_core_search._private.storage.DeclarativeBase import DeclarativeBase
from vortex.Tuple import Tuple, addTupleType


@addTupleType
class SearchPropertyTuple(Tuple, DeclarativeBase):
    __tupleType__ = searchTuplePrefix + 'SearchPropertyTuple'
    __tablename__ = 'SearchProperty'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    order = Column(Integer, nullable=False, server_default='0')

    __table_args__ = (
        Index("idx_SearchProp_name", name, unique=True),
        Index("idx_SearchProp_title", title, unique=True),
    )
