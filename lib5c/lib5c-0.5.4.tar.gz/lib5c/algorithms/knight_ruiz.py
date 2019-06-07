"""
Knight-Ruiz algorithm.

Transcribed from the MATLAB source provided in Rao et al. 2014 by Dan Gillis.
"""

import numpy as np

from lib5c.util.parallelization import parallelize_regions
from lib5c.util.counts import flatten_regional_counts, impute_values
from lib5c.util.mathematics import gmean


def strip_zero_rows_columns_sym_mat(sym_mat):
    """
    Given symmetric 2D numpy array sym_mat, removes rows and columns that have
    no non-zero entries
    """
    zero_cols = np.where(np.all(sym_mat == 0, axis=1))
    reduced_mat = np.delete(sym_mat, zero_cols, axis=1)
    reduced_mat = np.delete(reduced_mat, zero_cols, axis=0)
    return reduced_mat


@parallelize_regions
def kr_balance_matrix(matrix, max_iter=3000, retain_scale=True,
                      imputation_size=0):
    """
    Convenience function for applying KR balancing to a counts matrix.

    Parameters
    ----------
    matrix : np.ndarray
        The matrix to balance.
    max_iter : int
        The maximum number of iterations to try.
    retain_scale : bool
        Pass True to rescale the results to the scale of the original matrix
        using a ratio of geometric means.
    imputation_size : int
        Pass an int greater than 0 to replace NaN's in the matrix with a local
        median approximation. Pass 0 to skip imputation.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        The first array contains the balanced matrix. The second contains the
        bias vector. The third contains the residual.
    """
    imputed_matrix = impute_values(matrix, size=imputation_size)
    bias_vector, errs = kr_balance(imputed_matrix, max_iter=max_iter)
    balanced = balance_matrix(matrix, bias_vector)
    if retain_scale:
        # temporary heuristic for scaling the kr results to the original scale
        factor = gmean(np.array(flatten_regional_counts(matrix))) * len(matrix)
        balanced *= factor
        bias_vector *= np.sqrt(factor)
    balanced[~np.isfinite(matrix)] = np.nan
    return balanced, bias_vector[:, 0], errs


@parallelize_regions
def balance_matrix(matrix, bias_vector, invert=False):
    """
    Balance a matrix given the appropriate multiplicative bias vector.

    Parameters
    ----------
    matrix : np.ndarray
    bias_vector : np.ndarray

    invert : Optional[bool]
        Pass True to invert the bias vector before balancing.

    Returns
    -------
    np.ndarray
        The balanced matrix.
    """
    if invert:
        bias_vector = 1.0 / bias_vector
    return bias_vector.T * matrix * bias_vector


