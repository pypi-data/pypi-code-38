from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from peek_plugin_diagram._private.tuples.branch.BranchTuple import BranchTuple


@addTupleType
class BranchUpdateTupleAction(TupleActionABC):
    """ Branch Update Tuple Action

    This is the Branch Update tuple Action

    """
    __tupleType__ = diagramTuplePrefix + 'BranchUpdateTupleAction'

    doDelete: bool = TupleField(False)
    modelSetId:int = TupleField()
    branchTuple: BranchTuple = TupleField()
