"""
Module for fitting distributions to 5C data and using them to assign p-values to
5C interactions.
"""

import collections

import numpy as np
import scipy.stats as stats

from lib5c.util.counts import flatten_regional_counts
from lib5c.util.parallelization import parallelize_regions

from lib5c.algorithms.distributions_legacy.variance import \
    compute_log_log_fit_variance_factor, compute_obs_over_exp_mean_factor, \
    compute_obs_over_exp_variance_factor


@parallelize_regions
def fit_and_call(obs_matrix, exp_matrix, mode='obs_over_exp',
                 dist='nbinom', log=False, bias=None):
    """
    Convenience function that fits and calls p-values given an observed matrix,
    expected matrix, distribution fitting mode, and distribution.

    Parameters
    ----------
    obs_matrix : np.ndarray
        The matrix of observed counts.
    exp_matrix : np.ndarray
        The matrix of expected counts.
    mode : {'obs_over_exp','log_log_fit','regional_simple','regional_shifted'}
        The method to use to call the p-values:
            * obs_over_exp: use quadratic mean-variance relationship estimated
              via sample variance of obs/exp counts across whole region
            * log_log_fit: use quadratic mean-variance relationship estimated
              via fitting quadratic curve in log-mean vs log-variance space
            * regional_simple: fit single distribution to obs/exp across whole
              region
            * regional_shifted: fit distributions by shifting counts from the
              whole region to the appropriate distance scale
    dist : str
        String identifier for what distribution to use. Must match the name of a
        subclass of scipy.stats.rv_generic.
    log : bool
        Pass True to log the observed counts prior to p-value computation.
    bias : Optional[Sequence[float]]
        Pass a bias vector to deconvolute counts and distributions immediately
        before p-value assignment.

    Returns
    -------
    np.ndarray
        The matrix of called p-values.
    """
    frozen_dists = fit_distributions(
        obs_matrix, exp_matrix, mode=mode, dist=dist, log=log)
    return call_pvalues(
        obs_matrix, exp_matrix, frozen_dists, log=log, bias=bias)


def call_pvalues(obs_matrix, exp_matrix, frozen_dists, log=False, bias=None):
    """
    Convenience function that calls p-values given an observed matrix, expected
    matrix, and a collection of pre-fitted, frozen distributions.

    Parameters
    ----------
    obs_matrix : np.ndarray
        The matrix of observed counts.
    exp_matrix : np.ndarray
        The matrix of expected counts.
    frozen_dists : Union[Dict[float, scipy.stats.rv_frozen]]
        Distributions for each expected value, or a single frozen distribution
        to use for the whole region if the fitting mode was 'regional_simple'.
    log : bool
        Pass True to log the observed counts prior to p-value computation.
    bias : Optional[Sequence[float]]
        Pass a bias vector to deconvolute counts and distributions immediately
        before p-value assignment.

    Returns
    -------
    np.ndarray
        The matrix of called p-values.
    """
    if isinstance(frozen_dists, collections.Iterable):
        pvalues = regional_shifted_caller(obs_matrix, exp_matrix, frozen_dists,
                                          log=log, bias=bias)
    else:
        pvalues = regional_simple_caller(obs_matrix, exp_matrix, frozen_dists,
                                         log=log)
    return pvalues


