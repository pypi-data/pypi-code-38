from typing import List

from ..axis import Axis
from ..color import Color
from ..plot import Plot


class VerticalBar(Plot):
    def __init__(
        self,
        categories: List[str],
        values: List[str],
        *,
        legend: str=None,
        color=None,
        width=0.5
    ):
        if len(categories) != len(values):
            raise ValueError(f'Number of categories ({len(categories)}) does not match number of values ({len(values)})')

        self.categories = categories
        self.values = values
        self.legend = legend
        self.color = Color.random() if color is None else color
        self.width = width

    def build_x_axis(self):
        x = list(range(len(self.categories)))
        return Axis(ticks=x, tick_labels=self.categories)

    def build_y_axis(self):
        return Axis()

    def draw(self):
        self._backend.draw_vbar(self.legend, self.values, self.color, self.width)
