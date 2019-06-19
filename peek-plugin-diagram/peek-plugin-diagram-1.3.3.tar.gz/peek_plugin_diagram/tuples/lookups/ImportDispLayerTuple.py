from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ImportDispLayerTuple(Tuple):
    """ Import Display Layer Tuple


    """
    __tupleType__ = diagramTuplePrefix + 'ImportDispLayerTuple'

    name: str = TupleField()

    order: int = TupleField()

    visible: bool = TupleField()

    selectable: bool = TupleField()

    importHash: str = TupleField()

    modelSetKey: str = TupleField()
