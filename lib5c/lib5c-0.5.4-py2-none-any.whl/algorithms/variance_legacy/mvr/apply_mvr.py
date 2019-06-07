import numpy as np

from lib5c.util.parallelization import parallelize_regions


def apply_mvr(expected_matrix, mvr):
    new_expected_matrix = np.zeros_like(expected_matrix, dtype=float)
    variance_matrix = np.zeros_like(expected_matrix, dtype=float)
    for i in range(len(expected_matrix)):
        for j in range(i + 1):
            mu, sigma2 = mvr(expected_matrix[i, j])
            new_expected_matrix[i, j] = mu
            new_expected_matrix[j, i] = mu
            variance_matrix[i, j] = sigma2
            variance_matrix[j, i] = sigma2
    return new_expected_matrix, variance_matrix


apply_mvr_parallel = parallelize_regions(apply_mvr)
