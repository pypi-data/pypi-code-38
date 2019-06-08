# -*- coding: utf-8 -*-

import enum
import weakref

from typing import Dict, Optional

from .mpl import (
    FigureCanvas,
    Figure,
    Axes,
    KeyEvent,
    MouseEvent,
    PickEvent,
    LocationEvent,
    ResizeEvent,
    CloseEvent,
    DrawEvent,
)

from ._types import (
    MplObject_Type,
    EventHandler_Type,
    WeakRefFigure_Type,
)

from ._logging import logger


class MplEvent(enum.Enum):
    """Defines enumeration for all actual matplotlib events

    .. note::
        The values of enum items represent original matplotlib event names.

    """

    KEY_PRESS = 'key_press_event'
    """key is pressed"""

    KEY_RELEASE = 'key_release_event'
    """key is released"""

    MOUSE_BUTTON_PRESS = 'button_press_event'
    """mouse button is pressed"""

    MOUSE_BUTTON_RELEASE = 'button_release_event'
    """mouse button is released"""

    MOUSE_MOVE = 'motion_notify_event'
    """mouse motion"""

    MOUSE_WHEEL_SCROLL = 'scroll_event'
    """mouse scroll wheel is rolled"""

    FIGURE_RESIZE = 'resize_event'
    """figure canvas is resized"""

    FIGURE_ENTER = 'figure_enter_event'
    """mouse enters a figure"""

    FIGURE_LEAVE = 'figure_leave_event'
    """mouse leaves a figure"""

    FIGURE_CLOSE = 'close_event'
    """a figure is closed"""

    AXES_ENTER = 'axes_enter_event'
    """mouse enters a new axes"""

    AXES_LEAVE = 'axes_leave_event'
    """mouse leaves an axes"""

    PICK = 'pick_event'
    """an object in the canvas is selected"""

    DRAW = 'draw_event'
    """canvas draw (but before screen update)"""

    def make_connection(self, mpl_obj: MplObject_Type, handler: EventHandler_Type,
                        connect: bool = True) -> 'MplEventConnection':
        """Creates connection between event with this type and handler and returns instance of MplEventConnection

        This method can be used as shortcut for `MplEventConnection` construction.

        Parameters
        ----------
        mpl_obj : mpl.Figure, mpl.Axes, mpl.FigureCanvasBase
            Matplotlib object: Figure, Axes or Canvas
        handler : callable
            Event handler function/callable with signature: ``handler(event: mpl.Event)``.
        connect : bool
            If this flag is True, event and handler will be connected immediately

        Returns
        -------
        conn : MplEventConnection
            Connection object

        Raises
        ------
        TypeError
            If ``mpl_object`` has incorrect type.
        ValueError
            If mpl figure object has no a canvas.

        Examples
        --------

        .. code-block:: python

            from matplotlib import pyplot as plt
            from mpl_events import MplEvent

            def close_handler(event):
                print('figure closing')

            figure = plt.figure()
            conn = MplEvent.FIGURE_CLOSE.make_connection(figure, close_handler)
            plt.show()

        See Also
        --------
        MplEventConnection

        """
        return MplEventConnection(mpl_obj, self, handler, connect)


def _get_mpl_figure(mpl_obj: MplObject_Type) -> Figure:
    if isinstance(mpl_obj, Axes):
        figure = mpl_obj.figure
    elif isinstance(mpl_obj, Figure):
        figure = mpl_obj
    elif isinstance(mpl_obj, FigureCanvas):
        figure = mpl_obj.figure
    else:
        raise TypeError(
            'Invalid MPL object {}. '.format(mpl_obj)
            + 'The object must be one of these types: "Axes", "Figure" or "FigureCanvas".'
        )

    if not figure.canvas:
        raise ValueError('The figure object has no a canvas.')

    return figure


