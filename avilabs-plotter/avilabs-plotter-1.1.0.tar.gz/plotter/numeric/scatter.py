from typing import List

from ..axis import Axis
from ..color import Color
from ..enums import Marker
from ..plot import Plot


class Scatter(Plot):
    def __init__(
        self,
        x: List[float],
        y: List[float],
        *,
        legend=None,
        color=None,
        marker=Marker.POINT
    ):
        self.x = x
        self.y = y
        self.legend = legend
        self.color = Color.random() if color is None else color
        self.marker = marker

    def build_x_axis(self) -> Axis:
        return Axis()

    def build_y_axis(self) -> Axis:
        return Axis()

    def draw(self):
        self._backend.draw_scatter(self.legend, self.x, self.y, self.color, self.marker)
