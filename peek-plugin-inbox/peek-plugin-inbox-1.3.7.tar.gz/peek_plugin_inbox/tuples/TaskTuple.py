import logging
from datetime import datetime

from peek_plugin_inbox._private.PluginNames import inboxTuplePrefix
from peek_plugin_inbox.server.InboxApiABC import NewTask
from vortex.Tuple import Tuple, addTupleType, TupleField

logger = logging.getLogger(__name__)


@addTupleType
class TaskTuple(Tuple):
    """ Task Tuple

    A Task represents the feature rich messages that can be sent from initiator 
    plugins to mobile devices.
    
    see InboxAbiABC.NewTask for documentation.
        
    """
    __tupleType__ = inboxTuplePrefix + 'TaskTuple'

    pluginName: str = TupleField()
    uniqueId: str = TupleField()
    userId: str = TupleField()
    dateTime: datetime = TupleField()

    # The display properties of the task
    title: str = TupleField()
    description: str = TupleField()
    iconPath: str = TupleField()

    # The mobile-app route to open when this task is selected
    routePath: str = TupleField()
    routeParamJson: str = TupleField()

    # The state of this action
    STATE_DELIVERED = 1
    STATE_SELECTED = 2
    STATE_ACTIONED = 4
    STATE_COMPLETED = 8
    STATE_DIALOG_CONFIRMED = 16  # The dialog was acknowledged
    stateFlags: int = TupleField()

    NOTIFY_BY_DEVICE_POPUP = NewTask.NOTIFY_BY_DEVICE_POPUP
    NOTIFY_BY_DEVICE_SOUND = NewTask.NOTIFY_BY_DEVICE_SOUND
    NOTIFY_BY_SMS = NewTask.NOTIFY_BY_SMS
    NOTIFY_BY_EMAIL = NewTask.NOTIFY_BY_EMAIL
    NOTIFY_BY_DEVICE_DIALOG = NewTask.NOTIFY_BY_DEVICE_DIALOG
    notificationSentFlags: int = TupleField()

    DISPLAY_AS_TASK = NewTask.PRIORITY_SUCCESS
    DISPLAY_AS_MESSAGE = NewTask.PRIORITY_SUCCESS
    displayAs: int = TupleField()

    PRIORITY_SUCCESS = NewTask.PRIORITY_SUCCESS
    PRIORITY_INFO = NewTask.PRIORITY_INFO
    PRIORITY_WARNING = NewTask.PRIORITY_WARNING
    PRIORITY_DANGER = NewTask.PRIORITY_DANGER
    displayPriority: int = TupleField()
