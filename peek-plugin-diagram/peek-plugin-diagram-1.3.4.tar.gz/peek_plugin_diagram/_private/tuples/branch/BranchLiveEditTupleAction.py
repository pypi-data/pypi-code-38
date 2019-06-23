from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram._private.tuples.branch.BranchTuple import BranchTuple


@addTupleType
class BranchLiveEditTupleAction(TupleActionABC):
    """ Branch Live Edit Tuple Action

    This is the Branch Live Edit tuple Action

    """
    __tupleType__ = diagramTuplePrefix + 'BranchLiveEditTupleAction'

    EDITING_STARTED = 1
    EDITING_UPDATED = 2
    EDITING_FINISHED = 3

    updatedByUser: str = TupleField()
    actionType: int = TupleField()
    branchTuple: BranchTuple = TupleField()
