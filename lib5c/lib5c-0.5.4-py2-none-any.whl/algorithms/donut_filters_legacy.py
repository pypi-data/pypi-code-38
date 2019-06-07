"""
Contains a collection of functions to generate the "geometric filters" from
the Rao et al. paper "A 3D Map of the Human Genome at Kilobase Resolution
Reveals Principles of Chromatin Looping".

Compute_filter
Propagate NaN

Original author: Dan Gillis
"""

from __future__ import division
import numpy as np
from scipy.ndimage.filters import generic_filter


def donut_filt(m_star, e_star, w=15, p=5, min_percent=0.7):
    """
    Computes donut filter for each pixel in the upper right part of symmetric
    matrix for a static w and p.
    Note/Warning:
    This does not propagate NaNs across m_star to e_star (and vice versa)
    You will most likely want to do this before running this function.

    m_star is matrix of observed counts

    e_star is matrix of expected counts

    w is parameter for outer square

    p is parameter for inner square

    min_percent is the minimum percentage of donut that must fall in matrices
    and must be non-NaN for an expected value to be calculated.
    The minimum percentage is the primary method of determining whether or
    not a valid donut expected value can be computed.

    query_close_points determines whether or not to try to determine donut
    filter values at points that are less than 2 + p bins apart. This number
    comes from Rao et al. (2014) supplement pg. S58. The default, False,
    follows this guideline. Set to True (or some truthy value) to try to
    compute an expected value at these points

    Returns symmetric matrix of donut expected values at each point.
    All points not assigned an expected value will be a value of np.NaN
    """

    # w must be bigger than p
    # if p is bigger, assume user mixed up inputs
    if p > w:
        w, p = p, w
    elif p == w:
        raise Exception('w must be bigger than p')

    # maximum number of pixels that fall inside the filter
    max_in_filt = (2 * w + 1) ** 2 - (2 * p + 1) ** 2 - 4 * w + 4 * p
    # minimum number of non-NaN pixels for region to be allowed
    min_allowed = max_in_filt * min_percent

    # produces donut shape of 1s (inside) and 0s (outside)
    # is inside donut if column and row are not in inner p-square
    # unless it is the middle row or middle column
    footprint = [[1 if i != w and ((
        i > p + w or i < w - p) or (j < w - p or j > p + w)) and j != w else 0
        for i in xrange(2 * w + 1)] for j in xrange(2 * w + 1)]

    # make array to sum number of NaN elements inside filter at a step
    nan_arr = np.zeros(m_star.shape)
    nan_arr[np.isfinite(m_star)] = 1

    ms = generic_filter(
        m_star, np.nansum, footprint=footprint, mode='constant')
    es = generic_filter(
        e_star, np.nansum, footprint=footprint, mode='constant')
    n = generic_filter(
        nan_arr, np.sum, footprint=footprint, mode='constant')

    don_expect = np.multiply(np.true_divide(ms, es), e_star)
    don_expect[np.where(n < min_allowed)] = np.nan

    # ensure symmetricality
    # - not actually necessary for donut since it is symmetric across diagonal
    for j in range(len(don_expect)):
        for i in range(j):
            don_expect[j, i] = don_expect[i, j]

    return don_expect


def lower_left_filt(m_star, e_star, w=15, p=5, min_percent=0.2,
                    query_close_points=False):
    """
    Computes lower left filter for each pixel in the upper right
    part of matrix
    """

    # w must be bigger than p
    # if p is bigger, assume user mixed up inputs
    if p > w:
        w, p = p, w
    elif p == w:
        raise Exception('w must be bigger than p')

    # produces lower left shape of 1s (inside) and 0s (outside)
    # is inside donut if column and row are not in inner p-square
    # unless it is the middle row or middle column
    # includes 0-padding in upper right corner to make shape of footpring
    # rectangular
    footprint = [[1 if (j > w + p and i < w) or (j > w and i < w - p)
                  else 0 for i in xrange(2 * w + 1)] for j in xrange(2 * w + 1)]
    ll_expect = np.empty(np.shape(m_star))
    ll_expect[:] = np.NaN
    dim = len(m_star)
    max_in_filt = w ** 2 - p ** 2
    min_allowed = max_in_filt * min_percent

    nan_arr = np.zeros(m_star.shape)
    nan_arr[np.isfinite(m_star)] = 1

    ms = generic_filter(
        m_star, np.nansum, footprint=footprint, mode='constant')
    es = generic_filter(
        e_star, np.nansum, footprint=footprint, mode='constant')
    n = generic_filter(
        nan_arr, np.sum, footprint=footprint, mode='constant')

    ll_expect = np.multiply(np.true_divide(ms, es), e_star)
    ll_expect[np.where(n < min_allowed)] = np.nan

    for j in range(len(ll_expect)):
        for i in range(j):
            ll_expect[j, i] = ll_expect[i, j]

    return ll_expect


