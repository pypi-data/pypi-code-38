from sqlalchemy import Column
from sqlalchemy import Integer, String
from vortex.Tuple import Tuple, addTupleType

from peek_plugin_diagram_generic_menu._private.PluginNames import diagramGenericMenuTuplePrefix
from peek_plugin_diagram_generic_menu._private.storage.DeclarativeBase import DeclarativeBase


@addTupleType
class DiagramGenericMenuTuple(Tuple, DeclarativeBase):
    __tupleType__ = diagramGenericMenuTuplePrefix + 'DiagramGenericMenuTuple'
    __tablename__ = 'DiagramGenericMenu'

    id = Column(Integer, primary_key=True, autoincrement=True)
    modelSetKey = Column(String)
    coordSetKey = Column(String)
    faIcon = Column(String)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)