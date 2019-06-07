import numpy as np

from lib5c.algorithms.distributions_legacy.variance import\
    compute_obs_over_exp_variance_factor, compute_obs_over_exp_mean_factor
from lib5c.util.parallelization import parallelize_regions


def learn_mvr(obs_matrix, exp_matrix, log=False):
    variance_factor = compute_obs_over_exp_variance_factor(
        obs_matrix, exp_matrix, log=log)
    mean_factor = compute_obs_over_exp_mean_factor(
        obs_matrix, exp_matrix, log=log)
    if log:
        return lambda mu: (np.log(mu) + mean_factor, variance_factor)
    else:
        return lambda mu: (mu * mean_factor, variance_factor * mu ** 2)


learn_mvr_parallel = parallelize_regions(learn_mvr)
