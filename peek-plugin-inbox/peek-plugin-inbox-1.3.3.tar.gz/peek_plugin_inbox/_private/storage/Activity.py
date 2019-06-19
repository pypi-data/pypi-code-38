""" 
 *  Copyright Synerty Pty Ltd 2016
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""
import logging

from peek_plugin_inbox._private.PluginNames import inboxTuplePrefix
from peek_plugin_inbox._private.storage.DeclarativeBase import DeclarativeBase
from sqlalchemy import Column, Index
from sqlalchemy import Integer, String
from sqlalchemy.sql.sqltypes import DateTime
from vortex.Tuple import Tuple, addTupleType

logger = logging.getLogger(__name__)


@addTupleType
class Activity(Tuple, DeclarativeBase):
    """ Activity

    An Activity represents an item in the activity screen
    This is a screen that is intended to show actions that have been performed recently
        or events that plugins want in this list.
    
    see InboxAbiABC.NewActivity for documentation.
        
    """
    __tupleType__ = inboxTuplePrefix + 'Activity'
    __tablename__ = 'Activity'

    id = Column(Integer, primary_key=True, autoincrement=True)

    pluginName = Column(String, nullable=False)
    uniqueId = Column(String, nullable=False)
    userId = Column(String, nullable=False)
    dateTime = Column(DateTime(True), nullable=False)

    # The display properties of the task
    title = Column(String, nullable=False)
    description = Column(String)
    iconPath = Column(String)

    # The mobile-app route to open when this task is selected
    routePath = Column(String)
    routeParamJson = Column(String)

    # Auto Delete on Time
    autoDeleteDateTime = Column(DateTime(True), nullable=False)

    __table_args__ = (
        Index("idx_Activity_pluginName_uniqueId", pluginName, uniqueId, unique=True),
    )