def vert_filt(m_star, e_star, w, p, min_percent=0.7):
    """
    Computes vert filter for each pixel in the upper right part of matrix
    """

    # w must be bigger than p
    # if p is bigger, assume user mixed up inputs
    if p > w:
        w, p = p, w
    elif p == w:
        raise Exception('w must be bigger than p')

    vert_expect = np.empty(np.shape(m_star))
    vert_expect[:] = np.NaN
    dim = len(m_star)
    max_area = 3*(w-p)
    min_allowed = min_percent * max_area
    for j in xrange(1, dim):
        if j + 1 > dim - 1:
            continue
        for i in xrange(w, j-p-1):

            u_bound = max(i-w, 0)
            if i + w <= dim - 1:
                d_bound = min(i+w, dim-1)
            else:
                continue
            up_bound = max(0, i-p)

            # propagate NaNs across reflection
            # copy area
            m_1 = m_star[range(u_bound, up_bound), :][:, range(j-1, j+2)]
            m_2 = m_star[range(d_bound, i+p, -1), :][:, range(j+1, j-2, -1)]
            e_1 = e_star[range(u_bound, up_bound), :][:, range(j-1, j+2)]
            e_2 = e_star[range(d_bound, i+p, -1), :][:, range(j+1, j-2, -1)]

            m_2[np.isnan(m_1)] = np.NaN
            e_2[np.isnan(e_1)] = np.NaN
            non_nan_count = np.count_nonzero(np.isfinite(m_2))

            if non_nan_count < min_allowed:
                continue

            m_1[np.isnan(e_1)] = np.NaN
            m_2[np.isnan(e_2)] = np.NaN
            e_1[np.isnan(m_1)] = np.NaN
            e_2[np.isnan(m_2)] = np.NaN

            m_1[np.isnan(m_2)] = np.NaN
            e_1[np.isnan(e_2)] = np.NaN

            numer = 0
            denom = 0

            numer += np.nansum(m_1)
            n1 = np.nansum(e_1)
            denom += n1

            numer -= np.nansum(m_2)
            n2 = np.nansum(e_2)
            denom -= n2

            vert_expect[i, j] = numer * e_star[i, j] / denom
            vert_expect[j, i] = vert_expect[i, j]
    return vert_expect


