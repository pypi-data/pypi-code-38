from sqlalchemy import Column, Index, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship

from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintTuplePrefix
from peek_plugin_index_blueprint._private.storage.DeclarativeBase import DeclarativeBase
from peek_plugin_index_blueprint._private.storage.ThingType import \
    ThingType
from peek_plugin_index_blueprint._private.storage.ModelSet import ModelSet
from vortex.Tuple import Tuple, addTupleType


@addTupleType
class ThingIndex(Tuple, DeclarativeBase):
    __tablename__ = 'ThingIndex'
    __tupleType__ = indexBlueprintTuplePrefix + 'ThingIndexTable'

    #:  The unique ID of this thingIndex (database generated)
    id = Column(Integer, primary_key=True, autoincrement=True)

    #:  The model set for this thingIndex
    modelSetId = Column(Integer,
                        ForeignKey('ModelSet.id', ondelete='CASCADE'),
                        nullable=False)
    modelSet = relationship(ModelSet)

    #:  The model set for this thingIndex
    thingTypeId = Column(Integer,
                            ForeignKey('ThingType.id', ondelete='CASCADE'),
                            nullable=False)
    thingType = relationship(ThingType)

    importGroupHash = Column(String, nullable=False)

    #:  The unique key of this thingIndex
    key = Column(String, nullable=False)

    #:  The chunk that this thingIndex fits into
    chunkKey = Column(String, nullable=False)

    #:  The JSON ready for the Compiler to use
    packedJson = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_ThingIndex_key", modelSetId, key, unique=True),
        Index("idx_ThingIndex_thingType", thingTypeId, unique=False),
        Index("idx_ThingIndex_chunkKey", chunkKey, unique=False),
        Index("idx_ThingIndex_importGroupHash", importGroupHash, unique=False),
    )
