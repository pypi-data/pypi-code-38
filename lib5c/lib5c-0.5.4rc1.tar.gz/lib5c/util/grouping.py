"""
Module for constructing groups of points with particular properties.
"""

import numpy as np

from lib5c.util.sampling import uniform_range_coverage_sample
from lib5c.util.counts import flatten_obs_and_exp, flatten_obs_and_exp_counts, \
    distance_filter


def group_obs_by_exp(obs, exp, num_groups=100, group_fractional_tolerance=0.1,
                     log=True, min_group_count=2, exclude_offdiagonals=5):
    """
    Groups observed points according to their expected values.

    Parameters
    ----------
    obs : np.ndarray or dict of np.ndarray
        Vector, matrix, or counts dict of observed values.
    exp : np.ndarray or dict of np.ndarray
        Vector, matrix, or counts dict of expected values.
    num_groups : int
        The number of groups to make.
    group_fractional_tolerance : float
        The width of each group, specified as a fractional tolerance in the
        expected value.
    log : bool
        Pass True to space the groups out logarithmically.
    min_group_count : int
        Discard groups that have fewer than this many values in them.
    exclude_offdiagonals : int
        If `obs` and `exp` are not already vectors, discard this many
        off-diagonals from their square matrices before flattening. Pass 0 to
        exclude only the exact diagonal, and pass -1 to exclude nothing.

    Returns
    -------
    np.ndarray, list of np.ndarray
        The first array contains the expected values chosen as the centers of
        the groups. The list contains each group as an array of observed values.
    """
    # distance filter and flatten if appropriate
    if type(exp) == dict and len(exp[exp.keys()[0]].shape) == 2:
        exp = distance_filter(exp, k=exclude_offdiagonals)
        obs, exp = flatten_obs_and_exp_counts(obs, exp)
    elif len(exp.shape) == 2:
        exp = distance_filter(exp, k=exclude_offdiagonals)
        obs, exp = flatten_obs_and_exp(obs, exp)

    # establish group centers
    exps = uniform_range_coverage_sample(exp, num_groups, log_space=log)

    # establish groups
    groups = [obs[np.abs(e - exp) / e < group_fractional_tolerance]
              for e in exps]

    # filter groups which are too small
    if min_group_count > 1:
        filtered_exps = []
        filtered_groups = []
        for i in range(len(exps)):
            if len(groups[i]) >= min_group_count:
                filtered_exps.append(exps[i])
                filtered_groups.append(groups[i])
        return np.array(filtered_exps), filtered_groups
    return exps, groups
