import logging

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from vortex.Tuple import Tuple, addTupleType
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class GraphDbCompilerQueue(Tuple, DeclarativeBase):
    __tupleType__ = graphDbTuplePrefix + 'GraphDbChunkQueueTuple'
    __tablename__ = 'GraphDbChunkQueue'

    id = Column(Integer, primary_key=True, autoincrement=True)

    modelSetId = Column(Integer,
                        ForeignKey('GraphDbModelSet.id', ondelete='CASCADE'),
                        nullable=False)

    chunkKey = Column(String, primary_key=True)
