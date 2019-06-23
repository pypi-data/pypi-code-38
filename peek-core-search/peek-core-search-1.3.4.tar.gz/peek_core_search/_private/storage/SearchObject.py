import logging

from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy.sql.schema import Index, ForeignKey

from peek_core_search._private.PluginNames import searchTuplePrefix
from vortex.Tuple import Tuple, addTupleType
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class SearchObject(Tuple, DeclarativeBase):
    __tablename__ = 'SearchObject'
    __tupleType__ = searchTuplePrefix + 'SearchObjectTable'

    id = Column(Integer, primary_key=True, autoincrement=True)

    #:  The object that this routs is for
    objectTypeId = Column(Integer,
                          ForeignKey('SearchObjectType.id', ondelete='CASCADE'),
                          nullable=False)

    key = Column(String, nullable=False)

    chunkKey = Column(Integer, nullable=False)

    propertiesJson = Column(String, nullable=True)

    packedJson = Column(String, nullable=True)

    __table_args__ = (
        Index("idx_SearchObject_objectTypeId", objectTypeId),
        Index("idx_SearchObject_key", key, unique=True),
        Index("idx_SearchObject_chunkKey", chunkKey),
    )
