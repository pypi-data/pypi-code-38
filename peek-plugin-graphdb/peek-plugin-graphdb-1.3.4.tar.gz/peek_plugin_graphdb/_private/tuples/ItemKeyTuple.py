import json

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix


@addTupleType
class ItemKeyTuple(Tuple):
    """ Item Key Tuple

    This tuple provides the segment keys of a vertex or edge within the GraphDB model.

    """
    __tupleType__ = graphDbTuplePrefix + 'ItemKeyTuple'

    #:  The unique key of this itemKeyIndex
    key: str = TupleField()

    #:  The model set  keyof this itemKeyIndex
    modelSetKey: str = TupleField()

    #:  The itemKeyIndex type
    itemType: int = TupleField()
    ITEM_TYPE_VERTEX = 1
    ITEM_TYPE_EDGE = 2

    #:  The key of the vertex or edge
    itemKey: str = TupleField()

    #:  The key of the segment where it's stored
    segmentKeys: str = TupleField()

    def unpackJson(self, key: str, packedJson: str,
                   modelSetKey: str) -> 'ItemKeyTuple':
        # Reconstruct the data
        objectProps: {} = json.loads(packedJson)

        # Unpack the custom data here
        self.itemKey = key
        self.modelSetKey = modelSetKey
        self.itemType = objectProps.get('itemType')
        self.segmentKeys = objectProps.get('segmentKeys')

        return self
