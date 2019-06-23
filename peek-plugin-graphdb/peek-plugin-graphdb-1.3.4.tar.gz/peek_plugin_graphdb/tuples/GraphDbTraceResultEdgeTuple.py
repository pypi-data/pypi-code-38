from typing import Dict

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix


@addTupleType
class GraphDbTraceResultEdgeTuple(Tuple):
    """ GraphDB Trace Result Edge Tuple

    This tuple contains the result of running a trace on the model

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbTraceResultEdgeTuple'
    __rawJonableFields__ = ('key', 'srcVertexKey', 'dstVertexKey', 'props')

    #:  The key of edge
    key: str = TupleField()

    #:  The key of the source vertex
    srcVertexKey: str = TupleField()

    #:  The key of the destination vertex
    dstVertexKey: str = TupleField()

    #:  The key of the Trace Config
    props: Dict = TupleField()
