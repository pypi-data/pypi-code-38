"""``interpu()``: 1D linear interpolation using astropy quantities.

This is a wrapper for numpy.interp for use when using astropy quantities. If
x and xp have different units, xp is converted to the units of x before
interpolation.

:Author: Matthew Burger
"""
import numpy as np


def interpu(x, xp, fp, **kwargs):
    """Return one dimensional interpolated astropy quantities.

    Parameters
    ----------
    x
        The x-coordinates at which to evaluate the interpolated values

    xp
        The x-coordinates of the data points.

    fp
        The y-coordinates of the data points

    x and xp must have compatible units. See `numpy.interp
    <https://docs.scipy.org/doc/numpy/reference/generated/numpy.interp.html>`_
    for details on interpolation.
    """
    fp0 = fp.value
    x0 = x.value
    if x.unit == xp.unit:
        xp0 = xp.value
    else:
        xp0 = xp.to(x.unit).value

    result = np.interp(x0, xp0, fp0, **kwargs)
    return result * fp.unit
