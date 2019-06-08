# -*- coding: utf-8 -*-

import typing as t

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

MplEvent_Type = t.Union[KeyEvent, MouseEvent, PickEvent, LocationEvent, ResizeEvent, CloseEvent, DrawEvent]
MplObject_Type = t.Union[Axes, Figure, FigureCanvas]
EventHandler_Type = t.Callable[[MplEvent_Type], None]
EventFilter_Type = t.Callable[['MplEventDispatcher', MplEvent_Type], t.Optional[bool]]
WeakRefFigure_Type = t.Optional[Figure]
