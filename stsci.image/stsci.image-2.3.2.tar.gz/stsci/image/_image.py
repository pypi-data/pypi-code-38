from __future__ import division

import numpy as np
from scipy.signal import correlate2d
from scipy import ndimage


def _translate(a, dx, dy, output=None, mode="full", cval=0.0):
    """_translate does positive sub-pixel shifts using bilinear
    interpolation.
    """

    assert 0 <= dx < 1.0
    assert 0 <= dy < 1.0

    w = (1-dy) * (1-dx)
    x = (1-dy) * dx
    y = (1-dx) * dy
    z = dx * dy

    kernel = np.array([
        [ z, y ],
        [ x, w ],
        ])

    if output is not None:
        raise NotImplementedError(
            'scipy.signal.correlate2d does not accept output keyword')

    return correlate2d(a, kernel, mode=mode, fillvalue=cval)


def translate(a, sdx, sdy, output=None, mode="nearest", cval=0.0):
    """translate performs a translation of 'a' by (sdx, sdy)
    storing the result in 'output'.

    Parameters
    ----------
    sdx, sdy : float
        Value to translate image in x and y, respectively

    output : ndarray
        Output array

    mode : {'nearest','wrap','reflect','constant'}
        Supported 'mode's include::

            'nearest'   elements beyond boundary come from nearest edge pixel.
            'wrap'      elements beyond boundary come from the opposite array edge.
            'reflect'   elements beyond boundary come from reflection on same array
                        edge.
            'constant'  elements beyond boundary are set to 'cval'

    cval : float
        Value to use if mode set to 'constant'.
    """

    a = np.asarray(a)

    sdx, sdy = -sdx, -sdy     # Flip sign to match IRAF sign convention

    # _translate works "backwords" due to implementation of 2x2 correlation.
    if sdx >= 0 and sdy >= 0:
        rotation = 2
        dx, dy = abs(sdx), abs(sdy)
    elif sdy < 0 and sdx >= 0:
        rotation = 1
        dx, dy = abs(sdy), abs(sdx)
    elif sdx < 0 and sdy >= 0:
        rotation = 3
        dx, dy = abs(sdy), abs(sdx)
    elif sdx < 0 and sdy < 0:
        rotation = 0
        dx, dy = abs(sdx), abs(sdy)

    b = np.rot90(a, rotation)
    c = ndimage.shift(b, (int(dx), int(dy)), mode=mode)
    d = _translate(c, dx % 1, dy % 1, output, 'full', cval)
    if output is not None:
        output._copyFrom(np.rot90(output, -rotation%4))
    else:
        return np.rot90(d, -rotation % 4).astype(a.type())
