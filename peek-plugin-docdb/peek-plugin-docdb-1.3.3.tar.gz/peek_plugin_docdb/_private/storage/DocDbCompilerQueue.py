import logging

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String

from peek_plugin_docdb._private.PluginNames import docDbTuplePrefix
from vortex.Tuple import Tuple, addTupleType
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class DocDbCompilerQueue(Tuple, DeclarativeBase):
    __tupleType__ = docDbTuplePrefix + 'DocDbChunkQueueTuple'
    __tablename__ = 'DocDbChunkQueue'

    id = Column(Integer, primary_key=True, autoincrement=True)

    modelSetId = Column(Integer,
                        ForeignKey('DocDbModelSet.id', ondelete='CASCADE'),
                        nullable=False)

    chunkKey = Column(String, primary_key=True)
