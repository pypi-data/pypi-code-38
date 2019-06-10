import logging

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String

from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintTuplePrefix
from vortex.Tuple import Tuple, addTupleType
from .DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class ThingIndexCompilerQueue(Tuple, DeclarativeBase):
    __tablename__ = 'ThingIndexCompilerQueue'
    __tupleType__ = indexBlueprintTuplePrefix + 'ThingIndexCompilerQueueTable'

    id = Column(Integer, primary_key=True, autoincrement=True)

    modelSetId = Column(Integer,
                        ForeignKey('ModelSet.id', ondelete='CASCADE'),
                        nullable=False,
                        autoincrement=True)

    chunkKey = Column(String, primary_key=True)
