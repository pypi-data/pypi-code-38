import logging

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from sqlalchemy import Column, LargeBinary
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Index

from peek_plugin_diagram._private.storage.ModelSet import ModelSet
from vortex.Tuple import Tuple, addTupleType
from peek_plugin_diagram._private.storage.DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)



@addTupleType
class BranchIndexEncodedChunk(Tuple, DeclarativeBase):
    __tablename__ = 'BranchIndexEncodedChunk'
    __tupleType__ = diagramTuplePrefix + 'BranchIndexEncodedChunkTable'

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
        Index("idx_BranchIndexEnc_modelSetId_chunkKey", modelSetId, chunkKey, unique=False),
    )
