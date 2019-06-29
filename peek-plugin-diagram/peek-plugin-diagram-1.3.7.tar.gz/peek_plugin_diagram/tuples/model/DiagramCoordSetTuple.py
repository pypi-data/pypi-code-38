from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from vortex.Tuple import Tuple, addTupleType, TupleField


@addTupleType
class DiagramCoordSetTuple(Tuple):
    """ Diagram Coordinate Set Tuple

    This tuple represents a coordinate set in the diagram data storage.

    """
    __tupleType__ = diagramTuplePrefix + 'DiagramCoordSetTuple'

    #:  The ID of the coordinate set.
    key: int = TupleField()

    #:  The name of the coordinate set.
    name: str = TupleField()