def horz_filt(m_star, e_star, w, p, min_percent=0.7):
    """
    Computes horz filter for each pixel in the upper right part of matrix
    """

    # w must be bigger than p
    # if p is bigger, assume user mixed up inputs
    if p > w:
        w, p = p, w
    elif p == w:
        raise Exception('w must be bigger than p')

    horz_expect = np.empty(np.shape(m_star))
    horz_expect[:] = np.NaN
    dim = len(m_star)
    max_area = (w-p)*3
    min_allowed = max_area * min_percent
    # need to make sure both sides are symmetric in size (as well as NaNs)
    for j in xrange(w, dim):
        l_bound = max(j-w, 0)
        if j + w <= dim - 1:
            r_bound = min(j+w, dim-1)
        else:
            continue
        lp_bound = max(0, j-p)
        for i in xrange(1, j-p-1):
            if i + 1 > dim - 1:
                continue
            # propagate NaNs across reflection
            # copy area
            m_1 = m_star[range(i-1, i+2), :][:, range(l_bound, lp_bound)]
            m_2 = m_star[range(i+1, i-2, -1), :][:, range(r_bound, j+p, -1)]
            e_1 = e_star[range(i-1, i+2), :][:, range(l_bound, lp_bound)]
            e_2 = e_star[range(i+1, i-2, -1), :][:, range(r_bound, j+p, -1)]

            # may want to change how NaNs are reflected
            # could do across diagonal rather than across line
            m_1[np.isnan(e_1)] = np.NaN
            m_2[np.isnan(e_2)] = np.NaN
            e_1[np.isnan(m_1)] = np.NaN
            e_2[np.isnan(m_2)] = np.NaN

            m_2[np.isnan(m_1)] = np.NaN
            e_2[np.isnan(e_1)] = np.NaN
            non_nan_count = np.count_nonzero(np.isfinite(m_2))

            if non_nan_count < min_allowed:
                continue

            m_1[np.isnan(m_2)] = np.NaN
            e_1[np.isnan(e_2)] = np.NaN

            numer = 0
            denom = 0

            numer += np.nansum(m_1)
            n1 = np.nansum(e_1)
            denom += n1

            numer -= np.nansum(m_2)
            n2 = np.nansum(e_2)
            denom -= n2

            horz_expect[i, j] = numer * e_star[i, j] / denom
            horz_expect[j, i] = horz_expect[i, j]
            
    return horz_expect


def calc_filts(obs_mat, exp_mat, w, p):
    """
    Calculates the filter values for given observed and expected matrices
    """
    don_mat = donut_filt(obs_mat, exp_mat, w, p)
    ll_mat = lower_left_filt(obs_mat, exp_mat, w, p)
    vert_mat = vert_filt(obs_mat, exp_mat, w, p)
    horz_mat = horz_filt(obs_mat, exp_mat, w, p)

    return [don_mat, ll_mat, vert_mat,  horz_mat, w, p]


def propagate_nan(mat_1, mat_2):
    """
    propagates nans from one matrix to the other
    generates new matrices
    """
    new_mat_1 = np.zeros(np.shape(mat_1))
    new_mat_2 = np.zeros(np.shape(mat_2))

    # propagate NaNs
    new_mat_1[np.where(np.isnan(mat_2))] = np.nan
    new_mat_2[np.where(np.isnan(mat_1))] = np.nan

    # put in old values
    non_nan_1 = np.where(np.isfinite(mat_1))
    non_nan_2 = np.where(np.isfinite(mat_2))
    new_mat_1[non_nan_2] = mat_1[non_nan_2]
    new_mat_2[non_nan_1] = mat_2[non_nan_1]
    return new_mat_1, new_mat_2


def compute_filter(m_star, e_star, w, p, min_percent=0.7, geo='donut'):
    """
    Wrapper function for computing filter of any geometry
    Fill in kwarg geo with donut, horz, vert, or lower_left

    m_star is matrix of observed counts

    e_star is matrix of expected counts

    w is parameter for outer square

    p is parameter for inner square

    min_percent is the minimum percentage of donut that must fall in matrices
    and must be non-NaN for an expected value to be calculated.
    The minimum percentage is the primary method of determining whether or
    not a valid donut expected value can be computed.

    query_close_points determines whether or not to try to determine donut
    filter values at points that are less than 2 + p bins apart. This number
    comes from Rao et al. (2014) supplement pg. S58. The default, False,
    follows this guideline. Set to True (or some truthy value) to try to
    compute an expected value at these points

    """
    if geo == 'donut':
        filt_exp = donut_filt(m_star, e_star, w, p, min_percent=min_percent)
    elif geo == 'horz':
        filt_exp = horz_filt(m_star, e_star, w, p, min_percent=min_percent)
    elif geo == 'vert':
        filt_exp = vert_filt(m_star, e_star, w, p, min_percent=min_percent)
    elif geo == 'lower_left':
        filt_exp = lower_left_filt(m_star, e_star, w, p,
                                   min_percent=min_percent)
    else:
        raise ValueError('invalid geo %s' % geo)
    return filt_exp


def make_ut_symmetric(a):
    # makes a upper or lower triangular square matrix symmetric
    b = np.nansum(np.nansum(a, a.T), -1 * np.diag(a.diagonal()))
    return b


if __name__ == "__main__":
    pass
