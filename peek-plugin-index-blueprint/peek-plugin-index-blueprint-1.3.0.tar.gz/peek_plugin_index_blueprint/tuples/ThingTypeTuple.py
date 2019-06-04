from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintTuplePrefix


@addTupleType
class ThingTypeTuple(Tuple):
    """ ThingIndex Tuple

    This tuple is the publicly exposed ThingIndex

    """
    __tupleType__ = indexBlueprintTuplePrefix + 'ThingTypeTuple'

    #:  A protected variable
    id__: int = TupleField()

    #:  The unique key of this thingIndex
    key: str = TupleField()

    #:  The model set key of this thingIndex
    modelSetKey: str = TupleField()

    #:  The unique title of thingIndex
    name: str = TupleField()
