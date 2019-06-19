from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC

from peek_plugin_branch._private.PluginNames import branchTuplePrefix
from peek_plugin_branch.tuples.BranchDetailTuple import BranchDetailTuple


@addTupleType
class CreateBranchActionTuple(TupleActionABC):
    __tupleType__ = branchTuplePrefix + "CreateBranchActionTuple"

    branchDetail: BranchDetailTuple = TupleField()
