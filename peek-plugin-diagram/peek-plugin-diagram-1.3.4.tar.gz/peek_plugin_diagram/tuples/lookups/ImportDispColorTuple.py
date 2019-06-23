from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ImportDispColorTuple(Tuple):
    """ Imported Display Color

    This tuple is used by other plugins to load colours into the diagram.

    """
    __tupleType__ = diagramTuplePrefix + 'ImportDispColorTuple'

    #:  The name of the color
    name: str = TupleField()

    #:  The color
    color: str = TupleField()

    #:  The alt color
    altColor: str = TupleField()

    #:  The swap period if this is a flashing colour
    swapPeriod: float = TupleField()

    #:  The name of the model set for this colour
    modelSetKey: str = TupleField()

    #:  The import hash for this colour
    importHash: str = TupleField()
