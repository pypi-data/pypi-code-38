from typing import Dict

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class BranchKeyToIdMapTuple(Tuple):
    """ Branch Key to ID Map Tuple

    This tuple is used by the UI to get the IDs for branches for the
    model compiler to enable branches.

    """
    __tupleType__ = diagramTuplePrefix + 'BranchKeyToIdMapTuple'

    # This field is server side only
    coordSetId: int = TupleField()
    keyIdMap: Dict[str, int] = TupleField()