class MplEventConnection:
    """Implements the connection to matplotlib event

    The class manages the connection between a matplotlib event and a handler callable.

    This class is high level wrapper for ``canvas.mpl_connect``/``canvas.mpl_disconnect`` matplotlib API.

    Parameters
    ----------
    mpl_obj : mpl.Figure, mpl.Axes, mpl.FigureCanvasBase
        Matplotlib object: Figure, Axes or Canvas
    event : MplEvent
        Event type
    handler : callable
        Event handler function/callable with signature: ``handler(event: mpl.Event)``.
    connect : bool
        If this flag is True, event and handler will be connected immediately

    Attributes
    ----------
    figure
    event
    handler
    id
    valid
    connected

    Raises
    ------
    TypeError
        If ``mpl_object`` has incorrect type.
    ValueError
        If mpl figure object has no a canvas.

    Examples
    --------

    .. code-block:: python

        from mpl_events import MplEventConnection, MplEvent, mpl

        def close_handler(event: mpl.CloseEvent):
            print('figure closing')

        figure = plt.figure()
        conn = MplEventConnection(figure, MplEvent.FIGURE_CLOSE, close_handler)
        plt.show()

    """

    def __init__(self, mpl_obj: MplObject_Type,
                 event: MplEvent,
                 handler: EventHandler_Type,
                 connect: bool = True):
        self._figure = weakref.ref(_get_mpl_figure(mpl_obj))
        self._event = event
        self._handler = handler
        self._id = -1

        if connect:
            self.connect()

    def __del__(self):
        self.disconnect()

    def __repr__(self) -> str:
        return '{}(event=<{}:{}>, handler={}, id={})'.format(
            type(self).__name__, self.event.name,
            self.event.value, self.handler, self.id)

    @property
    def figure(self) -> WeakRefFigure_Type:
        """Returns the reference to the related matplotlib figure

        Returns
        -------
        figure : Figure
            Matplotlib figure that is related to this connection
        """
        return self._figure()

    @property
    def event(self) -> MplEvent:
        """Returns matplotlib event type as MplEvent enum item

        Returns
        -------
        event : :class:`MplEvent`
            Event type that is related to this connection
        """
        return self._event

    @property
    def handler(self) -> EventHandler_Type:
        """Returns the event handler callable

        Returns
        -------
        handler : callable
            Event handler callable that is related to this connection
        """
        return self._handler

    @property
    def id(self) -> int:
        """Returns matplotlib event connection id

        Returns
        -------
        id : int
            Matplotlib connection identifier
        """
        return self._id

    @property
    def valid(self) -> bool:
        """Retuns True if the connection is valid

        The connection is valid if the related matplotlib figure has not been destroyed.

        Returns
        valid : bool
            True if the connection is valid
        """
        return self.figure is not None

    @property
    def connected(self) -> bool:
        """Returns True if the handler is connected to the event

        Returns
        -------
        connected : bool
            True if the handler is connected to the event
        """
        return self._id > 0 and self.valid

    def connect(self):
        """Connects the handler to the event
        """
        if not self.valid:
            logger.error('Figure ref is dead')
            self._id = -1
            return

        if self.connected:
            return

        self._id = self.figure.canvas.mpl_connect(self._event.value, self._handler)
        logger.debug('"%s" was connected to %s handler (id=%d)',
                     self.event.value, self._handler, self._id)

    def disconnect(self):
        """Disconnects the handler from the event
        """
        if not self.connected:
            return

        self.figure.canvas.mpl_disconnect(self._id)
        logger.debug('"%s" was disconnected from %s handler (id=%d)',
                     self.event.value, self._handler, self._id)
        self._id = -1


