import logging

from peek_plugin_docdb._private.PluginNames import docDbTuplePrefix
from sqlalchemy import Column, LargeBinary
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Index

from peek_plugin_docdb._private.storage.DocDbModelSet import DocDbModelSet
from vortex.Tuple import Tuple, addTupleType
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)



@addTupleType
class DocDbEncodedChunk(Tuple, DeclarativeBase):
    __tablename__ = 'DocDbEncodedChunkTuple'
    __tupleType__ = docDbTuplePrefix + 'DocDbEncodedChunk'

    id = Column(Integer, primary_key=True, autoincrement=True)

    modelSetId = Column(Integer,
                        ForeignKey('DocDbModelSet.id', ondelete='CASCADE'),
                        nullable=False)
    modelSet = relationship(DocDbModelSet)

    chunkKey = Column(String, nullable=False)
    encodedData = Column(LargeBinary, nullable=False)
    encodedHash = Column(String, nullable=False)
    lastUpdate = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_Chunk_modelSetId_chunkKey", modelSetId, chunkKey, unique=False),
    )
