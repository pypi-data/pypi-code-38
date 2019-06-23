from typing import Dict

from peek_plugin_graphdb.tuples.GraphDbLinkedEdge import GraphDbLinkedEdge
from peek_plugin_graphdb.tuples.GraphDbLinkedVertex import GraphDbLinkedVertex


class GraphDbLinked:
    """ Linked Model

    This tuple is the publicly exposed Segment

    """
    #:  The model set of this model
    modelSetKey: str = None

    #:  The edges
    edgeByKey: Dict[str, GraphDbLinkedEdge] = {}

    #:  The vertexes
    vertexByKey: Dict[str, GraphDbLinkedVertex] = {}