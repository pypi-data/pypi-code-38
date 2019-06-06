import numpy as np
from scipy.ndimage.filters import generic_filter

from lib5c.util.parallelization import parallelize_regions


def estimate_moments(group_values, dist_gen, log=False, pseudocount=1.0):
    if log:
        group_values = np.log(group_values + pseudocount)
    if dist_gen.name == 'norm':
        return np.nanmean(group_values), np.nanvar(group_values)
    elif hasattr(dist_gen, 'fit'):
        frozen_dist = dist_gen(*dist_gen.fit(group_values))
        return frozen_dist.stats(moments='mv')
    elif dist_gen.name == 'poisson':
        return np.nanmean(group_values), np.nanmean(group_values)
    else:
        return np.nanmean(group_values), np.nanvar(group_values)


def make_moment_matrices(groups, dist_gen, log=False):
    expected_matrix = np.zeros_like(groups[0]['indices'], dtype=float)
    variance_matrix = np.zeros_like(groups[0]['indices'], dtype=float)
    for group in groups.values():
        mean, variance = estimate_moments(group['values'], dist_gen, log=log)
        expected_matrix[group['targets']] = mean
        variance_matrix[group['targets']] = variance
    expected_matrix = np.maximum(expected_matrix, expected_matrix.T)
    variance_matrix = np.maximum(variance_matrix, variance_matrix.T)
    return expected_matrix, variance_matrix


make_moment_matrices_parallel = parallelize_regions(make_moment_matrices)


def donut_moment_estimate(obs_matrix, dist_gen, moment=1, p=5, w=15, log=False,
                          pseudocount=1.0):
    footprint = [[1 if i != w and ((i > p + w or i < w - p) or
                                   (j < w - p or j > p + w)) and j != w
                  else 0
                  for i in xrange(2 * w + 1)] for j in xrange(2 * w + 1)]
    return generic_filter(
        obs_matrix,
        lambda x: estimate_moments(
            x,
            dist_gen,
            log=log,
            pseudocount=pseudocount
        )[moment-1],
        footprint=footprint,
        mode='constant'
    )


donut_moment_estimate_parallel = parallelize_regions(donut_moment_estimate)