@parallelize_regions
def kr_balance(array, tol=np.float_(1e-6), x0=None, delta=0.1, ddelta=3, fl=0,
               max_iter=3000):
    """
    Performs Knight-Ruiz matrix balancing algorithm on a 2D symmetric numpy
    array.

    Note that this function does not check for symmetry of the array - this
    function may not converge if given non-symmetric matrix.

    Note also that this function does not return balanced matrix - it returns
    the entries of the diagonal matrix that should be multiplied on either side
    of ``array`` to get balanced matrix.

    Parameters
    ----------
    array : np.ndarray
        Matrix to balance. Should be square and symmetric.
    tol : float
        Parameter related to tolerance
    x0 : Optional[np.ndarray]
        The initial guess to use for the bias vector. If not passed, a vector of
        all 1's will be used.
    delta : float
        Parameter related to learning rate.
    ddelta : float
        Parameter related to learning rate.
    fl : int
        Adjusts the verbosity of command line output.
    max_iter : Optional[int]
        The maximum number of iterations. Pass None to set no limit.

    Returns
    -------
    Tuple[np.ndarray]
        The first element is the bias vector, the second is the residual.

    Examples
    --------
    >>> import numpy as np
    >>> X = np.reshape(range(16), (4, 4)).astype(float)
    >>> counts = X + X.T
    >>> counts
    array([[ 0.,  5., 10., 15.],
           [ 5., 10., 15., 20.],
           [10., 15., 20., 25.],
           [15., 20., 25., 30.]])
    >>> counts.sum(axis=1)
    array([30., 50., 70., 90.])
    >>> x, res = kr_balance(counts)
    >>> balanced = x.T * counts * x
    >>> balanced
    array([[0.        , 0.26604444, 0.34729636, 0.3866592 ],
           [0.26604444, 0.2489703 , 0.24375574, 0.24122952],
           [0.34729636, 0.24375574, 0.21213368, 0.19681423],
           [0.3866592 , 0.24122952, 0.19681423, 0.17529705]])
    >>> balanced.sum(axis=1)
    array([1., 1., 1., 1.])
    >>> for i in range(len(counts)):
    ...     for j in range(i+1):
    ...         if i % 2 == j % 2:
    ...             counts[i, j] = 0.0
    ...             counts[j, i] = 0.0
    >>> counts
    array([[ 0.,  5.,  0., 15.],
           [ 5.,  0., 15.,  0.],
           [ 0., 15.,  0., 25.],
           [15.,  0., 25.,  0.]])
    >>> x, res = kr_balance(counts)
    >>> balanced = x.T * counts * x
    >>> balanced
    array([[0.        , 0.42705098, 0.        , 0.57294902],
           [0.42705098, 0.        , 0.57294902, 0.        ],
           [0.        , 0.57294902, 0.        , 0.42705098],
           [0.57294902, 0.        , 0.42705098, 0.        ]])
    >>> balanced.sum(axis=1)
    array([1., 1., 1., 1.])
    """
    dims = array.shape
    if dims[0] != dims[1] or len(dims) > 2:
        raise Exception
    n = dims[0]
    e = np.ones((n, 1))
    res = np.array([])
    if x0 is None:
        x0 = e.copy()
    g = np.float_(0.9)
    eta_max = 0.1
    eta = eta_max
    stop_tol = tol * 0.5
    # x0 is not used again, so do not need to copy object
    x = x0  # n x 1 array
    rt = tol ** 2
    v = x0 * np.dot(array, x)  # n x 1 array
    rk = 1 - v  # n x 1 array
    rho_km1 = np.dot(np.transpose(rk), rk)[0, 0]  # scalar value
    # no need to copy next two objects - are scalar values
    rout = rho_km1
    rold = rout
    mvp = 0
    i = 0
    if fl == 1:
        print('it in. it res')
    while rout > rt:
        if max_iter is not None and i > max_iter:
            break
        i += 1
        k = 0
        y = np.ones((n, 1))
        innertol = max(eta ** 2 * rout, rt)
        while rho_km1 > innertol:
            k += 1
            # print('{} {} {}'.format(i, k, innertol))
            # print(rk)
            if k == 1:
                z = rk / v
                p = z.copy()
                rho_km1 = np.dot(np.transpose(rk), z)
            else:
                beta = rho_km1 / rho_km2
                p = z + beta * p
            w = x * np.dot(array, x * p) + v * p
            alpha = rho_km1 / np.dot(np.transpose(p), w)
            ap = alpha * p
            ynew = y + ap
            if np.min(ynew) <= delta:
                if delta == 0:
                    break
                ind = np.where(ap < 0)
                gamma = np.min((delta - y[ind]) / ap[ind])
                y = y + gamma * ap
                break
            if np.max(ynew) >= ddelta:
                # see above - need to code
                # also check that (i.e. gamma or ap is scalar)
                ind = np.where(ynew > ddelta)
                gamma = min((ddelta - y[ind]) / ap[ind])
                y = y + gamma * ap
                break
            y = ynew
            rk = rk - alpha * w
            rho_km2 = rho_km1
            z = rk / v
            rho_km1 = np.dot(np.transpose(rk), z)
            # print(rho_km1)
        x = x * y
        v = x * np.dot(array, x)
        rk = 1 - v
        rho_km1 = np.dot(np.transpose(rk), rk)[0, 0]  # scalar value
        rout = rho_km1
        mvp = mvp + k + 1
        rat = rout / rold
        rold = rout
        res_norm = np.sqrt(rout)
        eta_0 = eta
        eta = g * rat
        if g * eta_0 ** 2 > 0.1:
            eta = max(eta, g * eta_0 ** 2)
        eta = max(min(eta, eta_max), stop_tol / res_norm)
        if fl == 1:
            print('{} {} {:.3e}'.format(i, k, res_norm))
            res = np.append(res, res_norm)

    return x, res
