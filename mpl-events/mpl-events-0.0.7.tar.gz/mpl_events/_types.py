# -*- coding: utf-8 -*-

import typing as t

from .mpl import (
    FigureCanvas,
    Figure,
    Axes,
    Event,
)

MplObject_Type = t.Union[Axes, Figure, FigureCanvas]
EventHandler_Type = t.Callable[[Event], None]
WeakRefFigure_Type = t.Optional[Figure]
