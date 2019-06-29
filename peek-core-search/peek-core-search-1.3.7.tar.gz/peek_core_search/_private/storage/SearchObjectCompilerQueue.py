import logging

from sqlalchemy import Column
from sqlalchemy import Integer, String

from peek_core_search._private.PluginNames import searchTuplePrefix
from vortex.Tuple import Tuple, addTupleType
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class SearchObjectCompilerQueue(Tuple, DeclarativeBase):
    __tablename__ = 'SearchObjectCompilerQueue'
    __tupleType__ = searchTuplePrefix + 'SearchObjectCompilerQueueTable'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chunkKey = Column(Integer, primary_key=True)


