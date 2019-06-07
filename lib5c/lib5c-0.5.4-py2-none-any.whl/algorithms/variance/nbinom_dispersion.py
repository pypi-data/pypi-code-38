"""
Module for estimating negative binomial dispersion parameters for 5C interaction
data.
"""

import numpy as np
import scipy.stats as stats
from scipy.special import digamma

from lib5c.util.distributions import convert_parameters


def dispersion_to_variance(disp, exp):
    """
    Converts a dispersion estimate to a variance by applying it to the expected
    value via the relationship ``var = exp + disp * exp**2``.

    Parameters
    ----------
    disp : float or np.ndarray
        The dispersion.
    exp : float or np.ndarray
        The expected value.

    Returns
    -------
    float or np.ndarray
        The variance.
    """
    return exp + disp * exp**2


def variance_to_dispersion(var, exp, min_disp=None):
    """
    Converts a variance estimate to a dispersion estimate by reversing the
    relationship in ``dispersion_to_variance()``. Only defined for points where
    ``var > exp``. If ``var`` is the sample variance and ``exp`` is the sample
    mean, this is the equivalent to the method-of-moments estimate of the
    dispersion parameter.

    Parameters
    ----------
    var : float or np.ndarray
        The variance.
    exp : float or np.ndarray
        The expected value.
    min_disp : float, optional
        Pass a value to enter a lenient mode where underdispersed points will be
        allowed, but will not be assigned a dispersion value from the
        statistical relationship. Underdispersed points will instead be assigned
        the ``min_disp`` value.

    Returns
    -------
    float or np.ndarray
        The dispersion.
    """
    if min_disp is None:
        assert np.all(var > exp)
        return (var - exp) / exp**2
    else:
        idx_od = var > exp + 0.001
        disp = np.tile(min_disp, var.shape)
        disp[idx_od] = variance_to_dispersion(var[idx_od], exp[idx_od])
        return disp


def nb_pmf(k, m, alpha):
    """
    The negative binomial PMF, parametrized in terms of a mean ``m`` and a
    dispersion ``alpha``.

    Parameters
    ----------
    k : int or np.ndarray
        The observed value.
    m : float or np.ndarray
        The expected or mean value.
    alpha : float or np.ndarray
        The dispersion parameter.

    Returns
    -------
    float or np.ndarray
        The value of the PMF.
    """
    v = dispersion_to_variance(alpha, m)
    return stats.nbinom(*convert_parameters(m, v, stats.nbinom)).pmf(k)


def nb_nll(disp, obs, exp):
    """
    The negative log likelihood of observed data ``obs`` given mean/expected
    value ``exp`` and dispersion parameter ``disp``.

    Parameters
    ----------
    disp : float or np.ndarray
        The dispersion parameter.
    obs : int or np.ndarray
        The observed data.
    exp : float or np.ndarray
        The mean/expected value.

    Returns
    -------
    float
        The negative log likelihood.
    """
    return -np.sum(np.log(nb_pmf(obs, exp, disp)))


def nb_nll_derivative(disp, obs):
    """
    Derivative of the negative binomial log-likelihood function with respect to
    the dispersion parameter, given observed data.

    This function is vectorized. Pass one dispersion and a vector of observed
    values to evaluate the derivative with just that one dispersion on the
    collection of all the observed values passed. Pass a vector of dispersions
    and a matrix of observed values to compute a vector of derivative
    evaluations, using the ``i`` th element of the dispersion vector and the
    ``i`` th row of the observed matrix to compute the ``i`` th derivative
    evaluation.

    Parameters
    ----------
    disp : float or np.ndarray
        The negative binomial dispersion parameter.
    obs : np.ndarray
        The observed values. If ``disp`` is a vector, this should be a matrix
        whose number of rows equals the length of ``disp``.

    Returns
    -------
    float or np.ndarray
        The derviative evaluation(s).
    """
    n = float(obs.shape[-1])
    disp = np.asarray(disp)
    if len(disp.shape) == 1:
        disp_wide = disp[:, np.newaxis]
    else:
        disp_wide = disp
    return np.sum(digamma(obs + 1 / disp_wide), axis=-1) - \
        n * digamma(1 / disp) - n * np.log(1 + disp * np.sum(obs / n, axis=-1))
