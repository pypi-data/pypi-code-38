from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintTuplePrefix


@addTupleType
class ThingImportTuple(Tuple):
    """ Import ThingIndex Tuple

    This tuple is the publicly exposed ThingIndex

    """
    __tupleType__ = indexBlueprintTuplePrefix + 'ThingImportTuple'

    #:  The unique key of this thingIndex
    key: str = TupleField()

    #:  The model set of this thingIndex
    modelSetKey: str = TupleField()

    #:  The thingIndex type
    thingTypeKey: str = TupleField()

    #:  The hash of this import group
    importGroupHash: str = TupleField()

    #:  A string value of the thing
    valueStr: str = TupleField()

    #:  An int value of the thing
    valueInt: int = TupleField()

    # Add more values here
