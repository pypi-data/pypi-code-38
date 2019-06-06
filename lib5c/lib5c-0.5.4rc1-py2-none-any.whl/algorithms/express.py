"""
Module for implementation of the "Express" algorithm from Sauria et al. 2015.
"""

import numpy as np

from lib5c.util.parallelization import parallelize_regions


@parallelize_regions
def express_normalize_matrix(obs_matrix, exp_matrix, max_iter=1000, eps=1e-4):
    """
    Express balance a matrix given a corresponding expected matrix.

    Parameters
    ----------
    obs_matrix : np.ndarray
        The matrix to normalize.
    exp_matrix : np.ndarray
        The expected matrix corresponding to the obs_matrix.
    max_iter : int
        The maximum number of iterations.
    eps : float
        When the fractional change in the residual is less than this number, the
        algorithm is considered to have converged and will stop iterating.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, List[float]]
        The first element of the tuple is the normalized matrix. The second
        element is the multiplicative bias vector. The third element is a list
        containing the L1 norm of the residual at every iteration.
    """
    # log transform
    log_obs = np.log(obs_matrix + 1)
    log_exp = np.log(exp_matrix + 1)

    # initialize bias vector
    bias_factors = np.zeros(len(log_obs))

    # counter for iterations
    i = 0

    # variables to track L1 error
    prev_err = np.inf
    curr_err = np.inf
    errs = []

    while i < max_iter and not (prev_err - curr_err) / prev_err < eps:
        # apply bias to expected
        log_corr_exp = \
            (log_exp.T + bias_factors).T + bias_factors

        # compute residual
        residual = log_obs - log_corr_exp

        # update each element of the bias vector
        for j in range(len(log_obs)):
            filtered_residual = \
                residual[:, j][(np.isfinite(residual[:, j])) &
                               (log_obs[:, j] != 0)]
            update = np.sum(filtered_residual) / (2 * len(filtered_residual))
            if np.isfinite(update):
                bias_factors[j] += update

        # increment iteration counter
        i += 1

        # update error
        prev_err = curr_err
        curr_err = np.linalg.norm(residual[np.isfinite(residual)], ord=1)
        errs.append(curr_err)

    # apply optimized bias to observed
    log_corr_obs = (log_obs.T - bias_factors).T - bias_factors

    # undo log transform
    normalized_matrix = np.exp(log_corr_obs) - 1
    bias_factors = np.exp(bias_factors)

    # force normalized matrix to be non-negative
    normalized_matrix[normalized_matrix < 0] = 0

    return normalized_matrix, bias_factors, errs


@parallelize_regions
def joint_express_normalize(obs_matrices, exp_matrices, max_iter=1000,
                            eps=1e-4):
    """
    Express balance a set of matrices given a set of corresponding expected
    matrices, using a single shared bias vector.

    Parameters
    ----------
    obs_matrices : List[np.ndarray]
        The matrix to normalize.
    exp_matrices : List[np.ndarray]
        The expected matrix corresponding to the obs_matrix.
    max_iter : int
        The maximum number of iterations.
    eps : float
        When the fractional change in the residual is less than this number, the
        algorithm is considered to have converged and will stop iterating.

    Returns
    -------
    Tuple[List[np.ndarray], np.ndarray, List[float]]
        The first element of the tuple is the list of normalized matrices. The
        second element is the multiplicative bias vector. The third element is a
        list containing the L1 norm of the residual at every iteration.
    """
    # log transform
    log_obs_matrices = [np.log(obs_matrix + 1) for obs_matrix in obs_matrices]
    log_exp_matrices = [np.log(exp_matrix + 1) for exp_matrix in exp_matrices]

    # initialize bias vector
    bias_factors = np.zeros(len(log_obs_matrices[0]))

    # counter for iterations
    i = 0

    # variables to track L1 error
    prev_err = np.inf
    curr_err = np.inf
    errs = []

    while i < max_iter and not (prev_err - curr_err) / prev_err < eps:
        # apply bias to expected
        log_corr_exp_matrices = [
            (log_exp_matrix.T + bias_factors).T + bias_factors
            for log_exp_matrix in log_exp_matrices]

        # concatenate
        log_obs = np.concatenate([log_obs_matrices[k]
                                  for k in range(len(obs_matrices))])
        log_corr_exp = np.concatenate([log_corr_exp_matrices[k]
                                       for k in range(len(obs_matrices))])

        # compute residual
        residual = log_obs - log_corr_exp

        # update each element of the bias vector
        for j in range(len(log_obs_matrices[0])):
            filtered_residual = \
                residual[:, j][(np.isfinite(residual[:, j])) &
                               (log_obs[:, j] != 0)]
            update = np.sum(filtered_residual) / (2 * len(filtered_residual))
            if np.isfinite(update):
                bias_factors[j] += update

        # increment iteration counter
        i += 1

        # update error
        prev_err = curr_err
        curr_err = np.linalg.norm(residual[np.isfinite(residual)], ord=1)
        errs.append(curr_err)

    # apply optimized bias to observed
    log_corr_obs_matrices = [(log_obs_matrix.T - bias_factors).T - bias_factors
                             for log_obs_matrix in log_obs_matrices]

    # undo log transform
    normalized_matrices = [np.exp(log_corr_obs_matrix) - 1
                           for log_corr_obs_matrix in log_corr_obs_matrices]
    bias_factors = np.exp(bias_factors)

    # force normalized matrices to be non-negative
    for normalized_matrix in normalized_matrices:
        normalized_matrix[normalized_matrix < 0] = 0

    return normalized_matrices, bias_factors, errs
