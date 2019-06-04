from typing import List

from ..axis import Axis
from ..enums import LineStyle, Marker
from ..plot import Plot
from ..color import Color


class Stem(Plot):
    def __init__(
        self,
        timesteps: List[float],
        outputs: List[float],
        *,
        legend=None,
        color=None,
        linewidth=1.0,
        linestyle=LineStyle.SOLID,
        marker=Marker.CIRCLE
    ):
        if len(timesteps) != len(outputs):
            raise ValueError(f'Number of timesteps ({len(timesteps)}) does not match number of outputs ({len(outputs)})')
        self.x = timesteps
        self.y = outputs
        self.legend = legend
        self.color = Color.random() if color is None else color
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.marker = marker

    def build_x_axis(self) -> Axis:
        return Axis()

    def build_y_axis(self) -> Axis:
        return Axis()

    def draw(self):
        self._backend.draw_stem(self.legend, self.x, self.y, self.color, self.linewidth, self.linestyle, self.marker)

