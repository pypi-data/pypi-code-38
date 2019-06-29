from typing import List

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class ImportBranchTuple(Tuple):
    """ Imported Branch

    This tuple is used by other plugins to load branches into the diagram.

    """
    __tupleType__ = diagramTuplePrefix + 'ImportBranchTuple'

    #:  The name of the model set for this branch
    modelSetKey: str = TupleField()

    #:  The Coordinate Set key that this branch applies to
    coordSetKey: str = TupleField()

    #:  The unique key for this branch
    key: str = TupleField()

    #:  The import hash for this branch
    importHash: str = TupleField()

    #:  The import hash for this branch
    importGroupHash: str = TupleField()

    #:  The alt color
    deltas: List = TupleField([])

    #:  The alt color
    addedDisps: List = TupleField([])

    #:  The alt color
    updatedDisps: List = TupleField([])

    #:  The alt color
    deletedDispKeys: List = TupleField([])

    #:  Is this branch Visible by default
    visible: bool = TupleField()
