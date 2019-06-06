import numpy as np
from scipy.signal import convolve

from lib5c.util.counts import propagate_nans
from lib5c.util.mathematics import zero_nans, symmetrize
from lib5c.util.donut import donut_footprint, lower_left_footprint


def apply_filter(obs_matrix, exp_matrix, footprint, max_percent=0.2,
                 min_exp=0.1):
    """
    Computes a corrected expected value by applying a footprint to observed and
    expected matrix.

    Parameters
    ----------
    obs_matrix, exp_matrix : np.ndarray
        The square, symmetric matrices of observed and expected counts,
        respectively.
    footprint : np.ndarray
        The footprint to convolve. Should contain 1's at positions included in
        the footprint and 0's everywhere else.
    max_percent : float
        If the proportion of nan's in the footprint for a pixel is greater than
        this value, the corrected expected at that point will be set to nan.
    min_exp : float
        If the sum of entries in ``exp_matrix`` under the footprint for a
        particular pixel is less than this value, set the output at this pixel
        to nan to avoid numerical instability related to division by small
        numbers.

    Returns
    -------
    np.ndarray
        The corrected expected value.
    """
    # propagate nans
    obs, exp = propagate_nans(obs_matrix, exp_matrix)

    # record where the nans are
    nan = ~np.isfinite(obs).astype(int)

    # wipe nans
    obs = zero_nans(obs)
    exp = zero_nans(exp)

    # convolve, reversing the dimensions of the second "signal" to agree with
    # naive intuition
    nan_conv = convolve(nan, footprint[::-1, ::-1], mode='same')
    obs_conv = convolve(obs, footprint[::-1, ::-1], mode='same')
    exp_conv = convolve(exp, footprint[::-1, ::-1], mode='same')

    # compute corrected expected
    result = (obs_conv / exp_conv) * exp_matrix

    # convert min_percent to a number of nans and apply the threshold
    max_nan = np.sum(footprint) * max_percent
    result[nan_conv > max_nan] = np.nan

    # write back nans
    result[nan == 1] = np.nan

    # write nan over inf (sum of exp was 0) or possibly unstable values
    result[exp_conv < min_exp] = np.nan

    # symmetrize and return, assuming footprint is correct for upper triangle
    return symmetrize(result, source='upper')


def donut_filt(obs_matrix, exp_matrix, p, w, max_percent=0.2, min_exp=0.1):
    """
    Computes the full donut filter.

    Parameters
    ----------
    obs_matrix, exp_matrix : np.ndarray
        The square, symmetric matrices of observed and expected counts,
        respectively.
    p, w : int
        The inner and outer radii of the donut, respectively.
    max_percent : float
        If the proportion of nan's in the footprint for a pixel is greater than
        this value, the corrected expected at that point will be set to nan.
    min_exp : float
        If the sum of entries in ``exp_matrix`` under the footprint for a
        particular pixel is less than this value, set the output at this pixel
        to nan to avoid numerical instability related to division by small
        numbers.

    Returns
    -------
    np.ndarray
        The corrected expected value.
    """
    return apply_filter(obs_matrix, exp_matrix, donut_footprint(p, w),
                        max_percent=max_percent, min_exp=min_exp)


def lower_left_filt(obs_matrix, exp_matrix, p, w, max_percent=0.2, min_exp=0.1):
    """
    Computes the lower left donut filter.

    Parameters
    ----------
    obs_matrix, exp_matrix : np.ndarray
        The square, symmetric matrices of observed and expected counts,
        respectively.
    p, w : int
        The inner and outer radii of the donut, respectively.
    max_percent : float
        If the proportion of nan's in the footprint for a pixel is greater than
        this value, the corrected expected at that point will be set to nan.
    min_exp : float
        If the sum of entries in ``exp_matrix`` under the footprint for a
        particular pixel is less than this value, set the output at this pixel
        to nan to avoid numerical instability related to division by small
        numbers.

    Returns
    -------
    np.ndarray
        The corrected expected value.

    Examples
    --------
    >>> import numpy as np
    >>> from lib5c.algorithms.donut_filters import lower_left_filt
    >>> from lib5c.algorithms.expected import empirical_binned
    >>> from lib5c.algorithms.expected import make_expected_matrix_from_list
    >>> obs = np.array([[10,  4,  1],
    ...                 [ 4,  8,  6],
    ...                 [ 1,  6, 12]]).astype(float)
    >>> exp = make_expected_matrix_from_list(
    ...     empirical_binned(obs, log_transform=False))
    >>> exp
    array([[10.,  5.,  1.],
           [ 5., 10.,  5.],
           [ 1.,  5., 10.]])
    >>> lower_left_filt(obs, exp, 0, 1, max_percent=0.0, min_exp=0.0)
    array([[ nan,  4. ,  0.8],
           [ 4. , 10. ,  6. ],
           [ 0.8,  6. ,  nan]])
    """
    return apply_filter(obs_matrix, exp_matrix, lower_left_footprint(p, w),
                        max_percent=max_percent, min_exp=min_exp)
