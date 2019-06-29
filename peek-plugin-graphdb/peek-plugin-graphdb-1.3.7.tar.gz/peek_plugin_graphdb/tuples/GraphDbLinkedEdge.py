from typing import Dict

from peek_plugin_graphdb.tuples.GraphDbLinkedVertex import GraphDbLinkedVertex


class GraphDbLinkedEdge:
    """ Graph DB Linked Edge

    This tuple is a connection between two vertices.

    """
    __slots__ = ("_k", "_s", "_d", "_p")

    @property
    def key(self) -> str:
        return self._k

    @property
    def srcVertex(self) -> GraphDbLinkedVertex:
        return self._s

    @property
    def dstVertex(self) -> GraphDbLinkedVertex:
        return self._d

    @property
    def props(self) -> Dict[str, str]:
        if self._p is None:
            self._p = {}
        return self._p

    def getOtherVertex(self, vertexKey:str) -> GraphDbLinkedVertex:
        if self.srcVertex.key == vertexKey:
            return self.dstVertex
        return self.srcVertex