import numpy as np

from lib5c.util.parallelization import parallelize_regions
from lib5c.util.sampling import uniform_range_coverage_sample


def group_by_bin_distance(matrix, window_radius):
    """
    Groups elements in a matrix according to their distance from the diagonal.

    Parameters
    ----------
    matrix : np.ndarray
        The matrix to group values in.
    window_radius : int
        How many bins away to include values when grouping.

    Returns
    -------
    Dict[int, [Dict[str, np.ndarray]]]
        Each inner dict represents one group and has the following structure::

            {
                'incides': np.ndarray,
                'values': np.ndarray,
                'targets': np.ndarray
            }

        ``'incides'`` and ``'targets'`` will be boolean arrays of the same size
        and shape as ``matrix``. ``'values'`` will be the values of ``matrix``
        refered to by ``'incides'`` as a one-dimensional array. The outer dict
        maps integer distances to the inner dict representing the group at that
        distance.

    Examples
    --------
    >>> import numpy as np
    >>> a = np.arange(16).reshape((4,4))
    >>> a
    array([[ 0,  1,  2,  3],
           [ 4,  5,  6,  7],
           [ 8,  9, 10, 11],
           [12, 13, 14, 15]])
    >>> groups = group_by_bin_distance(a, 1)
    >>> groups[1]['indices']
    array([[ True,  True,  True, False],
           [False,  True,  True,  True],
           [False, False,  True,  True],
           [False, False, False,  True]])
    >>> groups[1]['values']
    array([ 0,  1,  2,  5,  6,  7, 10, 11, 15])
    >>> groups[1]['targets']
    array([[False,  True, False, False],
           [False, False,  True, False],
           [False, False, False,  True],
           [False, False, False, False]])
    """
    # this list will store information about the groups
    groups = {}

    # there will be one group for every row
    for i in range(len(matrix)):
        # establish targets for this group
        group_targets = np.zeros_like(matrix, dtype=bool)
        for j in range(len(matrix) - i):
            group_targets[j, i+j] = True

        # establish indices for this group
        group_indices = np.zeros_like(matrix, dtype=bool)
        for k in range(max(i-window_radius, 0),
                       min(i+window_radius+1, len(matrix))):
            for j in range(len(matrix) - k):
                group_indices[j, k+j] = True

        # save information about this group to a dict
        groups[i] = {'targets': group_targets,
                     'indices': group_indices,
                     'values' : matrix[group_indices]}

    return groups


group_by_bin_distance_parallel = parallelize_regions(group_by_bin_distance)


def group_by_expected_value(obs_matrix, exp_matrix, fractional_tolerance,
                            centers=None, n_centers=None):
    """
    Groups elements in a matrix according to their distance from the diagonal.

    Parameters
    ----------
    obs_matrix : np.ndarray
        The matrix containing the actual values to group.
    exp_matrix : np.ndarray
        The matrix containing the expected values to be used to construct the
        groups.
    fractional_tolerance : float
        The fractional tolerance that controls how wide the ranges of expected
        values will be in each group.
    centers : Optional[List[float]]
        If passed, specifies the expected values to be used as the centers for
        the groups. If not passed, every unique expected value will be used as
        the center of its own group.

    Returns
    -------
    Dict[float, [Dict[str, np.ndarray]]]
        Each inner dict represents one group and has the following structure::

            {
                'incides': np.ndarray,
                'values': np.ndarray,
                'targets': np.ndarray
            }

        ``'incides'`` and ``'targets'`` will be boolean arrays of the same size
        and shape as ``matrix``. ``'values'`` will be the values of ``matrix``
        refered to by ``'incides'`` as a one-dimensional array. The outer dict
        maps float expected values to the inner dict representing the group at
        that expected value.
    """
    # this list will store information about the groups
    groups = {}

    # resolve n_centers
    if n_centers is None:
        n_centers = len(obs_matrix)

    # resolve centers
    if centers is None:
        centers = uniform_range_coverage_sample(
            np.unique(exp_matrix[np.isfinite(exp_matrix)]),
            n_centers,
            log_space=True
        )

    # there will be one group for every center
    for center in centers:
        # establish targets for this group
        group_targets = np.triu(exp_matrix == center)

        # establish indices for this group
        group_indices = np.triu(
            np.abs(exp_matrix-center)/center <= fractional_tolerance)

        # save information about this group to a dict
        groups[center] = {'targets': group_targets,
                          'indices': group_indices,
                          'values' : obs_matrix[group_indices]}

    return groups


group_by_expected_value_parallel = parallelize_regions(group_by_expected_value)
