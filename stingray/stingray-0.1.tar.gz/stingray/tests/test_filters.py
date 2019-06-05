import numpy as np
from astropy.modeling import models

from ..filters import Window1D, Optimal1D


class TestFilters(object):

    @classmethod
    def setup_class(self):
        self.x = np.linspace(0, 10, 100)

        self.amplitude_0 = 5.
        self.x_0_0 = 5.
        self.fwhm_0 = 1.
        self.amplitude_1 = -5
        self.lorentz = models.Lorentz1D(amplitude=self.amplitude_0,
                                        x_0=self.x_0_0, fwhm=self.fwhm_0)
        self.const = models.Const1D(amplitude=self.amplitude_1)
        self.model = self.lorentz + self.const
        self.y = self.model(self.x)

    def test_window(self):
        tophat_filter = Window1D(self.model)
        filtered_y = self.y * tophat_filter(self.x)
        filter_w = [1. if np.abs(x_i - self.x_0_0) <= self.fwhm_0 / 2 else 0.
                    for x_i in self.x]
        y_w = self.y * filter_w
        assert np.all(filtered_y == y_w)

    def test_optimal(self):
        optimal_filter = Optimal1D(self.model)
        filtered_y = self.y * optimal_filter(self.x)
        filter_o = (self.lorentz / self.model)(self.x)
        y_o = self.y * filter_o
        assert np.all(filtered_y == y_o)
