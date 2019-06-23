from datetime import datetime

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram._private.tuples.branch.BranchTuple import BranchTuple
from vortex.Tuple import Tuple, addTupleType, TupleField


@addTupleType
class BranchLiveEditTuple(Tuple):
    """ Branch Live Edit Tuple

    This tuple is used internally to transfer branches between UIs that are actively
    editing the.

    This isn't stored anywhere, it just gets relayed between multiple UIs.

    """
    __tupleType__ = diagramTuplePrefix + 'BranchLiveEditTuple'

    # This field is server side only
    branchTuple: BranchTuple = TupleField()
    updatedByUser: str = TupleField()

    uiUpdateDate: datetime = TupleField()
    serverUpdateDate: datetime = TupleField()
    updateFromSave: bool = TupleField()
