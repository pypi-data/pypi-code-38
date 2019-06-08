# -*- coding: utf-8 -*-

import matplotlib.axes as _mpl_ax
import matplotlib.figure as _mpl_fig
import matplotlib.backend_bases as _mpl_bb

FigureCanvas = _mpl_bb.FigureCanvasBase
Figure = _mpl_fig.Figure
Axes = _mpl_ax.Axes

Event = _mpl_bb.Event
KeyEvent = _mpl_bb.KeyEvent
MouseEvent = _mpl_bb.MouseEvent
PickEvent = _mpl_bb.PickEvent
LocationEvent = _mpl_bb.LocationEvent
ResizeEvent = _mpl_bb.ResizeEvent
CloseEvent = _mpl_bb.CloseEvent
DrawEvent = _mpl_bb.DrawEvent
