from abc import ABC, abstractmethod

from .axis import Axis


class Plot(ABC):
    def __init__(self):
        self._backend = None

    @abstractmethod
    def build_x_axis(self) -> Axis:
        pass

    @abstractmethod
    def build_y_axis(self) -> Axis:
        pass

    @abstractmethod
    def draw(self):
        pass
