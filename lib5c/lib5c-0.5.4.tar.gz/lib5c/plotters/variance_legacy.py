"""
Module for visualizing variance estimates over 5C data.

There are two different ways to plot a variance estimate:

1. from a single mean-variance scaling factor
2. from a set of frozen distributions

These two approaches are implemented in ``make_variance_plot()`` and
``make_variance_plot_from_frozen_dists()``, respectively.

A high-level convenience function, ``fit_and_plot()``, is provided that first
either fits distributions or determines the appropriate mean-variance scaling
factor using observed and expected counts matrices, and then calls the
appropriate variance plotting function.
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

from lib5c.util.parallelization import parallelize_regions
from lib5c.algorithms.distributions_legacy.fitting import \
    compute_obs_over_exp_variance_factor, compute_log_log_fit_variance_factor, \
    regional_simple_fitter, regional_shifted_fitter
from lib5c.util.system import check_outdir


@parallelize_regions
def fit_and_plot(outfile, obs_matrix, exp_matrix, region, mode='obs_over_exp',
                 dist='nbinom', log=False):
    """
    Convenience function that fits distributions to an observed counts matrix
    given an expected counts matrix and a modeling strategy, then plots the
    theoretical variance estimate over the empirical sample variance as a
    function of distance.

    Parameters
    ----------
    outfile : str
        String reference to a file to write the plot to.
    obs_matrix : np.ndarray
        The observed counts matrix for this region.
    exp_matrix : np.ndarray
        An expected counts matrix corresponding to ``obs_matrix``.
    region : str
        The region name as a string. This will be used in the plot title.
    mode : str, see options below
        The method to use to fit the distributions:
            * obs_over_exp: use quadratic mean-variance relationship estimated
              via sample variance of obs/exp counts across whole region
            * log_log_fit: use quadratic mean-variance relationship estimated
              via fitting quadratic curve in log-mean vs log-variance space
            * regional_simple: fit single distribution to obs/exp across whole
              region
            * regional_shifted: fit distributions by shifting counts from the
              whole region to the appropriate distance scale
    dist : str
        String identifier for what distribution to use. Must match the name of a
        subclass of ``scipy.stats.rv_generic``.
    log : bool
        Pass True to log the observed counts prior to fitting.
    """
    # resolve dist_gen
    dist_gen = getattr(stats, dist)

    if mode == 'log_log_fit':
        variance_factor = compute_log_log_fit_variance_factor(obs_matrix)
        make_variance_plot(
            obs_matrix, exp_matrix, variance_factor, outfile, region)
    elif mode == 'obs_over_exp':
        variance_factor = compute_obs_over_exp_variance_factor(
            obs_matrix, exp_matrix)
        make_variance_plot(
            obs_matrix, exp_matrix, variance_factor, outfile, region)
    elif mode == 'regional_simple':
        if log:
            raise NotImplementedError(
                '-v regional_simple -L combination not yet implemented')
        frozen_dist = regional_simple_fitter(
            obs_matrix, exp_matrix, dist_gen, log=log)
        make_variance_plot(
            obs_matrix, exp_matrix, frozen_dist.stats(moments='v'), outfile,
            region)
    elif mode == 'regional_shifted':
        if log:
            raise NotImplementedError(
                '-v regional_shifted -L combination not yet implemented')
        frozen_dists = regional_shifted_fitter(
            obs_matrix, exp_matrix, dist_gen, log=log)
        make_variance_plot_from_frozen_dists(
            obs_matrix, exp_matrix, frozen_dists, outfile, region)
    else:
        raise ValueError('invalid mode specified')


def make_variance_plot(regional_obs, regional_exp, regional_factor, outfile,
                       region):
    """
    Plot a theoretical variance estimate of the form
    ::

        regional_factor * regional_exp**2

    over the empirical sample variance as a function of distance.

    Parameters
    ----------
    regional_obs : np.ndarray
        The matrix of observed counts for this region.
    regional_exp : np.ndarray
        The matrix of expected counts for this region.
    regional_factor : float
        The mean-variance scaling factor for this region.
    outfile : str
        String reference to a file to write the plot to.
    region : str
        The region name as a string. This will be used for the plot title.
    """
    # check outdir
    check_outdir(outfile)

    # make offdiagonals
    offdiagonals = [np.diag(regional_obs, k=i)
                    for i in range(len(regional_obs))]

    # compute sample variance
    sample_variances = np.asarray([np.nanvar(offdiagonal, ddof=1)
                                   for offdiagonal in offdiagonals])
    log_sample_variances = np.log(sample_variances + 1)

    # compute predicted variance
    means = regional_exp[:, 0]
    pred_variances = regional_factor * means ** 2
    log_pred_variances = np.log(pred_variances + 1)

    # prepare x values
    xvals = range(len(offdiagonals))

    # plot
    plt.clf()
    plt.scatter(xvals, log_sample_variances, label='sample variance', c='b')
    plt.plot(xvals, log_pred_variances, label='predicted variance', c='r')
    plt.xlabel('Distance (bins)')
    plt.ylabel('Variance (log scale)')
    plt.title('Variance estimate for %s region' % region)
    plt.legend()
    plt.savefig(outfile, bbox_inches='tight')


def make_variance_plot_from_frozen_dists(regional_obs, regional_exp,
                                         frozen_dists, outfile, region):
    """
    Plot variance estimates lifted from a set of frozen distributions over the
    the empirical sample variance as a function of distance.

    Parameters
    ----------
    regional_obs : np.ndarray
        The matrix of observed counts for this region.
    regional_exp : np.ndarray
        The matrix of expected counts for this region.
    frozen_dists : Dict[float, scipy.stats.rv_frozen]
        A mapping from expected values to the appropriate frozen distribution to
        use at that expected value.
    outfile : str
        String reference to a file to write the plot to.
    region : str
        The region name as a string. This will be used for the plot title.
    """
    # check outdir
    check_outdir(outfile)

    # make offdiagonals
    offdiagonals = [np.diag(regional_obs, k=i)
                    for i in range(len(regional_obs))]

    # compute sample variance
    sample_variances = np.asarray([np.nanvar(offdiagonal, ddof=1)
                                   for offdiagonal in offdiagonals])
    log_sample_variances = np.log(sample_variances + 1)

    # get predicted variances
    pred_variances = np.array([frozen_dists[exp_value].stats(moments='v')
                               for exp_value in regional_exp[:, 0]])
    log_pred_variances = np.log(pred_variances + 1)

    # prepare x values
    xvals = range(len(offdiagonals))

    # plot
    plt.clf()
    plt.scatter(xvals, log_sample_variances, label='sample variance', c='b')
    plt.plot(xvals, log_pred_variances, label='predicted variance', c='r')
    plt.xlabel('Distance (bins)')
    plt.ylabel('Variance (log scale)')
    plt.title('Variance estimate for %s region' % region)
    plt.legend()
    plt.savefig(outfile, bbox_inches='tight')
