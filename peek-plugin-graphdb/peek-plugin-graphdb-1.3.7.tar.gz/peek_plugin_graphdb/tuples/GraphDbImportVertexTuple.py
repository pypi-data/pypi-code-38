from typing import Dict, Any

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from vortex.Tuple import Tuple, addTupleType


@addTupleType
class GraphDbImportVertexTuple(Tuple):
    """ Graph DB Vertex Tuple

    This tuple represents a vertex in the GraphDb plugin.

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbImportVertexTuple'
    __slots__ = ("k", "p")
    __rawJonableFields__ = ["p"]

    @property
    def key(self) -> str:
        return self.k

    @key.setter
    def key(self, val) -> None:
        self.k = val

    @property
    def props(self) -> Dict[str, str]:
        if self.p is None:
            self.p = {}
        return self.p

    @props.setter
    def props(self, val) -> None:
        self.p = val

    def __repr__(self):
        return '%s.%s' % (self.k, self.p)

    def packJsonDict(self) -> Dict[str, Any]:
        return dict(
            k=self.k,
            p=self.p
        )
