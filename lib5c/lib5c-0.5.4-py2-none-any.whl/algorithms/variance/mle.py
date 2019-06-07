import numpy as np
import scipy.stats as stats
from scipy.optimize import minimize

from lib5c.util.parallelization import parallelize_regions
from lib5c.util.counts import flatten_and_filter_counts
from lib5c.algorithms.variance.nbinom_dispersion import nb_nll, \
    dispersion_to_variance as nbinom_disp_to_var
from lib5c.algorithms.variance.lognorm_dispersion import \
    dispersion_to_variance as lognorm_disp_to_var


def mle_variance(obs, exp, model='lognorm', min_obs=2, min_dist=6,
                 regional=False):
    """
    Fits a single point estimate of the dispersion across each or all regions
    under the selected model, and returns the converted variance estimates.

    Parameters
    ----------
    obs, exp : dict of np.ndarray
        The counts dicts of observed and expected data. Keys are region names,
        values are square, symmetric count matrices.
    model : {'lognorm', 'loglogistic', 'nbinom'}
        The statistical model to use for MLE point estimation.
    min_obs : float
        Fit only points with at least this many observed counts.
    min_dist : int
        Fit only points with at least this interaction distance in bin units.
    regional : bool
        Pass True to fit a separate point estimate for each region.

    Returns
    -------
    dict of np.ndarray
        The variance estimates.
    """
    if regional:
        return parallelize_regions(mle_variance)(obs, exp, model=model,
                                                 min_dist=min_dist)
    original_exp = exp  # save full square symmetric matrices
    flattened_counts, _, _ = flatten_and_filter_counts(
        {'obs': obs, 'exp': exp},
        min_filters={'obs': min_obs, 'dist': min_dist})
    obs = flattened_counts['obs']
    exp = flattened_counts['exp']
    if model == 'nbinom':
        obs = np.floor(obs)
        res = minimize(nb_nll, [0.1], args=(obs, exp), method='Nelder-Mead')
        if not res.success:
            print(res.message)
            raise ValueError('optimization failed')
        disp = res.x
        if isinstance(original_exp, dict):
            return {r: nbinom_disp_to_var(disp, original_exp[r])
                    for r in original_exp}
        else:
            return nbinom_disp_to_var(disp, original_exp)
    elif model in ['lognorm', 'loglogistic']:
        dist_gen = getattr(stats, model[3:])
        disp = dist_gen(*dist_gen.fit(np.log1p(obs) - np.log1p(exp))).stats('v')
        if isinstance(original_exp, dict):
            return {r: lognorm_disp_to_var(disp, original_exp[r])
                    for r in original_exp}
        else:
            return lognorm_disp_to_var(disp, original_exp)
    elif model == 'norm':
        dist_gen = getattr(stats, model)
        var = dist_gen(*dist_gen.fit(obs - exp)).stats('v')
        if isinstance(original_exp, dict):
            return {r: np.tile(var, original_exp[r].shape)
                    for r in original_exp}
        else:
            return np.tile(var, original_exp.shape)
    elif model == 'poisson':
        raise ValueError('use var=exp for poisson variance')
    else:
        raise ValueError('unknown model %s' % model)
