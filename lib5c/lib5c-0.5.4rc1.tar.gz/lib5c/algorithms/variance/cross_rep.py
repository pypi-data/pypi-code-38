import numpy as np

from lib5c.util.parallelization import parallelize_regions
from lib5c.util.optimization import array_newton
from lib5c.algorithms.variance.nbinom_dispersion import variance_to_dispersion,\
    nb_nll_derivative
from lib5c.algorithms.variance.lognorm_dispersion import \
    dispersion_to_variance_direct


@parallelize_regions
def cross_rep_variance(obs, model='lognorm', min_disp=1e-8, method='mme'):
    """
    Estimates pixel-wise variance across replicates.

    Parameters
    ----------
    obs : dict or list of np.ndarray
        Dict values or list entries are are square, symmetric count matrices
        across replicates.
    model : {'lognorm', 'nbinom', 'norm'}
        Statistical model to use.
    min_disp : float
        Force a minimum value of the dispersion parameter.
    method : {'mme', 'mle'}
        When model='nbinom', pass 'mle' to run maximum likelihood estimation for
        each pixel independently. Pass 'mme' to use method-of-moments variance
        estimation. Has no effect if model='lognorm'.

    Returns
    -------
    tuple of np.ndarray
        The first three elements are the mean parameter estimate, dispersion
        estimate, and variance estimate, respectively, for each pixel. The
        fourth element is a boolean matrix showing which pixels are considered
        to be overdispersed.
    """
    if isinstance(obs, dict):
        obs = np.stack([obs[k] for k in obs])
    elif isinstance(obs, list):
        obs = np.stack([x for x in obs])
    if model == 'lognorm':
        obs = np.log1p(obs)
    mean = np.mean(obs, axis=0)
    var = np.var(obs, ddof=1, axis=0)
    if model == 'nbinom':
        idx_od = var > mean + 0.001
        disp = variance_to_dispersion(var, mean, min_disp=min_disp)
        if method == 'mle':
            disp_mme = disp
            disp = np.zeros_like(disp_mme)
            failed = np.zeros_like(disp_mme, dtype=bool)
            disp[idx_od], failed[idx_od], _ = array_newton(
                nb_nll_derivative, disp_mme[idx_od],
                args=(obs.T[idx_od, :],),
                maxiter=100, failure_idx_flag=True)
            print('%i/%i pixels failed' % (np.sum(failed), failed.size))
            print('%i/%i underdispersed' % (np.sum(~idx_od), idx_od.size))
            disp[failed] = np.nan
            disp[disp < min_disp] = min_disp
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
        raise ValueError('cross-rep loglogistic not supported')
    elif model == 'poisson':
        raise ValueError('use var=exp for poisson variance')
    else:
        raise ValueError('unknown model %s' % model)
    return mean, disp, var, idx_od
