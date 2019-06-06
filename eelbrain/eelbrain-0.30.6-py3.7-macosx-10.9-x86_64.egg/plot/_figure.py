"""Figures for custom plots"""
from ._base import EelFigure, Layout, XAxisMixin


class Figure(EelFigure):
    """Empty figure

    Parameters
    ----------
    nax : int (optional)
        Create this many axes (default is to not create any axes).
    ...
        Also accepts :ref:`general-layout-parameters`.
    autoscale : bool
        Autoscale data axes (default False).
    """
    def __init__(self, nax=0, *args, **kwargs):
        layout = Layout(nax, 1, 2, *args, **kwargs)
        EelFigure.__init__(self, None, layout)

    def show(self):
        self._show()


class XFigure(XAxisMixin, Figure):

    def __init__(self, nax, xmin, xmax, xlim, *args, **kwargs):
        Figure.__init__(self, nax, *args, **kwargs)
        self._args = (xmin, xmax, xlim)

    def show(self):
        XAxisMixin.__init__(self, *self._args)
        Figure.show(self)