def fit_distributions(obs_matrix, exp_matrix, mode='obs_over_exp',
                      dist='nbinom', log=False, expected_value=None):
    """
    Convenience function that fits distributions to the data given the observed
    and expected matrices.

    Parameters
    ----------
    obs_matrix : np.ndarray
        The matrix of observed counts.
    exp_matrix : np.ndarray
        The matrix of expected counts.
    mode : {'obs_over_exp','log_log_fit','regional_simple','regional_shifted'}
        The method to use to call the p-values:
            * obs_over_exp: use quadratic mean-variance relationship estimated
              via sample variance of obs/exp counts across whole region
            * log_log_fit: use quadratic mean-variance relationship estimated
              via fitting quadratic curve in log-mean vs log-variance space
            * regional_simple: fit single distribution to obs/exp across whole
              region
            * regional_shifted: fit distributions by shifting counts from the
              whole region to the appropriate distance scale
    dist : str
        String identifier for what distribution to use. Must match the name of a
        subclass of ``scipy.stats.rv_generic``.
    log : bool
        Pass True to log the observed counts prior to p-value computation.
    expected_value : Optional[float]
        Pass a float to fit only one distribution for this specific expected
        value.

    Returns
    -------
    Union[Dict[float, scipy.stats.rv_frozen], scipy.stats.rv_frozen]
        Returns a dictionary mapping expected values to the fitted frozen
        distributions for that expected value. If the fitting mode was
        'obs_over_exp', a single frozen distribution is returned directly,
        without being wrapped in a dict.
    """
    # resolve dist_gen
    dist_gen = getattr(stats, dist)

    # fit distributions
    if mode == 'log_log_fit':
        frozen_dists = log_log_fit_fitter(
            obs_matrix, exp_matrix, dist_gen, log=log,
            expected_value=expected_value)
    elif mode == 'obs_over_exp':
        frozen_dists = obs_over_exp_fitter(
            obs_matrix, exp_matrix, dist_gen, log=log,
            expected_value=expected_value)
    elif mode == 'regional_simple':
        frozen_dists = regional_simple_fitter(
            obs_matrix, exp_matrix, dist_gen, log=log)
    elif mode == 'regional_shifted':
        frozen_dists = regional_shifted_fitter(
            obs_matrix, exp_matrix, dist_gen, log=log,
            expected_value=expected_value)
    else:
        raise ValueError('invalid mode %s' % mode)

    return frozen_dists


def regional_shifted_fitter(regional_obs, regional_exp, dist_gen, log=False,
                            expected_value=None):
    """
    Fits distributions to observed counts, shifted to each expected value. This
    is the ``regional_shifted`` approach.

    Parameters
    ----------
    regional_obs : numpy array
        Square, symmetric array of observed counts for this region.
    regional_exp : numpy array
        Square, symmetric array of expected counts for this region.
    dist_gen : scipy.stats.rv_generic
        The distribution to use.
    log: bool
        Pass True to log the observed counts prior to p-value computation.
    expected_value : Optional[float]
        Specify a single expected value to compute the distribution for.

    Returns
    -------
    dict(float -> scipy.stats.rv_frozen)
        The keys are the expected values in ``regional_exp``. The value is the
        fitted distribution afted shifting to that expected value.

    Examples
    --------
    >>> obs = np.array([[2.0, 1.0], [1.0, 3.0]])
    >>> exp = np.array([[2.5, 1.0], [1.0, 2.5]])
    >>> frozen_dists = regional_shifted_fitter(obs, exp, stats.poisson)
    >>> for exp_val in frozen_dists:
    ...     print('%0.2f: %s distribution with mean %.2f and variance %.2f'
    ...           % ((exp_val, frozen_dists[exp_val].dist.name,) +
    ...              frozen_dists[exp_val].stats(moments='mv')))
    2.50: poisson distribution with mean 2.50 and variance 2.50
    1.00: poisson distribution with mean 1.00 and variance 1.00

    >>> obs = np.exp(np.array([[2.0, 1.0], [1.0, 3.0]]))
    >>> exp = np.exp(np.array([[2.5, 1.0], [1.0, 2.5]]))
    >>> frozen_dists = regional_shifted_fitter(obs, exp, stats.norm, log=True)
    >>> for exp_val in frozen_dists:
    ...     print('%0.2f: %s distribution with mean %.2f and variance %.2f'
    ...           % ((exp_val, frozen_dists[exp_val].dist.name,) +
    ...              frozen_dists[exp_val].stats(moments='mv')))
    2.72: norm distribution with mean 1.00 and variance 0.17
    12.18: norm distribution with mean 2.50 and variance 0.17
    """
    frozen_dists = {}

    # honor expected_value kwarg
    if expected_value is not None:
        exp_values = [expected_value]
    else:
        exp_values = flatten_regional_counts(regional_exp, discard_nan=True)

    for exp_value in exp_values:
        # skip expected values we've already seen before
        if exp_value in frozen_dists:
            continue

        # skip non-finite expected values
        if not np.isfinite(exp_value):
            continue

        # shift entire region
        shifted_matrix = regional_obs * (exp_value / regional_exp)

        # log if appropriate
        if log:
            shifted_matrix = np.log(shifted_matrix)

        # flatten shifted matrix
        shifted_flattened = np.array(
            flatten_regional_counts(shifted_matrix, discard_nan=True))

        # fit the appropriate distribution
        frozen_dist = fit_distribution(dist_gen, shifted_flattened)

        # save in cache
        frozen_dists[exp_value] = frozen_dist

    return frozen_dists


