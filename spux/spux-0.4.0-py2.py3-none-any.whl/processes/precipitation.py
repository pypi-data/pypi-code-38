
import numpy

import numba
Precipitation_numba_spec = [
    ('g', numba.float64[:]),
    ('a', numba.float64[:]),
    ('b', numba.float64[:]),
    ('c', numba.float64[:]),
    ('xi_1', numba.float64),
    ('xi_2', numba.float64),
]

class Precipitation (object):
    """Class for Precipitation process."""

    def __init__ (self, g, a, b, c, xi_1, xi_2):

        self.g = g
        self.a = a
        self.b = b
        self.c = c
        self.xi_1 = xi_1
        self.xi_2 = xi_2

    def evaluate (self, xi):

        mode = 0 if xi <= self.xi_1 else (1 if xi <= self.xi_2 else 2)
        x = self.a [mode] * (xi - self.b [mode]) ** self.g [mode] + self.c [mode]
        return numpy.float64 (x)

    def inverse (self, x):

        x_1 = self.evaluate (self.xi_1)
        x_2 = self.evaluate (self.xi_2)
        mode = 0 if x <= x_1 else (1 if x <= x_2 else 2)
        if mode == 0:
            xi = self.xi_1
        else:
            xi = ((x - self.c [mode]) / self.a [mode]) ** (1.0 / self.g [mode]) + self.b [mode]
        return numpy.float64 (xi)
