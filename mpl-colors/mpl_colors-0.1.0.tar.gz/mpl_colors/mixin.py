from typing import NamedTuple, Tuple
import colorsys

from colour import Color


class RgbTuple(NamedTuple):
    r: float
    g: float
    b: float

    def color(self) -> Color:
        return Color(rgb=self.value)

    def hex(self) -> str:
        return self.color().hex_l

    def hsl(self) -> Tuple[float, float, float]:
        return self.color().hsl

    def rgb(self) -> Tuple[float, float, float]:
        return self.value

    def rgba(self, a=1.0) -> Tuple[float, float, float, float]:
        return self.value + (a,)

    def web(self) -> str:
        return self.color().web

    def hsv(self) -> Tuple[float, float, float]:
        return colorsys.rgb_to_hsv(*self.value)

    def yiq(self) -> Tuple[float, float, float]:
        return colorsys.rgb_to_yiq(*self.value)
