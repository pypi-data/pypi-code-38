"""
Module for estimating the mean-variance scaling parameter to be used for
parameterizing distributions over 5C interaction frequencies.
"""

import numpy as np

from lib5c.util.counts import flatten_regional_counts


def quadratic_log_log_fit(x, y):
    """
    Fit a pure-quadratic function ``y = a * x**2`` using a loss function in
    log-log space.

    Parameters
    ----------
    x : np.ndarray
        Flat vector of ``x`` values to fit.
    y : np.ndarray
        Flat vector of ``y`` values to fit.

    Returns
    -------
    np.poly1d
        The fitted function.
    """
    a = np.exp(np.nanmean(np.log(y + 1) - 2 * np.log(x + 1)))
    return np.poly1d([a, 0, 0])


def make_power_law_function(p, a):
    """
    Construct a power law function of the form ``a * (x ** p)`` given parameters
    ``a`` and ``p``.

    Parameters
    ----------
    p : float
        The power in the power law relationship.
    a : float
        The scaling constant in the power law relationship.

    Returns
    -------
    Callable[[float], float]
        The power law function, which takes a single argument ``x`` and returns
        the float ``a * (x ** p)``.
    """
    def power_law_function(x):
        return a * (x ** p)

    return power_law_function


def compute_log_log_fit_variance_factor(regional_counts):
    """
    Compute a variance scaling factor using the ``log_log_fit`` approach.

    Parameters
    ----------
    regional_counts : np.ndarray
        The matrix of observed counts for this region.

    Returns
    -------
    float
        The variance scaling factor for this region.
    """
    # make offdiagonals
    offdiagonals = [np.diag(regional_counts, k=i)
                    for i in range(len(regional_counts))]

    # compute means and variances at each distance
    sample_variances = np.asarray([np.nanvar(offdiagonal, ddof=1)
                                   for offdiagonal in offdiagonals])
    sample_means = np.asarray([np.nanmean(offdiagonal)
                               for offdiagonal in offdiagonals])

    # filter nans
    filtered_sample_variances = sample_variances[
        np.isfinite(sample_variances) & np.isfinite(sample_means)]
    filtered_sample_means = sample_means[
        np.isfinite(sample_variances) & np.isfinite(sample_means)]

    return np.exp(np.mean(np.log(filtered_sample_variances + 1) -
                          2 * np.log(filtered_sample_means + 1)))


def compute_log_log_fit_variance_factors(counts):
    """
    Compute variance scaling factors for each region using the ``log_log_fit``
    approach.

    Parameters
    ----------
    counts : Dict[str, np.ndarray]
        The dict of observed counts matrices.

    Returns
    -------
    Dict[str, float]
        The variance scaling factor for each region.
    """
    return {region: compute_log_log_fit_variance_factor(counts[region])
            for region in counts.keys()}


def compute_obs_over_exp_variance_factor(regional_obs, regional_exp, log=False):
    """
    Compute a variance scaling factor using the ``obs_over_exp`` approach.

    Parameters
    ----------
    regional_obs : np.ndarray
        The matrix of observed counts for this region.
    regional_exp : np.ndarray
        The matrix of expected counts for this region.
    log : Optional[bool]
        Whether or not the data should be logged.

    Returns
    -------
    float
        The variance scaling factor for this region.
    """
    obs_over_exp = regional_obs / regional_exp
    if log:
        obs_over_exp = np.log(obs_over_exp)
    flattened_obs_over_exp = flatten_regional_counts(obs_over_exp)
    return np.nanvar(flattened_obs_over_exp)


def compute_obs_over_exp_variance_factors(obs_counts, exp_counts, log=False):
    """
    Compute variance scaling factors for each region using the ``obs_over_exp``
    approach.

    Parameters
    ----------
    obs_counts : Dict[str, np.ndarray]
        The dict of observed counts matrices.
    exp_counts : Dict[str, np.ndarray]
        The dict of expected counts matrices.
    log : Optional[bool]
        Whether or not the data should be logged.

    Returns
    -------
    Dict[str, float]
        The variance scaling factor for each region.
    """
    return {region: compute_obs_over_exp_variance_factor(obs_counts[region],
                                                         exp_counts[region],
                                                         log=log)
            for region in obs_counts.keys()}


def compute_obs_over_exp_mean_factor(regional_obs, regional_exp, log=False):
    """
    Compute a mean scaling factor using the ``obs_over_exp`` approach.

    Parameters
    ----------
    regional_obs : np.ndarray
        The matrix of observed counts for this region.
    regional_exp : np.ndarray
        The matrix of expected counts for this region.
    log : Optional[bool]
        Whether or not the data should be logged.

    Returns
    -------
    float
        The mean scaling factor for this region.
    """
    obs_over_exp = regional_obs / regional_exp
    if log:
        obs_over_exp = np.log(obs_over_exp)
    flattened_obs_over_exp = flatten_regional_counts(obs_over_exp)
    return np.nanmean(flattened_obs_over_exp)


def compute_obs_over_exp_mean_factors(obs_counts, exp_counts, log=False):
    """
    Compute mean scaling factors for each region using the ``obs_over_exp``
    approach.

    Parameters
    ----------
    obs_counts : Dict[str, np.ndarray]
        The dict of observed counts matrices.
    exp_counts : Dict[str, np.ndarray]
        The dict of expected counts matrices.
    log : Optional[bool]
        Whether or not the data should be logged.

    Returns
    -------
    Dict[str, float]
        The mean scaling factor for each region.
    """
    return {region: compute_obs_over_exp_mean_factor(obs_counts[region],
                                                     exp_counts[region],
                                                     log=log)
            for region in obs_counts.keys()}
