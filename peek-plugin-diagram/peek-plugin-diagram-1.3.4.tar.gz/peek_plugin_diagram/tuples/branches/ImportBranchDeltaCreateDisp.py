from typing import List

from vortex.Tuple import TupleField, addTupleType, Tuple

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ImportBranchDeltaCreateDisp(Tuple):
    """ Imported Branch Delta Create Disp

    This branch delta will change the color of disps.

    """
    __tupleType__ = diagramTuplePrefix + 'ImportBranchDeltaCreateDisp'

    #:  A list of keys to apply this color to.
    disps: List[str] = TupleField([])