def regional_shifted_caller(regional_obs, regional_exp, frozen_dists,
                            log=False, bias=None):
    """
    Calls p-values according to the ``regional_shifted`` approach given fitted
    distributions for every expected value.

    Parameters
    ----------
    regional_obs : numpy array
        Square, symmetric array of observed counts for this region.
    regional_exp : numpy array
        Square, symmetric array of expected counts for this region.
    frozen_dists : dict(float -> scipy.stats.rv_frozen)
        Distributions for each expected value.
    log: bool, optional
        Pass True to log the observed counts prior to p-value computation.
    bias : sequence of float, optional
        Pass a bias vector to deconvolute counts and distributions immediately
        before p-value assignment.

    Returns
    -------
    numpy array
        A square, symmetric array of called p-values.

    Examples
    --------
    >>> obs = np.array([[2.0, 1.0], [1.0, 3.0]])
    >>> exp = np.array([[2.5, 1.0], [1.0, 2.5]])
    >>> frozen_dists = regional_shifted_fitter(obs, exp, stats.poisson)
    >>> regional_shifted_caller(obs, exp, frozen_dists)
    array([[0.45618688, 0.26424112],
           [0.26424112, 0.24242387]])

    >>> obs = np.exp(np.array([[2.0, 1.0], [1.0, 3.0]]))
    >>> exp = np.exp(np.array([[2.5, 1.0], [1.0, 2.5]]))
    >>> frozen_dists = regional_shifted_fitter(obs, exp, stats.norm, log=True)
    >>> regional_shifted_caller(obs, exp, frozen_dists, log=True)
    array([[0.88966432, 0.5       ],
           [0.5       , 0.11033568]])
    """
    pvalues = np.zeros_like(regional_obs)
    if bias is not None:
        bias_matrix = np.outer(bias, bias)
        regional_obs *= bias_matrix
    for i in range(len(pvalues)):
        for j in range(i + 1):
            if regional_exp[i, j] in frozen_dists:
                frozen_dist = frozen_dists[regional_exp[i, j]]
                if bias is not None:
                    frozen_dist = bias_frozen_dist(
                        frozen_dist, bias[i] * bias[j], log=log)
                if (not np.isfinite(regional_exp[i, j]) or
                        not np.isfinite(regional_obs[i, j])):
                    pvalue = np.nan
                elif not log:
                    pvalue = frozen_dist.sf(regional_obs[i, j])
                else:
                    pvalue = frozen_dist.sf(np.log(regional_obs[i, j]))
            else:
                pvalue = np.nan
            pvalues[i, j] = pvalue
            pvalues[j, i] = pvalue
    return pvalues


def regional_simple_fitter(regional_obs, regional_exp, dist_gen, log=False):
    """
    Fits a distribution to the observed over expected counts across the whole
    region. This is the ``regional_simple`` approach.

    Parameters
    ----------
    regional_obs : numpy array
        Square, symmetric array of observed counts for this region.
    regional_exp : numpy array
        Square, symmetric array of expected counts for this region.
    dist_gen : scipy.stats.rv_generic
        The distribution to use.
    log: bool, optional
        Pass True to log the observed over expected matrix prior to fitting the
        distribution.

    Returns
    -------
    scipy.stats.rv_frozen
        The frozen distribution.

    Examples
    --------
    >>> obs = np.array([[2.0, 1.0], [1.0, 3.0]])
    >>> exp = np.array([[2.5, 1.0], [1.0, 2.5]])
    >>> frozen_dist = regional_simple_fitter(obs, exp, dist_gen=stats.poisson)
    >>> print('%s distribution with mean %.2f and variance %.2f'
    ...       % ((frozen_dist.dist.name,) + frozen_dist.stats(moments='mv')))
    poisson distribution with mean 1.00 and variance 1.00

    >>> obs = np.exp(np.array([[2.0, 1.0], [1.0, 3.0]]))
    >>> exp = np.exp(np.array([[2.5, 1.0], [1.0, 2.5]]))
    >>> frozen_dist = regional_simple_fitter(obs, exp, dist_gen=stats.norm,
    ...                                      log=True)
    >>> print('%s distribution with mean %.2f and variance %.2f'
    ...       % ((frozen_dist.dist.name,) + frozen_dist.stats(moments='mv')))
    norm distribution with mean 0.00 and variance 0.17
    """
    # compute obs/exp
    obs_over_exp = regional_obs / regional_exp

    # log if appropriate
    if log:
        obs_over_exp = np.log(obs_over_exp)

    # flatten
    flat_obs_over_exp = np.array(
        flatten_regional_counts(obs_over_exp, discard_nan=True))

    # fit appropriate distribution
    return fit_distribution(dist_gen, flat_obs_over_exp)