def mpl_event_handler(event_type: MplEvent):
    """Marks the decorated method as given matplotlib event handler

    .. note::
        This decorator should be used only for methods of classes that
        inherited from :class:`MplEventDispatcher` class.

    This decorator can be used for reassignment event handlers in a dispatcher class.

    Examples
    --------

    .. code-block:: python

        from mpl_events import MplEventDispatcher, mpl_event_handler, mpl

        class MyEventDispatcher(MplEventDispatcher):
            @mpl_event_handler(MplEvent.KEY_PRESS)
            def on_my_key_press(self, event: mpl.KeyPress):
                pass
    """
    class HandlerDescriptor:
        """Adds handler method name to event handlers mapping
        """
        def __init__(self, handler):
            self.handler = handler

        def __get__(self, obj, cls=None):
            return self.handler.__get__(obj, cls)

        def __set_name__(self, owner, name):
            if 'mpl_event_handlers' not in owner.__dict__:
                owner.mpl_event_handlers = getattr(owner, 'mpl_event_handlers', {}).copy()
            owner.mpl_event_handlers[event_type] = name

    return HandlerDescriptor


class MplEventDispatcher:
    """The base dispatcher class for connecting and handling all matplotlib events

    You can use this class as base class for your matplotlib event dispatcher.

    `MplEventDispatcher` class provides API (handler methods interface) for all matplotlib events.
    You may override and implement some of these methods for handling corresponding events.

    Parameters
    ----------
    mpl_obj : mpl.Figure, mpl.Axes, mpl.FigureCanvasBase
        Matplotlib object: Figure, Axes or Canvas
    connect : bool
        If this flag is True (default), all events and handlers will be connected immediately

    Attributes
    ----------
    figure
    valid
    mpl_connections

    Raises
    ------
    TypeError
        If ``mpl_object`` has incorrect type.
    ValueError
        If mpl figure object has no a canvas.

    Examples
    --------

    .. code-block:: python

        from matplotlib import pyplot as plt
        from mpl_events import MplEventDispatcher, mpl

        class KeyEventDispatcher(MplEventDispatcher):

            disable_default_handlers = True

            def on_key_press(self, event: mpl.KeyEvent):
                print(f'Pressed key {event.key}')

            def on_key_release(self, event: mpl.KeyEvent):
                print(f'Released key {event.key}')

        figure = plt.figure()
        dispatcher = KeyEventDispatcher(figure)
        plt.show()
    """

    mpl_event_handlers: Dict[MplEvent, str] = {}

    disable_default_handlers: bool = False
    """If flag is True default handlers will be disabled

    See Also
    --------
    disable_default_key_press_handler
    """

    def __init__(self, mpl_obj: MplObject_Type, connect: bool = True):
        self._figure = weakref.ref(_get_mpl_figure(mpl_obj))
        self._mpl_connections = self._make_mpl_connections()

        if self.disable_default_handlers:
            disable_default_key_press_handler(mpl_obj)
        if connect:
            self.mpl_connect()

    def __del__(self):
        self.mpl_disconnect()

    def _make_mpl_connections(self) -> Dict[MplEvent, MplEventConnection]:
        conns = {}

        for event, handler_name in self.mpl_event_handlers.items():
            handler = self._get_handler(handler_name)
            if handler:
                conn = event.make_connection(self.figure, handler, connect=False)
                conns[event] = conn

        return conns

    def _get_handler(self, handler_name: str) -> Optional[EventHandler_Type]:
        for cls in type(self).__mro__:
            if cls is not MplEventDispatcher and handler_name in cls.__dict__:
                handler = getattr(self, handler_name)
                if callable(handler):
                    logger.debug('Found event handler: %s', handler)
                    return handler
                else:
                    logger.warning('"%s": %s is not callable', handler_name, handler)

    @property
    def figure(self) -> WeakRefFigure_Type:
        """Returns the reference to the related matplotlib figure

        Returns
        -------
        figure : Figure
            Matplotlib figure that is related to this dispatcher
        """
        return self._figure()

    @property
    def valid(self) -> bool:
        """Retuns True if the dispatcher is valid

        The dispatcher is valid if the related matplotlib figure has not been destroyed.

        Returns
        valid : bool
            True if the dispatcher is valid
        """
        return self.figure is not None

    @property
    def mpl_connections(self) -> Dict[MplEvent, MplEventConnection]:
        """Returns the mapping for all connections for this event dispatcher instance

        Returns mapping in this form::

            {
                event_type1: connection1,
                event_type2: connection2,
            }

        Returns
        -------
        mpl_connections : Dict[MplEvent, MplEventConnection]
            The mapping for all connections for this event dispatcher instance
        """
        return self._mpl_connections

    def mpl_connect(self):
        """Connects the implemented event handlers to the related matplotlib events for this instance
        """
        if not self.valid:
            logger.error('The figure ref is dead')
            return

        self.mpl_disconnect()
        for conn in self._mpl_connections.values():
            conn.connect()

    def mpl_disconnect(self):
        """Disconnects the implemented handlers from the related matplotlib events for this instance
        """
        if not self.valid:
            return

        for conn in self._mpl_connections.values():
            conn.disconnect()

    # ########################################################################
    # The methods below define API for handling matplotlib events.
    # All handler methods of the base class (MplEventDispatcher) never
    # connected to events. Any of these methods can be implemented in
    # subclasses and will be connected to relevant events automatically.
    # ########################################################################

    @mpl_event_handler(MplEvent.KEY_PRESS)
    def on_key_press(self, event: KeyEvent):
        """KeyEvent -- key is pressed
        """

    @mpl_event_handler(MplEvent.KEY_RELEASE)
    def on_key_release(self, event: KeyEvent):
        """KeyEvent -- key is released
        """

    @mpl_event_handler(MplEvent.MOUSE_BUTTON_PRESS)
    def on_mouse_button_press(self, event: MouseEvent):
        """MouseEvent -- mouse button is pressed
        """

    @mpl_event_handler(MplEvent.MOUSE_BUTTON_RELEASE)
    def on_mouse_button_release(self, event: MouseEvent):
        """MouseEvent -- mouse button is released
        """

    @mpl_event_handler(MplEvent.MOUSE_MOVE)
    def on_mouse_move(self, event: MouseEvent):
        """MouseEvent -- mouse motion
        """

    @mpl_event_handler(MplEvent.MOUSE_WHEEL_SCROLL)
    def on_mouse_wheel_scroll(self, event: MouseEvent):
        """MouseEvent -- mouse scroll wheel is rolled
        """

    @mpl_event_handler(MplEvent.FIGURE_RESIZE)
    def on_figure_resize(self, event: ResizeEvent):
        """ResizeEvent -- figure canvas is resized
        """

    @mpl_event_handler(MplEvent.FIGURE_ENTER)
    def on_figure_enter(self, event: LocationEvent):
        """LocationEvent -- mouse enters a new figure
        """

    @mpl_event_handler(MplEvent.FIGURE_LEAVE)
    def on_figure_leave(self, event: LocationEvent):
        """LocationEvent -- mouse leaves a figure
        """

    @mpl_event_handler(MplEvent.FIGURE_CLOSE)
    def on_figure_close(self, event: CloseEvent):
        """CloseEvent -- a figure is closed
        """

    @mpl_event_handler(MplEvent.AXES_ENTER)
    def on_axes_enter(self, event: LocationEvent):
        """LocationEvent -- mouse enters a new axes
        """

    @mpl_event_handler(MplEvent.AXES_LEAVE)
    def on_axes_leave(self, event: LocationEvent):
        """LocationEvent -- mouse leaves an axes
        """

    @mpl_event_handler(MplEvent.PICK)
    def on_pick(self, event: PickEvent):
        """PickEvent -- an object in the canvas is selected
        """

    @mpl_event_handler(MplEvent.DRAW)
    def on_draw(self, event: DrawEvent):
        """DrawEvent -- canvas draw (but before screen update)
        """


def disable_default_key_press_handler(mpl_obj: MplObject_Type):
    """Disables default key_press handling for given figure/canvas

    The default key handler using the toolmanager.

    Parameters
    ----------
    mpl_obj : mpl.Figure, mpl.Axes, mpl.FigureCanvasBase
        Matplotlib object: Figure, Axes or Canvas

    """
    figure = _get_mpl_figure(mpl_obj)
    cid = figure.canvas.manager.key_press_handler_id
    if cid:
        figure.canvas.mpl_disconnect(cid)
