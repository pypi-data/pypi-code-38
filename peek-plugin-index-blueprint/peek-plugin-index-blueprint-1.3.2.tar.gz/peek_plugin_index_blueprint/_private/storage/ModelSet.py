import json

from sqlalchemy import Column
from sqlalchemy import Integer, String
from vortex.Tuple import addTupleType, Tuple

from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintTuplePrefix
from peek_plugin_index_blueprint.tuples.IndexBlueprintModelSetTuple import \
    IndexBlueprintModelSetTuple
from .DeclarativeBase import DeclarativeBase


@addTupleType
class ModelSet(Tuple, DeclarativeBase):
    __tablename__ = 'ModelSet'
    __tupleType__ = indexBlueprintTuplePrefix + "ModelSetTable"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)

    comment = Column(String)
    propsJson = Column(String)

    def toTuple(self) -> IndexBlueprintModelSetTuple:
        newTuple = IndexBlueprintModelSetTuple()
        newTuple.id__ = self.id
        newTuple.key = self.key
        newTuple.name = self.name
        newTuple.comment = self.comment
        newTuple.props = json.loads(self.propsJson) if self.propsJson else {}
        return newTuple
