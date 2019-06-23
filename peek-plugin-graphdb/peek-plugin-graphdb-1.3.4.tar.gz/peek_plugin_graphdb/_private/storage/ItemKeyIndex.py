from peek_plugin_graphdb._private.tuples.ItemKeyTuple import ItemKeyTuple
from sqlalchemy import Column, Index, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb._private.storage.DeclarativeBase import DeclarativeBase
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from vortex.Tuple import Tuple, addTupleType


@addTupleType
class ItemKeyIndex(Tuple, DeclarativeBase):
    __tablename__ = 'ItemKeyIndex'
    __tupleType__ = graphDbTuplePrefix + 'ItemKeyIndexTable'

    #:  The unique ID of this itemKeyIndex (database generated)
    id = Column(Integer, primary_key=True, autoincrement=True)

    #:  The model set for this itemKeyIndex
    modelSetId = Column(Integer,
                        ForeignKey('GraphDbModelSet.id', ondelete='CASCADE'),
                        nullable=False)
    modelSet = relationship(GraphDbModelSet)

    importGroupHash = Column(String, nullable=False)

    #:  The chunk that this itemKeyIndex fits into
    chunkKey = Column(String, nullable=False)

    #:  The unique key of this itemKeyIndex
    itemKey = Column(String, nullable=False)

    #:  The unique key of this itemKeyIndex
    itemType = Column(Integer, nullable=False)
    ITEM_TYPE_VERTEX = ItemKeyTuple.ITEM_TYPE_VERTEX
    ITEM_TYPE_EDGE = ItemKeyTuple.ITEM_TYPE_EDGE

    #:  The key of the segment where it's stored
    segmentKey = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_ItemKeyIndex_chunkKey", chunkKey, unique=False),
        Index("idx_ItemKeyIndex_importGroupHash", importGroupHash, unique=False),
    )
