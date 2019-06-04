from typing import List

from ..axis import Axis
from ..color import Color
from ..enums import LineStyle, Marker
from ..plot import Plot


class Line(Plot):
    def __init__(
        self,
        categories: List[str],
        values: List[float],
        *,
        legend: str=None,
        color=None,
        linewidth=1.0,
        linestyle=LineStyle.SOLID,
        marker=Marker.POINT
    ):
        if len(categories) != len(values):
            raise ValueError(f'Number of categories ({len(categories)}) does not match number of values ({len(values)})')

        self.categories = categories
        self.values = values
        self.legend = legend
        self.color = Color.random() if color is None else color
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.marker = marker

    def build_x_axis(self):
        x = list(range(len(self.categories)))
        return Axis(ticks=x, tick_labels=self.categories)

    def build_y_axis(self):
        return Axis()

    def draw(self):
        self._backend.draw_line(self.legend, self.values, self.color, self.linewidth, self.linestyle, self.marker)
