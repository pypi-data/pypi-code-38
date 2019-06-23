import logging
from datetime import datetime

from peek_plugin_inbox._private.PluginNames import inboxTuplePrefix
from vortex.Tuple import Tuple, addTupleType, TupleField

logger = logging.getLogger(__name__)


@addTupleType
class ActivityTuple(Tuple):
    """ Activity Tuple

    An Activity represents an item in the activity screen
    This is a screen that is intended to show actions that have been performed recently
        or events that plugins want in this list.
    
    see InboxAbiABC.NewActivity for documentation.
        
    """
    __tupleType__ = inboxTuplePrefix + 'ActivityTuple'

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

    # Auto Delete on Time
    autoDeleteDateTime: datetime = TupleField()
