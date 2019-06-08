# -*- coding: utf-8 -*-

"""
The module contains some event filters that can be useful

"""

import weakref

from ._base import MplEventDispatcher, MplEvent
from ._types import MplEvent_Type
from ._logging import logger


class LoggingEventFilter:
    """Logging events

    The filter logs all events that will be handled.

    .. note::

        This event filter should be append to end of of event filters list.

    """

    def __call__(self, obj: MplEventDispatcher, event: MplEvent_Type):
        logger.info('%s (%s) %s', obj, MplEvent(event.name), event)


class MouseDoubleClickReleaseEventFilter:
    """Sets correct value of dblclick flag to MOUSE_BUTTON_RELEASE event

    The filter adds  true ``dblclick`` flag to ``MOUSE_BUTTON_RELEASE`` event
    if ``dblclick`` is True in previous ``MOUSE_BUTTON_PRESS`` event.
    """

    def __init__(self):
        self._double_clicks = weakref.WeakKeyDictionary()

    def __call__(self, obj: MplEventDispatcher, event: MplEvent_Type):
        event_type = MplEvent(event.name)

        if event_type not in {MplEvent.MOUSE_BUTTON_PRESS,
                              MplEvent.MOUSE_BUTTON_RELEASE}:
            return

        if event_type == MplEvent.MOUSE_BUTTON_PRESS:
            self._double_clicks[obj] = event.dblclick

        if event_type == MplEvent.MOUSE_BUTTON_RELEASE:
            if obj in self._double_clicks and self._double_clicks[obj]:
                self._double_clicks[obj] = False
                event.dblclick = True
