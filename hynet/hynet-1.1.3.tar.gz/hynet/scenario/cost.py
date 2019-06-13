"""
Representation of (injector) cost functions in *hynet*.
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d

from hynet.types_ import hynet_float_


class PWLFunction:
    """
    Representation of a piecewise linear function ``f: R -> R``.

    Parameters
    ----------
    samples : (numpy.ndarray[.hynet_float_], numpy.ndarray[.hynet_float_]), optional
        Tuple ``(x, y)`` of ``x``- and ``y``-coordinates of sample points of
        the piecewise linear function, i.e., ``(x[0], y[0]), ..., (x[N], y[N])``.
    """

    def __init__(self, samples=None, marginal_price=None):
        """
        Create the PWL function.

        Either the sample points (``samples``) or the marginal price
        (``marginal_price``) may be specified to initialize the function.
        Please refer to the respective properties for more information. By
        default, the object is set to a linear function with slope zero.
        """
        self._x = np.array([0, 1], dtype=hynet_float_)
        self._y = np.array([0, 0], dtype=hynet_float_)

        if samples is not None and marginal_price is not None:
            raise ValueError("Only samples or the marginal price may be specified.")
        elif samples is not None:
            self.samples = samples
        elif marginal_price is not None:
            self.marginal_price = marginal_price
        else:
            self.marginal_price = 0

    @property
    def samples(self):
        """
        Return the tuple ``(x, y)`` of ``x``- and ``y``-coordinate arrays.
        """
        return self._x, self._y

    @samples.setter
    def samples(self, value):
        """
        Set the tuple ``(x, y)`` of ``x``- and ``y``-coordinate arrays.
        """
        if len(value) != 2:
            raise ValueError("Expecting a tuple (x, y) of coordinates.")
        x = np.array(value[0], dtype=hynet_float_)
        y = np.array(value[1], dtype=hynet_float_)
        if len(x) < 2 or len(x) != len(y) or x.ndim != 1 or y.ndim != 1:
            raise ValueError("Expecting a tuple (x, y) of coordinates "
                             "comprising at least two points.")
        if any(np.diff(x) <= 0):
            raise ValueError("The x-coordinate of samples must be "
                             "strictly increasing.")
        (self._x, self._y) = (x, y)

    @property
    def marginal_price(self):
        """
        Return the slope if the function is linear or ``numpy.nan`` otherwise.

        **Remark:** This function requires that the linear function is
        specified using two sample points, i.e., the function will return
        ``numpy.nan`` even if three or more samples lie on a line. The latter
        case should be avoided anyway, as it introduces unnecessary constraints
        in the epigraph representation of the function.
        """
        if len(self._x) != 2:
            return np.nan
        return (np.diff(self._y) / np.diff(self._x)).item()

    @marginal_price.setter
    def marginal_price(self, value):
        """
        Set to this object to a linear function with the slope ``value``.
        """
        self.samples = ((0, 1), (0, value))

    def __repr__(self):
        marginal_price = self.marginal_price
        if not np.isnan(marginal_price):
            return str(marginal_price)
        if len(self._x) == 2:
            return str((np.diff(self._y) / np.diff(self._x)).item())
        return '-'.join(['({0:.1f},{1:.1f})'.format(x, y)
                         for x, y in zip(self._x, self._y)])

    def __eq__(self, other):
        """Return True if the cost functions feature the same sample points."""
        if other is None:
            return False
        return (np.array_equal(self._x, other.samples[0]) and
                np.array_equal(self._y, other.samples[1]))

    def evaluate(self, x):
        """
        Evaluate the function at ``x``, i.e., return ``y = f(x)``.
        """
        result = interp1d(self._x, self._y,
                          kind='linear', fill_value='extrapolate')(x)
        if np.isscalar(x):
            return result.item()
        return result

    def show(self):
        """
        Show the piecewise linear function.
        """
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(self._x, self._y,
                color='xkcd:sea blue', linestyle='-', linewidth=1)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        fig.tight_layout()
        fig.show()
        return fig

    def scale(self, scaling):
        """
        Scale the function by ``scaling``, i.e., ``f(x) -> scaling * f(x)``.
        """
        if scaling < 0:
            raise ValueError("Expecting a nonnegative scaling factor.")
        self._y *= scaling
        return self

    def is_convex(self):
        """
        Return ``True`` if the function is convex.
        """
        if len(self._x) == 2:
            # Affine function
            return True
        # Convex if curvature is nonnegative
        return all(np.diff(np.diff(self._y) / np.diff(self._x)) >= 0)

    def get_epigraph_polyhedron(self):
        """
        Return ``(A, b)`` such that ``f(x) = min{z in R: z*1 >= A*x + b}``.

        Note that ``f`` must be **convex**.
        """
        A = np.diff(self._y) / np.diff(self._x)        # Slope
        b = self._y[1:] - np.multiply(A, self._x[1:])  # Offset
        return A, b
