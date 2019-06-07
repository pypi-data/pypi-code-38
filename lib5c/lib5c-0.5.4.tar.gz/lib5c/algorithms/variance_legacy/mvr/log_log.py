import numpy as np

from lib5c.algorithms.distributions_legacy.variance import quadratic_log_log_fit
from lib5c.util.parallelization import parallelize_regions


def learn_mvr(groups, plot_outfile=None):
    # collect data from groups
    sample_means = np.array([np.nanmean(group['values'])
                             for group in groups.values()
                             if len(group['values'])])
    sample_vars = np.array([np.nanvar(group['values'])
                            for group in groups.values()
                            if len(group['values'])])

    # filter nans
    filtered_means = sample_means[np.isfinite(sample_means) &
                                  np.isfinite(sample_vars)]
    filtered_vars = sample_vars[np.isfinite(sample_means) &
                                np.isfinite(sample_vars)]

    # fit
    f = quadratic_log_log_fit(filtered_means, filtered_vars)

    # plot visualization of fit
    if plot_outfile is not None:
        import matplotlib.pyplot as plt
        plt.clf()
        ax = plt.gca()
        ax.scatter(np.log(filtered_means), np.log(filtered_vars), c='r')
        ax.scatter(np.log(filtered_means), np.log(f(filtered_means)), c='b')
        plt.xlabel('log mean')
        plt.ylabel('log variance')
        plt.savefig(plot_outfile, bbox_inches='tight')

    return lambda mu: (mu, f(mu))


learn_mvr_parallel = parallelize_regions(learn_mvr)


def learn_mvr_from_matrices(exp_matrix, var_matrix, plot_outfile=None):
    # filter nans
    filtered_means = exp_matrix[np.isfinite(exp_matrix) &
                                np.isfinite(var_matrix) &
                                np.triu(np.ones_like(exp_matrix, dtype=bool))]
    filtered_vars = var_matrix[np.isfinite(exp_matrix) &
                               np.isfinite(var_matrix) &
                               np.triu(np.ones_like(exp_matrix, dtype=bool))]

    # fit
    f = quadratic_log_log_fit(filtered_means, filtered_vars)

    # plot visualization of fit
    if plot_outfile is not None:
        import matplotlib.pyplot as plt
        plt.clf()
        ax = plt.gca()
        ax.scatter(np.log(filtered_means), np.log(filtered_vars), c='r')
        ax.scatter(np.log(filtered_means), np.log(f(filtered_means)), c='b')
        plt.xlabel('log mean')
        plt.ylabel('log variance')
        plt.savefig(plot_outfile, bbox_inches='tight')

    return lambda mu: (mu, f(mu))


learn_mvr_from_matrices_parallel = parallelize_regions(learn_mvr_from_matrices)
