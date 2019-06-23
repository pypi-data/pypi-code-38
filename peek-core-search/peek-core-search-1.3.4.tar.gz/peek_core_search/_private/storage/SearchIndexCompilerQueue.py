import logging

from sqlalchemy import Column
from sqlalchemy import Integer, String

from peek_core_search._private.PluginNames import searchTuplePrefix
from vortex.Tuple import Tuple, addTupleType
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class SearchIndexCompilerQueue(Tuple, DeclarativeBase):
    __tablename__ = 'SearchIndexCompilerQueue'
    __tupleType__ = searchTuplePrefix + 'SearchIndexCompilerQueueTable'

    id = Column(Integer, primary_key=True, autoincrement=True)

    chunkKey = Column(Integer, primary_key=True)
