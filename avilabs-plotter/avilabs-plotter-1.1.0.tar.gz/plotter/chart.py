from typing import Tuple  # NOQA

from .axis import Axis
from .enums import LegendLocation  # NOQA
from .font import Font


class Chart:
    def __init__(self, backend):
        self._backend = backend
        self._plots = []

        self.legend_location: LegendLocation = None
        self.title = ''
        self.title_font: Font = None
        self.x_axis = Axis()
        self.y_axis = Axis()
        self.grid = False
        self.origin: Tuple[float, float] = None
        self.show_axes = True

    def add(self, plot):
        plot._backend = self._backend

        x_axis = plot.build_x_axis()
        if self.x_axis.is_compatible(x_axis):
            self.x_axis.merge_(x_axis)
        else:
            raise RuntimeError('Incompatible plots in the same chart')

        y_axis = plot.build_y_axis()
        if self.y_axis.is_compatible(y_axis):
            self.y_axis.merge_(y_axis)
        else:
            raise RuntimeError('Incompatible plots in the same chart')

        self._plots.append(plot)
