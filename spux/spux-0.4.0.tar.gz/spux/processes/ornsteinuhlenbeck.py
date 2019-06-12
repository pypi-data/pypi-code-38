
import numpy

import numba
OrnsteinUhlenbeck_numba_spec = [
    ('tau', numba.float64),
    ('t', numba.float64),
    ('xi', numba.float64),
]

class OrnsteinUhlenbeck (object):
    """Class for Ornstein-Uhlenbeck process."""

    def __init__ (self, tau):

        self.tau = tau

    def init (self, t, xi):

        self.t = t
        self.xi = xi

    def evaluate (self, t, rng):
        """Evaluate Ornstein-Uhlenbeck process at time 't'."""

        if t < self.t:
            assert t >= self.t, ' :: ERROR: OU process assumes evaluation of increasing time sequence, and not %f < %f' % (t, self.t)
        if t == self.t:
            return self.xi
        dt = t - self.t
        V = 1.0 - numpy.exp (-2 * dt / self.tau)
        E = self.xi * numpy.exp (-dt / self.tau)
        self.xi = rng.normal (loc=E, scale=numpy.sqrt (V))
        self.t = t
        return numpy.float64 (self.xi)
