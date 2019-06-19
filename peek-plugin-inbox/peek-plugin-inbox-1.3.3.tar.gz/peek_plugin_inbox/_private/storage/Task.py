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

from peek_plugin_base.storage.TypeDecorators import PeekLargeBinary
from peek_plugin_inbox._private.PluginNames import inboxTuplePrefix
from peek_plugin_inbox._private.storage.DeclarativeBase import DeclarativeBase
from peek_plugin_inbox.server.InboxApiABC import NewTask
from sqlalchemy import Column, Index
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from vortex.Tuple import Tuple, addTupleType

logger = logging.getLogger(__name__)


@addTupleType
class Task(Tuple, DeclarativeBase):
    """ Task

    A Task represents the feature rich messages that can be sent from initiator 
    plugins to mobile devices.
    
    see InboxAbiABC.NewTask for documentation.
        
    """
    __tupleType__ = inboxTuplePrefix + 'Task'
    __tablename__ = 'Task'

    # Ensure that the actions are serialised
    __fieldNames__ = ["actions"]

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

    # The confirmation options
    onDeliveredPayloadEnvelope = Column(PeekLargeBinary)
    onCompletedPayloadEnvelope = Column(PeekLargeBinary)
    onDeletedPayloadEnvelope = Column(PeekLargeBinary)
    onDialogConfirmPayloadEnvelope = Column(PeekLargeBinary)

    AUTO_COMPLETE_OFF = NewTask.AUTO_COMPLETE_OFF
    AUTO_COMPLETE_ON_DELIVER = NewTask.AUTO_COMPLETE_ON_DELIVER
    AUTO_COMPLETE_ON_SELECT = NewTask.AUTO_COMPLETE_ON_SELECT
    AUTO_COMPLETE_ON_ACTION = NewTask.AUTO_COMPLETE_ON_ACTION
    AUTO_COMPLETE_ON_DIALOG = NewTask.AUTO_COMPLETE_ON_DIALOG
    autoComplete = Column(Integer, nullable=False, server_default='0')
    autoDeleteDateTime = Column(DateTime(True), nullable=True)

    AUTO_DELETE_OFF = NewTask.AUTO_DELETE_OFF
    AUTO_DELETE_ON_DELIVER = NewTask.AUTO_DELETE_ON_DELIVER
    AUTO_DELETE_ON_SELECT = NewTask.AUTO_DELETE_ON_SELECT
    AUTO_DELETE_ON_ACTION = NewTask.AUTO_DELETE_ON_ACTION
    AUTO_DELETE_ON_COMPLETE = NewTask.AUTO_DELETE_ON_COMPLETE
    AUTO_DELETE_ON_DIALOG = NewTask.AUTO_DELETE_ON_DIALOG
    autoDelete = Column(Integer, nullable=False, server_default='0')

    # The state of this action
    STATE_DELIVERED = 1
    STATE_SELECTED = 2
    STATE_ACTIONED = 4
    STATE_COMPLETED = 8
    STATE_DIALOG_CONFIRMED = 16  # The dialog was achnowledged
    stateFlags = Column(Integer, nullable=False, server_default='0')

    NOTIFY_BY_DEVICE_POPUP = NewTask.NOTIFY_BY_DEVICE_POPUP
    NOTIFY_BY_DEVICE_SOUND = NewTask.NOTIFY_BY_DEVICE_SOUND
    NOTIFY_BY_SMS = NewTask.NOTIFY_BY_SMS
    NOTIFY_BY_EMAIL = NewTask.NOTIFY_BY_EMAIL
    NOTIFY_BY_DEVICE_DIALOG = NewTask.NOTIFY_BY_DEVICE_DIALOG
    notificationRequiredFlags = Column(Integer, nullable=False, server_default='0')
    notificationSentFlags = Column(Integer, nullable=False, server_default='0')

    DISPLAY_AS_TASK = NewTask.PRIORITY_SUCCESS
    DISPLAY_AS_MESSAGE = NewTask.PRIORITY_SUCCESS
    displayAs = Column(Integer, nullable=False, server_default='0')

    PRIORITY_SUCCESS = NewTask.PRIORITY_SUCCESS
    PRIORITY_INFO = NewTask.PRIORITY_INFO
    PRIORITY_WARNING = NewTask.PRIORITY_WARNING
    PRIORITY_DANGER = NewTask.PRIORITY_DANGER
    displayPriority = Column(Integer, nullable=False, server_default='0')

    # The actions for this Task.
    actions = relationship("TaskAction")

    __table_args__ = (
        Index("idx_Task_pluginName_uniqueId", pluginName, uniqueId, unique=True),
    )
