#
#  utils/numpy.py
#  bxtorch
#
#  Created by Oliver Borchert on May 10, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import numpy as np
import numba

def find_contexts(array, context_size, exclude_pivot=False):
    """
    Given an array of size [N], the function extracts subarrays of size C
    (where C is ``context_size`), hence yielding an array of size [W, C] where 
    W is the number of subarrays, given as ``N - C + 1``.

    If the given array has multiple dimensions, the subarrays are only
    extracted for the last dimension.

    Parameters:
    -----------
    - array: numpy.ndarray
        The array to extract subarrays from.
    - context_size: int
        The size of the subarrays to extract.
    - exclude_pivot: bool, default: False
        If this option is set, the number of subarrays returned does not change,
        however, the size of the subarrays reduces to C - 1 and the middle value
        is not included. Instead, a second value is returned, containing all
        these middle values. Setting this option is useful in some settings
        such as sampling windows from random walks for DeepWalk. Note that the
        context size must be an odd number if this option is set.

    Returns:
    --------
    - numpy.ndarray
        The subarrays whose dimension is one more than the given array and where
        all dimensions (except for the last one) are preserved.
    - numpy.ndarray
        The target values if the ``exclude_pivot`` option is set. This array
        has the same dimension as the given array, however, its last dimension
        is equal to the number of contexts found in this dimension.
    """
    assert context_size > 1, \
        "The context size must be at least 2."
    assert not exclude_pivot or context_size % 2 == 1, \
        "If the exclude_pivot option is set, the context size must be odd."
    
    old_shape = array.shape
    array = array.reshape((-1, array.shape[-1]))
    if not exclude_pivot:
        result = _find_contexts_without_pivot(array, context_size)
        return result.reshape(old_shape[:-1] + result.shape[1:])
    else:
        contexts, targets = _find_contexts_with_pivot(array, context_size)
        return (
            contexts.reshape(old_shape[:-1] + contexts.shape[1:]),
            targets.reshape(old_shape[:-1] + targets.shape[-1:])
        )


@numba.njit
def _find_contexts_without_pivot(array, context_size):
    # Dimension of array is 2
    contexts = np.empty(
        (array.shape[0], array.shape[1] - context_size + 1, context_size),
        dtype=array.dtype
    )

    for i in range(array.shape[0]):
        sliding = []
        for j, item in enumerate(array[i]):
            sliding.append(item)
            if j < context_size - 1:
                continue
            else:
                contexts[i][j - context_size + 1] = sliding
                sliding = sliding[1:]

    return contexts


@numba.njit
def _find_contexts_with_pivot(array, context_size):
    contexts = np.empty(
        (array.shape[0], array.shape[1] - context_size + 1, context_size - 1)
    )
    targets = np.empty(contexts.shape[:2])

    halfc = (context_size - 1) // 2

    for i in range(array.shape[0]):
        sliding = []
        for j, item in enumerate(array[i]):
            sliding.append(item)
            if j < context_size - 1:
                continue
            else:
                contexts[i][j - context_size + 1] = \
                    sliding[:halfc] + sliding[halfc+1:]
                targets[i][j - context_size + 1] = sliding[halfc]
                sliding = sliding[1:]

    return contexts, targets



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
def intersection_mask_pairs(x, y):
    """
    Computes the intersection of the given pair arrays.

    The arrays are expected to be sorted alphabetically (i.e. (1, 0) comes 
    after (0, 9)) in ascending order (first in terms of the first dimension,
    then in terms of the second). Otherwise, the result is undefined.

    Parameters:
    -----------
    - x: numpy.ndarray [N, 2]
        Array of pairs number one.
    - y: numpy.ndarray [N, 2]
        Array of pairs number two.

    Returns:
    --------
    - numpy.ndarray [N]
        A mask for the array passed as first parameter. When applied to the
        first array, it returns the pairs contained in both arrays.
    """
    N, M = (x.shape[0], y.shape[0])
    mask = np.zeros(N)

    xp, yp = (0, 0)

    while xp < N and yp < M:
        if x[xp][0] == y[yp][0] and x[xp][1] == y[yp][1]:
            mask[xp] = 1
            xp += 1
            yp += 1
        elif x[xp][0] < y[yp][0] or \
                (x[xp][0] == y[yp][0] and x[xp][1] < y[yp][1]):
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
