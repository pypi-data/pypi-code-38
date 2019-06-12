import numpy as np
#
import pymap3d.haversine as haver


def findClosestAzel(az, el, azpts, elpts):
    """
    assumes that azpts, elpts are each list of 1-D arrays or 2-D arrays
    az: 2-D Numpy array of azimuths in the image
    el: 2-D Numpy array of elevations in the image
    azpts: 1-D or 2-D Numpy array of azimuth points to see where nearest neighbor index is
    elpts: 1-D or 2-D Numpy array of azimuth points to see where nearest neighbor index is
    """
    assert az.ndim == 2
    assert az.shape == el.shape

    azpts = np.atleast_1d(azpts)
    elpts = np.atleast_1d(elpts)

    assert azpts.shape == elpts.shape

    az = np.ma.masked_invalid(az)
    el = np.ma.masked_invalid(el)

    az = np.radians(az)
    el = np.radians(el)
    azpts = np.radians(azpts)
    elpts = np.radians(elpts)

    if np.ma.is_masked(azpts):
        azpts = azpts.compressed()
        elpts = elpts.compressed()
    else:
        azpts = np.atleast_1d(azpts).ravel()
        elpts = np.atleast_1d(elpts).ravel()

    # can be FAR FAR faster than scipy.spatial.distance.cdist()
    nearRow, nearCol = _findindex(az, el, azpts, elpts)

    return nearRow, nearCol


def _findindex(az0, el0, az, el):
    """
    inputs:
    ------
    az0, el0: N-D array of azimuth, elevation. May be masked arrays
    az, el: 1-D vectors of azimuth, elevation points from other camera to find closest angle for joint FOV.

    output:
    row, col:  index of camera 0 closest to camera 1 FOV for each unmasked pixel

    I think with some minor tweaks this could be numba.jit if too slow.
    """

    assert az0.size == el0.size  # just for clarity
    assert az.ndim == el.ndim == 1, 'expect vector of test points'
    ic = np.empty(az.size, dtype=int)

    for i, (a, e) in enumerate(zip(az, el)):
        # we do this point by point because we need to know the closest pixel for each point
        # errang = haver.anglesep(az,el, apt,ept, deg=False)
        ic[i] = haver.anglesep_meeus(az0, el0, a, e, deg=False).argmin()

    """
    THIS UNRAVEL_INDEX MUST BE ORDER = 'C'
    """
    r, c = np.unravel_index(ic, az0.shape, order='C')

    mask = (c == 0) | (c == az0.shape[1] - 1) | (r == 0) | (r == az0.shape[0] - 1)

    r = np.ma.masked_where(mask, r)
    c = np.ma.masked_where(mask, c)

    return r, c
