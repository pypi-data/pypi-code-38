from sqlalchemy import Column, Index, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from vortex.Tuple import Tuple, addTupleType

from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintTuplePrefix
from peek_plugin_index_blueprint._private.storage.DeclarativeBase import DeclarativeBase
from peek_plugin_index_blueprint._private.storage.ModelSet import ModelSet
from peek_plugin_index_blueprint.tuples.ThingTypeTuple import ThingTypeTuple


@addTupleType
class ThingType(Tuple, DeclarativeBase):
    __tablename__ = 'ThingType'
    __tupleType__ = indexBlueprintTuplePrefix + 'ThingTypeTable'

    id = Column(Integer, primary_key=True, autoincrement=True)

    #:  The model set for this thingIndex
    modelSetId = Column(Integer,
                        ForeignKey('ModelSet.id', ondelete='CASCADE'),
                        nullable=False)
    modelSet = relationship(ModelSet, lazy=False)

    key = Column(String, nullable=False)
    name = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_DocType_model_key", modelSetId, key, unique=True),
        Index("idx_DocType_model_name", modelSetId, name, unique=True),
    )

    def toTuple(self) -> ThingTypeTuple:
        newTuple = ThingTypeTuple()
        newTuple.id__ = self.id
        newTuple.key = self.key
        newTuple.modelSetKey = self.modelSet.key
        newTuple.name = self.name
        return newTuple
