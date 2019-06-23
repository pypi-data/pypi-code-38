import logging

from sqlalchemy import Column, LargeBinary
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Index

from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from peek_plugin_graphdb._private.tuples.GraphDbEncodedChunkTuple import \
    GraphDbEncodedChunkTuple
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


class GraphDbEncodedChunk(DeclarativeBase):
    __tablename__ = 'GraphDbEncodedChunk'

    id = Column(Integer, primary_key=True, autoincrement=True)

    modelSetId = Column(Integer,
                        ForeignKey('GraphDbModelSet.id', ondelete='CASCADE'),
                        nullable=False)
    modelSet = relationship(GraphDbModelSet, lazy=False)

    chunkKey = Column(String, nullable=False)
    encodedData = Column(LargeBinary, nullable=False)
    encodedHash = Column(String, nullable=False)
    lastUpdate = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_Chunk_modelSetId_chunkKey", modelSetId, chunkKey, unique=False),
    )

    def toTuple(self) -> GraphDbEncodedChunkTuple:
        return GraphDbEncodedChunkTuple(
            modelSetKey=self.modelSet.key,
            chunkKey=self.chunkKey,
            encodedData=self.encodedData,
            encodedHash=self.encodedHash,
            lastUpdate=self.lastUpdate
        )
