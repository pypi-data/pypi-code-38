import logging

from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintTuplePrefix
from sqlalchemy import Column, LargeBinary
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Index

from peek_plugin_index_blueprint._private.storage.ModelSet import ModelSet
from vortex.Tuple import Tuple, addTupleType
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)



@addTupleType
class ThingIndexEncodedChunk(Tuple, DeclarativeBase):
    __tablename__ = 'ThingIndexEncodedChunk'
    __tupleType__ = indexBlueprintTuplePrefix + 'ThingIndexEncodedChunkTable'

    id = Column(Integer, primary_key=True, autoincrement=True)

    modelSetId = Column(Integer,
                        ForeignKey('ModelSet.id', ondelete='CASCADE'),
                        nullable=False)
    modelSet = relationship(ModelSet)

    chunkKey = Column(String, nullable=False)
    encodedData = Column(LargeBinary, nullable=False)
    encodedHash = Column(String, nullable=False)
    lastUpdate = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_ThingIndexEnc_modelSetId_chunkKey", modelSetId, chunkKey, unique=False),
    )
