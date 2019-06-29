from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ImportDispLevelTuple(Tuple):
    """ Import Display Level Tuple


    """
    __tupleType__ = diagramTuplePrefix + 'ImportDispLevelTuple'

    name: str = TupleField()

    order: int = TupleField()

    minZoom: float = TupleField()

    maxZoom: float = TupleField()

    importHash: str = TupleField()

    modelSetKey: str = TupleField()
