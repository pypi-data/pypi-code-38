import logging

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from vortex.Tuple import Tuple, addTupleType
from peek_plugin_diagram._private.storage.DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class BranchIndexCompilerQueue(Tuple, DeclarativeBase):
    __tablename__ = 'BranchIndexCompilerQueue'
    __tupleType__ = diagramTuplePrefix + 'BranchIndexCompilerQueueTable'

    id = Column(Integer, primary_key=True, autoincrement=True)

    modelSetId = Column(Integer,
                        ForeignKey('ModelSet.id', ondelete='CASCADE'),
                        nullable=False,
                        autoincrement=True)

    chunkKey = Column(String, primary_key=True)
