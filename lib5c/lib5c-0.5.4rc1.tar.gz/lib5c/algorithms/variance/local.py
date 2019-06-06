import numpy as np
from scipy.signal import convolve

from lib5c.util.mathematics import zero_nans
from lib5c.util.parallelization import parallelize_regions
from lib5c.algorithms.variance.nbinom_dispersion import variance_to_dispersion
from lib5c.algorithms.variance.lognorm_dispersion import \
    dispersion_to_variance_direct


@parallelize_regions
def local_variance(matrix, model='lognorm', w=1, min_finite=3, min_disp=1e-8):
    """
    Estimates pixel-wise variance by treating nearby matrix entries as
    replicates.

    Parameters
    ----------
    matrix : np.ndarray
        Square, symmetric matrix of count values.
    model : {'lognorm', 'nbinom'}
        Statistical model to use.
    w : int or np.ndarray
        Size of footprint to use. Footprint will be ``np.eye(2*w+1)``. To use a
        different footprint, pass it as an ``np.ndarray``.
    min_finite : int
        Points with fewer than this many finite entries inside their footprint
        will have their variance estimate set to nan.
    min_disp : float
        Force a minimum value of the dispersion parameter.

    Returns
    -------
    tuple of np.ndarray
        The first three elements are the mean parameter estimate, dispersion
        estimate, and variance estimate, respectively, for each pixel. The
        fourth element is a boolean matrix showing which pixels are considered
        to be overdispersed.

    Examples
    --------
    >>> import numpy as np
    >>> from lib5c.algorithms.variance.local import local_variance
    >>> local_variance(np.array([[1, 4, 1],
    ...                          [4, 1, 1],
    ...                          [1, 1, 1]]), model='norm', min_finite=2)
    (array([[1. , 2.5, 1. ],
            [2.5, 1. , 2.5],
            [1. , 2.5, 1. ]]),
     array([[1.0e-08, 4.5e+00,     nan],
            [4.5e+00, 1.0e-08, 4.5e+00],
            [    nan, 4.5e+00, 1.0e-08]]),
     array([[1.0e-08, 4.5e+00,     nan],
            [4.5e+00, 1.0e-08, 4.5e+00],
            [    nan, 4.5e+00, 1.0e-08]]),
     array([[False,  True, False],
            [ True, False,  True],
            [False,  True, False]]))
    """
    if type(w) == int:
        s = 2*w + 1
        footprint = np.eye(s)
    else:
        footprint = w
    if model == 'lognorm':
        matrix = np.log1p(matrix)
    finite = np.isfinite(matrix)
    matrix = zero_nans(matrix)
    n_finite = convolve(finite, footprint, mode='same')
    mean = convolve(matrix, footprint, mode='same') / n_finite
    dev = (matrix - mean)**2
    dev[~np.isfinite(dev)] = 0.0
    var = convolve(dev, footprint, mode='same') / (n_finite - 1)
    var[n_finite < min_finite] = np.nan
    var[~np.isfinite(matrix)] = np.nan
    if model == 'nbinom':
        idx_od = var > mean + 0.001
        disp = variance_to_dispersion(var, mean, min_disp=min_disp)
    elif model == 'lognorm':
        idx_od = var > min_disp
        disp = var
        disp[~idx_od & np.isfinite(disp)] = min_disp
        var = dispersion_to_variance_direct(disp, mean)
    elif model == 'norm':
        idx_od = var > min_disp
        var[~idx_od & np.isfinite(var)] = min_disp
        disp = var
    elif model == 'loglogistic':
        raise ValueError('local loglogistic not supported')
    elif model == 'poisson':
        raise ValueError('use var=exp for poisson variance')
    else:
        raise ValueError('unknown model %s' % model)
    return mean, disp, var, idx_od
