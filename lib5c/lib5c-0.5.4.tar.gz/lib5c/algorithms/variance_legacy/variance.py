"""
Module for computing variance estimates for 5C interaction data.
"""

import numpy as np
import scipy.stats as stats
from scipy.ndimage import generic_filter

from lib5c.algorithms.variance.mle import mle_variance
from lib5c.util.parallelization import parallelize_regions
from lib5c.util.optimization import quadratic_log_log_fit
from lib5c.util.counts import flatten_obs_and_exp
from lib5c.util.grouping import group_obs_by_exp
from lib5c.util.donut import donut_footprint


@parallelize_regions
def estimate_variance(obs, exp, method='disp', **kwargs):
    """
    Convenience function for estimating the variance using any of a variety of
    available methods.

    Parameters
    ----------
    obs : np.ndarray
        Regional matrix of the observed values.
    exp : np.ndarray
        Regional matrix of the expected values.
    method : {'disp', 'mvr', 'vst', 'local', 'local_vst', 'poisson'}
        The method by which the variance should be estimated.
    kwargs : additional keyword arguments
        Will be passed to the selected ``estimate_*_variance()`` function.

    Returns
    -------
    np.ndarray
        Regional matrix of variances.
    """
    if method == 'disp':
        if 'exclude_offdiagonals' in kwargs:
            kwargs['min_dist'] = kwargs['exclude_offdiagonals'] + 1
            del kwargs['exclude_offdiagonals']
        return mle_variance(obs, exp, **kwargs)
    elif method == 'mvr':
        return estimate_mvr_variance(obs, exp, **kwargs)
    elif method == 'vst':
        return estimate_vst_variance(obs, exp, **kwargs)
    elif method == 'local':
        return estimate_local_variance(obs, exp, vst=False, **kwargs)
    elif method == 'local_vst':
        return estimate_local_variance(obs, exp, vst=True, **kwargs)
    elif method == 'poisson':
        return exp
    else:
        raise ValueError('unrecognized variance estimation method: %s' % method)


def estimate_global_mvr_variance(obs_counts, exp_counts, num_groups=100,
                                 group_fractional_tolerance=0.1,
                                 exclude_offdiagonals=5):
    """
    Estimates the variance using a single mean-variance relationship shared
    across all regions.

    Parameters
    ----------
    obs_counts : dict of np.ndarray
        Counts dict of observed values.
    exp_counts : dict of np.ndarray
        Counts dict of expected values.
    num_groups : int
        The number of groups to fit the MVR to.
    group_fractional_tolerance : float
        The width of each group, specified as a fractional tolerance in the
        expected value.
    exclude_offdiagonals : int
        Exclude this many off-diagonals from the estimation. Pass 0 to exclude
        only the exact diagonal. Pass -1 to exclude nothing.

    Returns
    -------
    dict of np.ndarray
        The counts dict containing the estimated variances.
    """
    exps, groups = group_obs_by_exp(
        obs_counts, exp_counts,
        num_groups=num_groups,
        group_fractional_tolerance=group_fractional_tolerance,
        exclude_offdiagonals=exclude_offdiagonals)
    vars = np.array([np.nanvar(group) for group in groups])
    mvr = quadratic_log_log_fit(exps, vars)
    return {region: mvr(exp_counts[region]) for region in exp_counts}


@parallelize_regions
def estimate_mvr_variance(obs, exp, num_groups=100,
                          group_fractional_tolerance=0.1,
                          exclude_offdiagonals=5):
    """
    Estimates the variance using a mean-variance relationship.

    Parameters
    ----------
    obs : np.ndarray
        Regional matrix of the observed values.
    exp : np.ndarray
        Regional matrix of the expected values.
    num_groups : int
        The number of groups to fit the MVR to.
    group_fractional_tolerance : float
        The width of each group, specified as a fractional tolerance in the
        expected value.
    exclude_offdiagonals : int
        Exclude this many off-diagonals from the estimation. Pass 0 to exclude
        only the exact diagonal. Pass -1 to exclude nothing.

    Returns
    -------
    np.ndarray
        Regional matrix of variances.
    """
    exps, groups = group_obs_by_exp(
        obs, exp,
        num_groups=num_groups,
        group_fractional_tolerance=group_fractional_tolerance,
        exclude_offdiagonals=exclude_offdiagonals)
    vars = np.array([np.nanvar(group) for group in groups])
    mvr = quadratic_log_log_fit(exps, vars)
    return mvr(exp)


@parallelize_regions
def estimate_vst_variance(obs, exp, dist_gen=stats.logistic):
    """
    Estimates the variance using a variance-stabilizing transform.

    Parameters
    ----------
    obs : np.ndarray
        Regional matrix of the observed values.
    exp : np.ndarray
        Regional matrix of the expected values.
    dist_gen : scipy.stats.rv_generic
        The distribution to use to estimate the variance of the VST'd data.

    Returns
    -------
    np.ndarray
        Regional matrix of variances.
    """
    flat_obs, flat_exp = flatten_obs_and_exp(obs, exp, log=True)
    stabilized_variance = dist_gen(*dist_gen.fit(flat_obs-flat_exp))\
        .stats(moments='v')
    return np.ones_like(exp) * stabilized_variance


@parallelize_regions
def estimate_local_variance(obs, exp, p=5, w=15, vst=False):
    """
    Estimates the variance using a local donut window.

    Parameters
    ----------
    obs : np.ndarray
        Regional matrix of the observed values.
    exp : np.ndarray
        Regional matrix of the expected values.
    w : int
        The outer radius of the donut window to use.
    p : int
        The inner radius of the donut window to use.
    vst : bool
        Pass True to apply a VST before estimating the local variance.

    Returns
    -------
    np.ndarray
        Regional matrix of variances.
    """
    if vst:
        obs = np.log(obs + 1)
        exp = np.log(exp + 1)
    return generic_filter(
        obs - exp,
        lambda x: np.nansum(x**2) / (np.sum(np.isfinite(x))-1),
        footprint=donut_footprint(p, w), mode='constant', cval=np.nan
    )
