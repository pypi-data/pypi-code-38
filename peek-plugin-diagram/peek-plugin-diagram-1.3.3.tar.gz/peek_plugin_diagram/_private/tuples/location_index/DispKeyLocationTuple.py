from typing import List

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple


@addTupleType
class DispKeyLocationTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "DispKeyLocationTuple"

    coordSetKey: str = TupleField()

    coordSetId: int = TupleField()
    dispId: int = TupleField()

    x: float = TupleField()
    y: float = TupleField()

    def toLocationJson(self) -> str:
        return '[%s,%s,%s,%s]' % (
            self.coordSetId,
            self.dispId,
            self.x,
            self.y
        )

    @classmethod
    def fromLocationJson(self, items: List[int]) -> 'DispKeyLocationTuple':
        assert len(items) == 4, "Invalid packed data."
        newItem = DispKeyLocationTuple()

        newItem.coordSetId = items[0]
        newItem.dispId = items[1]
        newItem.x = items[2]
        newItem.y = items[3]

        return newItem
