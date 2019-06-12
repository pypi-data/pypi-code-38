
import numpy

import numba
Wastewater_numba_spec = [
    ('zeta', numba.float64 [:]),
    ('chi', numba.float64 [:]),
]

class Wastewater (object):
    """Class for waste water process."""

    def __init__ (self, zeta, chi):

        self.zeta = zeta
        self.chi = chi

    def evaluate (self, t):

        arg = 2 * numpy.pi * 1j * t / numpy.float64 (24 * 3600)
        sin = numpy.sin (arg)
        cos = numpy.cos (arg)
        w = numpy.sum (self.zeta * sin + self.chi * cos)
        return numpy.float64 (w.real)
