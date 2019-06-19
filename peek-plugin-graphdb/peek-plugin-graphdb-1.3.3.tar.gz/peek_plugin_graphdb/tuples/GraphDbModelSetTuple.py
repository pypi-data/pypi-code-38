from typing import Dict

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from vortex.Tuple import Tuple, addTupleType, TupleField


@addTupleType
class GraphDbModelSetTuple(Tuple):
    """ GraphDB Model Set Tuple

    This tuple is the publicly exposed ModelSet

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbModelSetTuple'

    #:  A private variable
    id: int = TupleField()
    key: str = TupleField()
    name: str = TupleField()

    comment: str = TupleField()
    propsJson: Dict = TupleField()
