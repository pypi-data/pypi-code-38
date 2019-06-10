from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintTuplePrefix


@addTupleType
class IndexBlueprintModelSetTuple(Tuple):
    """ Model Set Tuple

    This tuple is the publicly exposed Model Set for the IndexBlueprint plugin

    """
    __tupleType__ = indexBlueprintTuplePrefix + 'ModelSetTuple'

    #:  A protected variable
    id__: int = TupleField()

    #:  The unique key of this model set
    key: str = TupleField()

    #:  The name of this model set
    name: str = TupleField()

    #:  The name of this model set
    comment: str = TupleField()

    #:  Custom properties of this model set
    props: {} = TupleField()

