import numpy as np


def lognorm_to_norm(mean, var):
    """
    Convert mean and variance from an estimate of lognormal distribution to that for the
    equivalent normal.
    """
    return np.exp(mean + 0.5 * var), np.exp(2 * mean + var) * (np.exp(var) - 1)


def norm_to_lognorm(mean, var):
    """
    Convert mean and variance from an estimate of normal distribution to that for the
    equivalent lognormal.
    """
    return (
        2 * np.log(mean) - 0.5 * np.log(var + mean ** 2),
        -2 * np.log(mean) + np.log(var + mean ** 2),
    )
