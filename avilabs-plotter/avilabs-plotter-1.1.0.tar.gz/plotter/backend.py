from abc import ABC, abstractmethod
from typing import List

from .frame import Frame
from .chart import Chart
from .color import Color
from .enums import LineStyle, Marker


class Backend(ABC):
    @abstractmethod
    def set_frame(self, frame: Frame):
        pass

    @abstractmethod
    def add_chart(self, chart: Chart):
        pass

    @abstractmethod
    def draw_hbar(self, legend: str, values: List[float], color: Color, height: float):
        pass

    @abstractmethod
    def draw_line(self, legend: str, y: List[float], color: Color, linewidth: float, linestyle: LineStyle):
        pass

    @abstractmethod
    def draw_vbar(self, lenged: str, values: List[float], color: Color, width: float):
        pass

    @abstractmethod
    def draw_scatter(self, legend: str, x: List[float], y: List[float], color: Color, marker: Marker):
        pass

    @abstractmethod
    def draw_graph(self, legend: str, x: List[float], y: List[float], color: Color, linewidth: float, linestyle: LineStyle):
        pass

    @abstractmethod
    def draw_rgbimg(self, img):
        pass

    @abstractmethod
    def draw_grayimg(self, img):
        pass
