from typing import Dict

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix


@addTupleType
class GraphDbTraceResultVertexTuple(Tuple):
    """ GraphDB Trace Result Vertex Tuple

    This tuple contains the result of running a trace on the model

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbTraceResultVertexTuple'
    __rawJonableFields__ = ('key', 'props')

    #:  The key of this vertex
    key: str = TupleField()

    #:  The properties of this vertex
    props: Dict = TupleField()

