import numpy as np

from lib5c.util.parallelization import parallelize_regions
from lib5c.algorithms.variance.nbinom_dispersion import variance_to_dispersion
from lib5c.algorithms.variance.lognorm_dispersion import \
    dispersion_to_variance_direct


@parallelize_regions
def deviation_variance(obs, exp, model='lognorm', min_disp=1e-8):
    """
    Estimates pixel-wise variance as the squared deviation between observed and
    expected values.

    Parameters
    ----------
    obs, exp : np.ndarray
        Square, symmetric matrix of observed and expected values, respectively.
    model : {'lognorm', 'nbinom', 'norm'}
        Statistical model to use.
    min_disp : float
        Force a minimum value of the dispersion parameter.

    Returns
    -------
    tuple of np.ndarray
        The first three elements are the mean parameter estimate, dispersion
        estimate, and variance estimate, respectively, for each pixel. The
        fourth element is a boolean matrix showing which pixels are considered
        to be overdispersed.
    """
    if model == 'lognorm':
        obs = np.log1p(obs)
        exp = np.log1p(exp)
    var = (obs - exp)**2
    if model == 'nbinom':
        idx_od = var > exp + 0.001
        disp = variance_to_dispersion(var, exp, min_disp=min_disp)
        mean = exp
    elif model == 'lognorm':
        idx_od = var > min_disp
        disp = var
        disp[~idx_od & np.isfinite(disp)] = min_disp
        mean = exp - disp / 2
        var = dispersion_to_variance_direct(disp, mean)
    elif model == 'norm':
        idx_od = var > min_disp
        var[~idx_od & np.isfinite(var)] = min_disp
        disp = var
        mean = exp
    elif model == 'loglogistic':
        raise ValueError('deviation loglogistic not supported')
    elif model == 'poisson':
        raise ValueError('use var=exp for poisson variance')
    else:
        raise ValueError('unknown model %s' % model)
    return mean, disp, var, idx_od
