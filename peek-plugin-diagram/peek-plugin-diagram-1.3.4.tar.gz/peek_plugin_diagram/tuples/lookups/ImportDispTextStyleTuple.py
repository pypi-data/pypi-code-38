from typing import Optional

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ImportDispTextStyleTuple(Tuple):
    """ Import Display Text Style Tuple


    """
    __tupleType__ = diagramTuplePrefix + 'ImportDispTextStyleTuple'



    name: str = TupleField()

    fontName: str = TupleField()
    fontSize: float = TupleField()

    STYLE_BOLD = "bold"
    fontStyle: str = TupleField()

    scalable: bool = TupleField()
    scaleFactor: float = TupleField()

    importHash: str = TupleField()

    modelSetKey: str = TupleField()
