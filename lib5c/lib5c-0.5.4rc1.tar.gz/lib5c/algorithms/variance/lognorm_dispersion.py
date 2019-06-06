"""
Module for estimating lognormal dispersion parameters for 5C interaction data.
"""

import numpy as np


def dispersion_to_variance(disp, exp):
    """
    Converts a dispersion estimate to a variance by applying it to the expected
    value of unlogged counts.

    Parameters
    ----------
    disp : float or np.ndarray
        The dispersion (variance of logged values).
    exp : float or np.ndarray
        The expected value (of unlogged values).

    Returns
    -------
    float or np.ndarray
        The variance.
    """
    mu = np.log(exp) - disp / 2  # convert exp to mean of log counts
    return dispersion_to_variance_direct(disp, mu)


def dispersion_to_variance_direct(disp, mu):
    """
    Converts a dispersion estimate to a variance by applying it to the expected
    value of logged counts.

    Parameters
    ----------
    disp : float or np.ndarray
        The dispersion (variance of logged values).
    mu : float or np.ndarray
        The expected value (of logged values).

    Returns
    -------
    float or np.ndarray
        The variance.
    """
    return (np.exp(disp) - 1) * np.exp(2 * mu + disp)


def variance_to_dispersion(var, exp):
    """
    Converts a variance estimate to a dispersion by applying it to the expected
    value of unlogged counts.

    Parameters
    ----------
    var : float or np.ndarray
        The variance (of unlogged values).
    exp : float or np.ndarray
        The expected value (of unlogged values).

    Returns
    -------
    float or np.ndarray
        The dispersion (variance of logged values).
    """
    return np.log(1 + var / exp**2)
