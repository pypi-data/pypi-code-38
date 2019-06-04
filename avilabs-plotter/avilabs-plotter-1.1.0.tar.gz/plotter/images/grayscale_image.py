from ..axis import Axis
from ..plot import Plot
from ..color import ColorMap


class GrayscaleImage(Plot):
    def __init__(self, img, colormap=ColorMap.GRAY):
        self.img = img
        self.colormap = colormap

    def build_x_axis(self):
        return Axis()

    def build_y_axis(self):
        return Axis()

    def draw(self):
        self._backend.draw_grayimg(self.img, self.colormap)
