#
#  utils/numpy.py
#  bxtorch
#
#  Created by Oliver Borchert on May 10, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import numpy as np
import numba

@numba.njit
def intersection_mask(x, y):
    """
    Computes the intersection of the given arrays.

    The arrays are expected to be sorted in ascending order and elements must
    be unique. Otherwise, the result is undefined.

    Parameters:
    -----------
    - x: numpy.ndarray [N]
        Array number one.
    - y: numpy.ndarray [M]
        Array number two.

    Returns:
    --------
    - numpy.ndarray [N]
        A mask for the array passed as first parameter. When applied to the
        first array, it returns the values contained in both arrays.
    """
    mask = np.zeros_like(x)
    
    N, M = (x.shape[0], y.shape[0])
    xp, yp = (0, 0)

    while xp < N and yp < M:
        if x[xp] == y[yp]:
            mask[xp] = 1
            xp += 1
            yp += 1
        elif x[xp] < y[yp]:
            xp += 1
        else:
            yp += 1

    return mask


@numba.njit
def cantor_pairing(x, y):
    """
    Computes the cantor pairing function for two integer, mapping two integers
    bijectively to a single one.

    The function is given as follows:

        p(x, y) = ((x + y) * (x + y + 1)) / 2 + y

    Parameters:
    -----------
    - x: int
        The first integer.
    - y: int
        The second integer.

    Returns:
    --------
    - int
        The result of the pairing function.
    """
    return ((x + y) * (x + y + 1)) // 2 + y
