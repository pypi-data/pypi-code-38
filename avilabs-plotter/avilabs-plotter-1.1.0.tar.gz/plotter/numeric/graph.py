from typing import Callable, List, Tuple, Union

import numpy as np

from ..axis import Axis
from ..color import Color
from ..enums import LineStyle
from ..plot import Plot


class Graph(Plot):
    def __init__(
        self,
        x_range: Tuple[float, float],
        func: Union[Callable[[float], float], Callable[[List[float]], float]],
        *,
        legend=None,
        color=None,
        linewidth=1.0,
        linestyle=LineStyle.SOLID
    ):
        self.x = np.linspace(x_range[0], x_range[1], self._numpoints(x_range), endpoint=True)
        self.y = None
        try:
            self.y = func(self.x)
        except Exception as err:
            pass  # Not a vector function

        self.y = [func(v) for v in self.x] if self.y is None else self.y

        self.legend = legend
        self.color = Color.random() if color is None else color
        self.linewidth = linewidth
        self.linestyle = linestyle

    def build_x_axis(self) -> Axis:
        return Axis()

    def build_y_axis(self) -> Axis:
        return Axis()

    def draw(self):
        self._backend.draw_graph(self.legend, self.x, self.y, self.color, self.linewidth, self.linestyle)

    def _numpoints(self, x_range):
        return 500 * (x_range[1] - x_range[0])
