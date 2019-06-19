from sqlalchemy import Column, Index, ForeignKey, DateTime
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from vortex.Tuple import Tuple, addTupleType

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram._private.storage.DeclarativeBase import DeclarativeBase
from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSet


@addTupleType
class BranchIndex(Tuple, DeclarativeBase):
    """ Branch Index

    The BranchIndex is implemented to allow editing of individual branches via the UI,
    AND staging of imported branches so they are packed into the grids.

    This table stores the JSON packed versions of the branches, ready to be compiled
    into the encoded chunk.

    This table is not in an ideal format for updates (appending deltas, etc), but since
    edits are performed by users, this can be unpacked and re-packed suitable fast.

    """
    __tablename__ = 'BranchIndex'
    __tupleType__ = diagramTuplePrefix + 'BranchIndexTable'

    #:  The unique ID of this branchIndex (database generated)
    id = Column(Integer, primary_key=True, autoincrement=True)

    #:  The model set for this branchIndex
    coordSetId = Column(Integer,
                        ForeignKey('ModelCoordSet.id', ondelete='CASCADE'),
                        nullable=False)
    coordSet = relationship(ModelCoordSet)

    importHash = Column(String)

    importGroupHash = Column(String)

    #:  The unique key of this branchIndex
    key = Column(String, nullable=False)

    #:  The chunk that this branchIndex fits into
    chunkKey = Column(String, nullable=False)

    updatedDate = Column(DateTime(timezone=True))
    createdDate = Column(DateTime(timezone=True), nullable=False)

    #:  The JSON ready for the Compiler to use
    packedJson = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_BranchIndex_key", coordSetId, key, unique=True),
        Index("idx_BranchIndex_chunkKey", chunkKey, unique=False),
        Index("idx_BranchIndex_importHash", coordSetId, importHash, unique=True),
        Index("idx_BranchIndex_importGroupHash", coordSetId, importGroupHash,
              unique=False),
    )
