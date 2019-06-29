from typing import Dict, Any

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from vortex.Tuple import Tuple, addTupleType


@addTupleType
class GraphDbImportEdgeTuple(Tuple):
    """ Graph DB Edge Tuple

    This tuple represents a connection between two vertices.

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbImportEdgeTuple'
    __slots__ = ("k", "sk", "dk", "p")
    __rawJonableFields__ = ["p"]

    @property
    def key(self) -> str:
        return self.k

    @key.setter
    def key(self, val) -> None:
        self.k = val

    @property
    def srcVertexKey(self) -> str:
        return self.sk

    @srcVertexKey.setter
    def srcVertexKey(self, val) -> None:
        self.sk = val

    @property
    def dstVertexKey(self) -> str:
        return self.dk

    @dstVertexKey.setter
    def dstVertexKey(self, val) -> None:
        self.dk = val

    @property
    def props(self) -> Dict[str, str]:
        if self.p is None:
            self.p = {}
        return self.p

    @props.setter
    def props(self, val) -> None:
        self.p = val

    def __repr__(self):
        return '%s.%s.%s.%s' % (self.k, self.sk, self.dk, self.p)

    def packJsonDict(self) -> Dict[str, Any]:
        return dict(
            k=self.k,
            sk=self.sk,
            dk=self.dk,
            p=self.p
        )
