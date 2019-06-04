from ..axis import Axis
from ..plot import Plot


class RgbImage(Plot):
    def __init__(self, img):
        self.img = img

    def build_x_axis(self):
        return Axis()

    def build_y_axis(self):
        return Axis()

    def draw(self):
        self._backend.draw_rgbimg(self.img)
