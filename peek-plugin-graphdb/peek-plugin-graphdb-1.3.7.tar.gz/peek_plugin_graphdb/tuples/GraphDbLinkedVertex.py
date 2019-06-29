from typing import Dict, List


class GraphDbLinkedVertex:
    """ Graph DB Linked Vertex

    This tuple is a vertex in the GraphDb plugin.

    """
    __slots__ = ("_k", "_p", "_e", "_sk")

    @property
    def key(self) -> str:
        """ Key

        The unique ID of this vertex
        """
        return self._k

    @property
    def props(self) -> Dict[str, str]:
        """ Properties
        """
        if self._p is None:
            self._p = {}
        return self._p

    @property
    def edges(self) -> List:
        """ Edges
            @:rtype List[GraphDbLinkedEdge]
        """
        if self._e is None:
            self._e = []
        return self._e


    @property
    def linksToSegmentKeys(self) -> List[str]:
        """ Next Segment Keys

        The keys of the other segments that this vertex links to.
        """
        if self._sk is None:
            self._sk = []
        return self._sk