def regional_simple_caller(regional_obs, regional_exp, frozen_dist, log=False):
    """
    Calls p-values according to the ``regional_simple`` approach given a fitted
    distribution.

    Parameters
    ----------
    regional_obs : numpy array
        Square, symmetric array of observed counts for this region.
    regional_exp : numpy array
        Square, symmetric array of expected counts for this region.
    frozen_dist : scipy.stats.rv_frozen
        The distribution to use.
    log: bool, optional
        Pass True to log the observed over expected matrix prior to computing
        p-values.

    Returns
    -------
    numpy array
        A square, symmetric array of called p-values.

    Examples
    --------
    >>> obs = np.array([[2.0, 1.0], [1.0, 3.0]])
    >>> exp = np.array([[2.5, 1.0], [1.0, 2.5]])
    >>> frozen_dist = stats.poisson(mu=1.0)
    >>> regional_simple_caller(obs, exp, frozen_dist)
    array([[0.63212056, 0.26424112],
           [0.26424112, 0.26424112]])

    >>> obs = np.exp(np.array([[2.0, 1.0], [1.0, 3.0]]))
    >>> exp = np.exp(np.array([[2.5, 1.0], [1.0, 2.5]]))
    >>> frozen_dist = stats.norm(loc=0.0, scale=np.sqrt(0.17))
    >>> regional_simple_caller(obs, exp, frozen_dist, log=True)
    array([[0.88737355, 0.5       ],
           [0.5       , 0.11262645]])
    """
    # compute obs/exp
    obs_over_exp = regional_obs / regional_exp

    # log if appropriate
    if log:
        obs_over_exp = np.log(obs_over_exp)

    # call
    return frozen_dist.sf(obs_over_exp)


def obs_over_exp_fitter(regional_obs, regional_exp, dist_gen, log=False,
                        expected_value=None):
    """
    Computes distributions for observed counts, using the sample mean and sample
    variance of the observed over expected across the whole region to determine
    the optimal parameters for each expected.

    Parameters
    ----------
    regional_obs : numpy array
        Square, symmetric array of observed counts for this region.
    regional_exp : numpy array
        Square, symmetric array of expected counts for this region.
    dist_gen : scipy.stats.rv_generic
        The distribution to use.
    log: bool, optional
        Pass True to log the observed counts prior to p-value computation.
    expected_value : float, optional
        Specify a single expected value to compute the distribution for.

    Returns
    -------
    dict(float -> scipy.stats.rv_frozen)
        The keys are the expected values in ``regional_exp``. The value is the
        fitted distribution afted shifting to that expected value.

    Examples
    --------
    >>> obs = np.array([[2.0, 1.0], [1.0, 3.0]])
    >>> exp = np.array([[2.5, 1.0], [1.0, 2.5]])
    >>> frozen_dists = obs_over_exp_fitter(obs, exp, stats.poisson)
    >>> for exp_val in frozen_dists:
    ...     print('%0.2f: %s distribution with mean %.2f and variance %.2f'
    ...           % ((exp_val, frozen_dists[exp_val].dist.name,) +
    ...              frozen_dists[exp_val].stats(moments='mv')))
    2.50: poisson distribution with mean 2.50 and variance 2.50
    1.00: poisson distribution with mean 1.00 and variance 1.00

    >>> obs = np.exp(np.array([[2.0, 1.0], [1.0, 3.0]]))
    >>> exp = np.exp(np.array([[2.5, 1.0], [1.0, 2.5]]))
    >>> frozen_dists = obs_over_exp_fitter(obs, exp, stats.norm, log=True)
    >>> for exp_val in frozen_dists:
    ...     print('%0.2f: %s distribution with mean %.2f and variance %.2f'
    ...           % ((exp_val, frozen_dists[exp_val].dist.name,) +
    ...              frozen_dists[exp_val].stats(moments='mv')))
    2.72: norm distribution with mean 1.00 and variance 0.17
    12.18: norm distribution with mean 2.50 and variance 0.17
    """
    # compute variance and mean scaling factors
    variance_factor = compute_obs_over_exp_variance_factor(
        regional_obs, regional_exp, log=log)
    mean_factor = compute_obs_over_exp_mean_factor(
        regional_obs, regional_exp, log=log)

    return variance_only_fitter(regional_exp, dist_gen, variance_factor,
                                mean_factor=mean_factor, log=log,
                                expected_value=expected_value)


