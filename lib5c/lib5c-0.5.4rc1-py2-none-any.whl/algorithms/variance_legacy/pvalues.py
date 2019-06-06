import numpy as np

from lib5c.algorithms.distributions_legacy.fitting import freeze_distribution,\
    bias_frozen_dist
from lib5c.util.parallelization import parallelize_regions


def call_pvalues(obs_matrix, exp_matrix, var_matrix, dist_gen, log=False,
                 pseudocount=1.0, bias=None):
    pvalues = np.zeros_like(obs_matrix)
    dists = {}
    if bias is not None:
        bias_matrix = np.outer(bias, bias)
        obs_matrix *= bias_matrix
    for i in range(len(obs_matrix)):
        for j in range(i + 1):
            # skip points with infinite anything
            if (not np.isfinite(obs_matrix[i, j]) or
                    not np.isfinite(exp_matrix[i, j]) or
                    not np.isfinite(var_matrix[i, j])):
                pvalue = np.nan
            else:
                # make sure we have a distribution for this expected value in
                # the cache
                if exp_matrix[i, j] not in dists:
                    dists[exp_matrix[i, j]] = freeze_distribution(
                        dist_gen, exp_matrix[i, j], var_matrix[i, j])

                # if/else to get a reference to the right distribution to use
                # here, biasing it if necessary
                if bias is not None:
                    dist = bias_frozen_dist(dists[exp_matrix[i, j]],
                                            bias[i] * bias[j], log=log)
                else:
                    dist = dists[exp_matrix[i, j]]

                # compute a p-value
                if not log:
                    pvalue = dist.sf(obs_matrix[i, j])
                else:
                    pvalue = dist.sf(np.log(obs_matrix[i, j] + pseudocount))

            # write the p-value into the output matrix
            pvalues[i, j] = pvalue
            pvalues[j, i] = pvalue
    return pvalues


call_pvalues_parallel = parallelize_regions(call_pvalues)
