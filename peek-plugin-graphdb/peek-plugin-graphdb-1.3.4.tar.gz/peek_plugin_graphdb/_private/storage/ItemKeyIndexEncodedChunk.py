import logging

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from sqlalchemy import Column, LargeBinary
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Index

from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from vortex.Tuple import Tuple, addTupleType
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)



@addTupleType
class ItemKeyIndexEncodedChunk(Tuple, DeclarativeBase):
    __tablename__ = 'ItemKeyIndexEncodedChunk'
    __tupleType__ = graphDbTuplePrefix + 'ItemKeyIndexEncodedChunkTable'

    id = Column(Integer, primary_key=True, autoincrement=True)

    modelSetId = Column(Integer,
                        ForeignKey('GraphDbModelSet.id', ondelete='CASCADE'),
                        nullable=False)
    modelSet = relationship(GraphDbModelSet)

    chunkKey = Column(String, nullable=False)
    encodedData = Column(LargeBinary, nullable=False)
    encodedHash = Column(String, nullable=False)
    lastUpdate = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_ItemKeyIndexEnc_modelSetId_chunkKey", modelSetId, chunkKey, unique=False),
    )
