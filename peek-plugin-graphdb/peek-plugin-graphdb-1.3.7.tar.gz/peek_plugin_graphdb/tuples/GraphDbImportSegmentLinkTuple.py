from typing import Dict, Any

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from vortex.Tuple import Tuple, addTupleType, TupleField


@addTupleType
class GraphDbImportSegmentLinkTuple(Tuple):
    """ Segment Link Tuple

    This tuple is the publicly exposed Segment Links

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbImportSegmentLinkTuple'

    #:  The key of the vertex that joins the two segments
    vertexKey: str = TupleField()

    #:  The segment that this segment links to
    segmentKey: str = TupleField()

    def packJsonDict(self) -> Dict[str, Any]:
        return dict(
            vk=self.vertexKey,
            sk=self.segmentKey
        )
