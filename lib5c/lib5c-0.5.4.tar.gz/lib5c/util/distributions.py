"""
Module containing utility functions for parametrizing statistical distributions.
"""

import numpy as np
import scipy.stats as stats

from lib5c.util.parallelization import parallelize_regions


def log_parameters(m, v):
    """
    Attempts to guess appropriate log-scale mean and variance parameters given
    non-log scale estimators of these quantities, under the assumptions of a
    lognormal model.

    Based on https://en.wikipedia.org/wiki/Log-normal_distribution#Notation

    Parameters
    ----------
    m : float
        The non-log scale mean.
    v : float
        The non-log scale variance.

    Returns
    -------
    float, float
        The first float is the log-scale mean, the second is the log-scale
        variance.

    Notes
    -----
    This function is array-safe.

    Examples
    --------
    >>> mu = 2  # mean of a normal random variable X
    >>> sigma_2 = 16  # variance of X
    >>> scale = np.exp(mu)  # parameter conversion for scipy.stats.lognorm
    >>> s = np.sqrt(sigma_2)  # ditto
    >>> y = stats.lognorm(s=s, scale=scale)  # a lognormal RV: exp(X) = Y
    >>> m, v = y.stats(moments='mv')  # mean and variance of Y
    >>> m, v
    (array(22026.4657948...), array(4.31123106e+15))
    >>> log_parameters(m, v)  # recover moments of X from moments of Y
    (2.0, 16.0)
    """
    return np.log(m / np.sqrt(1 + v/m**2)), np.log(1 + v/m**2)


def convert_parameters(mu, sigma_2, dist_gen, log=False):
    """
    Obtain correct scipy.stats parameterizations for selected one- and two-
    parameter distributions given a desired mean and variance.

    Parameters
    ----------
    mu : float
        The mean of the desired distribution.
    sigma_2 : float
        The variance of the desired distribution.
    dist_gen : scipy.stats.rv_generic
        The target distribution.
    log : bool
        Pass True to attempt to convert exp and var to log-scale.

    Returns
    -------
    tuple of float
        The appropriate scipy.stats parameters.
    """
    mu = np.array(mu) if hasattr(mu, '__len__') else np.array([mu])
    sigma_2 = np.array(sigma_2) if hasattr(sigma_2, '__len__')\
        else np.array([sigma_2])
    if log:
        mu, sigma_2 = log_parameters(mu, sigma_2)
    if dist_gen.name == 'norm':
        return mu, np.sqrt(sigma_2)
    elif dist_gen.name == 'logistic':
        return mu, np.sqrt(3 * sigma_2) / np.pi
    elif dist_gen.name == 'nbinom':
        # overwrite sigma_2's that are below mu (force to Poisson)
        idx = sigma_2 < mu + 0.001
        sigma_2[idx] = mu[idx] + 0.001
        # compute n and p
        return mu**2 / (sigma_2 - mu), 1 - (sigma_2 - mu) / sigma_2
    elif dist_gen.name == 'poisson':
        return (mu,)
    else:
        raise NotImplementedError(
            'distribution %s not supported' % dist_gen.name)


def freeze_distribution(dist_gen, mu, sigma_2, log=False):
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
    log : bool
        Pass True to attempt to convert mu and sigma_2 to log-scale.

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
    >>> print('%s distribution with mean %.2f and variance %.2f'
    ...       % ((frozen_dist.dist.name,) + frozen_dist.stats(moments='mv')))
    nbinom distribution with mean 4.00 and variance 4.00

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
    >>> mu = 2  # mean of a normal random variable X
    >>> sigma_2 = 16  # variance of X
    >>> scale = np.exp(mu)  # parameter conversion for scipy.stats.lognorm
    >>> s = np.sqrt(sigma_2)  # ditto
    >>> y = stats.lognorm(s=s, scale=scale)  # a lognormal RV: exp(X) = Y
    >>> m, v = y.stats(moments='mv')  # mean and variance of Y
    >>> m, v
    (array(22026.4657948...), array(4.31123106e+15))
    >>> frozen_dist = freeze_distribution(stats.logistic, m, v, log=True)
    >>> print('%s distribution with mean %.2f and variance %.2f'
    ...       % ((frozen_dist.dist.name,) + frozen_dist.stats(moments='mv')))
    logistic distribution with mean 2.00 and variance 16.00
    """
    return dist_gen(*convert_parameters(mu, sigma_2, dist_gen, log=log))


@parallelize_regions
def call_pvalues(obs, exp, var, dist_gen, log=False):
    """
    Call right-tail p-values for obs against a theoretical distribution whose
    family is specified by dist_gen an whose first two moments are specified by
    exp and var, respectively.

    Parameters
    ----------
    obs : float
        The observed value to call a p-value for.
    exp, var : float
        The first two moments of the null distribution.
    dist_gen : scipy.stats.rv_generic or str
        The null distribution to parameterize. If a string is passed this will
        be replaced with `getattr(scipy.stats, dist_gen)`.
    log : bool
        Pass True to attempt to convert exp and var to log-scale.

    Returns
    -------
    float
        The right-tail p-value.

    Notes
    -----
    This function is array-safe.
    """
    if type(dist_gen) == str:
        dist_gen = getattr(stats, dist_gen)
    params = convert_parameters(exp, var, dist_gen, log=log)
    if hasattr(dist_gen, 'pmf'):
        return dist_gen.sf(obs, *params) + dist_gen.pmf(obs, *params)
    return dist_gen.sf(obs, *params)