def log_log_fit_fitter(regional_obs, regional_exp, dist_gen, log=False,
                       expected_value=None):
    """
    Computes distributions for observed counts, assuming that the mean-variance
    relationship is quadratic with a variance scaling constant estaimated by a
    log-log fit.

    Parameters
    ----------
    regional_obs : numpy array
        Square, symmetric array of observed counts for this region.
    regional_exp : numpy array
        Square, symmetric array of expected counts for this region.
    dist_gen : scipy.stats.rv_generic
        The distribution to use.
    log: bool, optional
        Pass True to compute distributions appropriate for logged counts.
    expected_value : float, optional
        Specify a single expected value to compute the distribution for.

    Returns
    -------
    dict(float -> scipy.stats.rv_frozen)
        The keys are the expected values in ``regional_exp``. The value is the
        fitted distribution afted shifting to that expected value.
    """
    if log:
        raise NotImplementedError('log-log fit not implemented for logged data')

    # compute variance and mean scaling factors
    variance_factor = compute_log_log_fit_variance_factor(regional_obs)

    return variance_only_fitter(regional_exp, dist_gen, variance_factor,
                                log=log, expected_value=expected_value)


def variance_only_fitter(regional_exp, dist_gen, variance_factor,
                         mean_factor=1.0, log=False, expected_value=None):
    """
    Computes distributions for observed counts, assuming that the mean-variance
    relationship is quadratic, given a variance scaling factor, and, optionally,
    a mean scaling factor.

    Parameters
    ----------
    regional_exp : numpy array
        Square, symmetric array of expected counts for this region.
    dist_gen : scipy.stats.rv_generic
        The distribution to use.
    variance_factor : float
        The variance scaling factor for this region. The variance at a point is
        assumed to be ``variance_factor * exp_value**2`` where ``exp_value`` is
        the expected value at that point.
    mean_factor : float, optional.
        The mean scaling factor for this region. The mean at a point is assumed
        to be ``mean_factor * exp_value`` where ``exp_value`` is the expected
        value at that point. By default, this value is 1.0, meaning that the
        mean used to parametrize the distribution will be exactly the value read
        from the expected model.
    log: bool, optional
        Pass True to compute distributions appropriate for logged counts.
    expected_value : float, optional
        Specify a single expected value to compute the distribution for.
    """
    frozen_dists = {}

    # honor expected_value kwarg
    if expected_value is not None:
        exp_values = [expected_value]
    else:
        exp_values = flatten_regional_counts(regional_exp, discard_nan=True)

    for exp_value in exp_values:
        # skip expected values we've already seen before
        if exp_value in frozen_dists:
            continue

        # skip non-finite expected values
        if not np.isfinite(exp_value):
            continue

        # compute universal intermediate parameters mu and sigma_2
        if log:
            mu = np.log(exp_value) + mean_factor
            sigma_2 = variance_factor
        else:
            mu = mean_factor * exp_value
            sigma_2 = variance_factor * exp_value ** 2

        # create appropriate frozen distribution
        frozen_dist = freeze_distribution(dist_gen, mu, sigma_2)

        # store frozen dist
        frozen_dists[exp_value] = frozen_dist

    return frozen_dists


def bias_frozen_dist(frozen_dist, bias_factor, log=False):
    """
    Add a multiplicative bias to a frozen distribution, returning a new frozen
    distribution created through ``freeze_distribution()``.

    Parameters
    ----------
    frozen_dist : scipy.stats.rv_frozen
        The distribution to bias.
    bias_factor : float
        The multiplicative factor with which to bias the distribution.
    log : boolean, optional
        Whether or not the frozen distribtion should be biased in log-space.

    Returns
    -------
    scipy.stats.rv_frozen
        The biased distribution.

    Examples
    --------
    >>> frozen_dist = stats.norm(loc=5.0, scale=np.sqrt(3.0))
    >>> biased_dist = bias_frozen_dist(frozen_dist, 2.0)
    >>> print('%s distribution with mean %.2f and variance %.2f'
    ...       % ((biased_dist.dist.name,) + biased_dist.stats(moments='mv')))
    norm distribution with mean 10.00 and variance 12.00
    """
    # get mean and standard deviation from old
    mu, sigma_2 = frozen_dist.stats(moments='mv')

    # add bias
    if not log:
        mu *= bias_factor
        sigma_2 *= bias_factor ** 2
    else:
        mu += np.log(bias_factor)

    return freeze_distribution(frozen_dist.dist, mu, sigma_2)


