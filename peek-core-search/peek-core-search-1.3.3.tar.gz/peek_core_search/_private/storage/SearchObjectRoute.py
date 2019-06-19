import logging

from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy.sql.schema import Index, ForeignKey

from peek_core_search._private.PluginNames import searchTuplePrefix
from vortex.Tuple import Tuple, addTupleType
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class SearchObjectRoute(Tuple, DeclarativeBase):
    """ Search Object Route

    This is like the "Open with"

    """
    __tablename__ = 'SearchObjectRoute'
    __tupleType__ = searchTuplePrefix + 'SearchObjectRouteTable'

    id = Column(Integer, primary_key=True, autoincrement=True)

    #:  The object that this routs is for
    objectId = Column(Integer,
                      ForeignKey('SearchObject.id', ondelete='CASCADE'),
                      nullable=False)

    importGroupHash = Column(String, nullable=False)
    routeTitle = Column(String, nullable=False)
    routePath = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_ObjectRoute_objectId", objectId), # For foreign key
        Index("idx_ObjectRoute_routeTitle_importGroupHash", importGroupHash, unique=False),
        Index("idx_ObjectRoute_routeTitle_objectId", routeTitle, objectId, unique=True),
    )
