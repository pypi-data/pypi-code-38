from typing import Dict

from vortex.Tuple import addTupleType, Tuple

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix


@addTupleType
class GraphDbPackedSegmentTuple(Tuple):
    """ Packed Segment

    This tuple transports the Segment JSON that is packed in the encoded segment.

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbPackedSegmentTuple'
    __rawJonableFields__ = ['key', 'jsonDict']

    #:  The unique key of this segment
    key: str = None

    #:  The raw packed data of the segment (Not in vortex.Tuple format)
    packedJson: Dict = None