def freeze_distribution(dist_gen, mu, sigma_2):
    """
    Create a frozen distribution of a given type, given a mean and variance.

    Parameters
    ----------
    dist_gen : scipy.stats.rv_generic
        The distribution to use.
    mu : float
        The desired mean.
    sigma_2 : float
        The desired variance.

    Returns
    -------
    scipy.stats.rv_frozen
        A frozen distribution of the specified type with specified mean and
        variance.

    Notes
    -----
    This function does not perform any fitting, because it assumes that the
    first two moments directly and uniquely identify the desired distribution.

    Examples
    --------
    >>> frozen_dist = freeze_distribution(stats.poisson, 4.0, 4.0)
    >>> print('%s distribution with mean %.2f and variance %.2f'
    ...       % ((frozen_dist.dist.name,) + frozen_dist.stats(moments='mv')))
    poisson distribution with mean 4.00 and variance 4.00

    >>> frozen_dist = freeze_distribution(stats.nbinom, 4.0, 3.0)
    falling back to Poisson 3.00 < 4.00
    >>> print('%s distribution with mean %.2f and variance %.2f'
    ...       % ((frozen_dist.dist.name,) + frozen_dist.stats(moments='mv')))
    poisson distribution with mean 4.00 and variance 4.00

    >>> frozen_dist = freeze_distribution(stats.nbinom, 3.0, 4.0)
    >>> print('%s distribution with mean %.2f and variance %.2f'
    ...       % ((frozen_dist.dist.name,) + frozen_dist.stats(moments='mv')))
    nbinom distribution with mean 3.00 and variance 4.00

    >>> frozen_dist = freeze_distribution(stats.norm, 4.0, 3.0)
    >>> print('%s distribution with mean %.2f and variance %.2f'
    ...       % ((frozen_dist.dist.name,) + frozen_dist.stats(moments='mv')))
    norm distribution with mean 4.00 and variance 3.00

    >>> frozen_dist = freeze_distribution(stats.logistic, 4.0, 3.0)
    >>> print('%s distribution with mean %.2f and variance %.2f'
    ...       % ((frozen_dist.dist.name,) + frozen_dist.stats(moments='mv')))
    logistic distribution with mean 4.00 and variance 3.00
    """
    if dist_gen.name == 'norm':
        frozen_dist = dist_gen(loc=mu, scale=np.sqrt(sigma_2))
    elif dist_gen.name == 'logistic':
        frozen_dist = dist_gen(loc=mu, scale=np.sqrt(3 * sigma_2) / np.pi)
    elif dist_gen.name == 'nbinom' and sigma_2 > mu:
        p = 1 - (sigma_2 - mu) / sigma_2
        n = mu ** 2 / (sigma_2 - mu)
        frozen_dist = dist_gen(n, p)
    elif dist_gen.name == 'nbinom' and not sigma_2 > mu:
        print('falling back to Poisson %0.2f < %0.2f' % (sigma_2, mu))
        frozen_dist = stats.poisson(mu=mu)
    elif dist_gen.name == 'poisson':
        frozen_dist = dist_gen(mu=mu)
    else:
        raise NotImplementedError('combination not supported')
    return frozen_dist


def fit_distribution(dist_gen, data):
    """
    Fit a distribution of a given type to data, falling back to computational
    approximations based on the sample mean and sample variance if an MLE
    estimator is not available.

    Parameters
    ----------
    dist_gen : scipy.stats.rv_generic
        The distribution to use.
    data : sequence of float
        The data to fit.

    Returns
    -------
    scipy.stats.rv_frozen
        A frozen distribution of the specified type fit to the data.

    Notes
    -----
    This function attempts to use the ``fit()`` function on the dist_gen if it
    is available. If it is not available, it will compute the sample mean and
    sample variance of the data, and send these parameters to
    ``freeze_distribution()``, which will create a distribution without fitting.
    """
    if hasattr(dist_gen, 'fit'):
        frozen_dist = dist_gen(*dist_gen.fit(data))
    else:
        try:
            mu = np.nanmean(data)
            sigma_2 = np.nanvar(data)
            frozen_dist = freeze_distribution(dist_gen, mu, sigma_2)
        except NotImplementedError:
            raise NotImplementedError('distribution scipy.stats.%s has no '
                                      'method fit() and no approximation is '
                                      'available' % dist_gen.name)

    return frozen_dist
