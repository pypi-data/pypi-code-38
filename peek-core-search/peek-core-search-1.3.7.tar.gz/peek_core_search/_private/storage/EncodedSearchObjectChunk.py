from sqlalchemy import Column, LargeBinary
from sqlalchemy import Integer, String
from sqlalchemy.sql.schema import Index

from peek_core_search._private.PluginNames import searchTuplePrefix
from peek_core_search._private.storage.DeclarativeBase import DeclarativeBase
from vortex.Tuple import Tuple, addTupleType


@addTupleType
class EncodedSearchObjectChunk(Tuple, DeclarativeBase):
    __tablename__ = 'EncodedSearchObjectChunk'
    __tupleType__ = searchTuplePrefix + 'EncodedSearchObjectChunkTable'

    id = Column(Integer, primary_key=True, autoincrement=True)

    chunkKey = Column(Integer, primary_key=True)
    encodedData = Column(LargeBinary, nullable=False)
    encodedHash = Column(String, nullable=False)
    lastUpdate = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_EncodedSearchObject_chunkKey", chunkKey, unique=True),
    )
