"""
Module for visualizing distributions overlayed over real 5C data.

The base function for plotting fits is :func:`plot_fit`, but several convenience
functions are provided to help set up plotting distributions set up using
different fitting modes.

If you haven't actually fitted distributions yet, call :func:`fit_and_plot`.

If you have already fitted 'obs_over_exp' or 'log_log_fit' mode distributions,
call :func:`plot_partial_fit` (to draw one fit) or :func:`plot_partial_fit` (to
draw fits for multiple expected values in one call).

If you have already fitted a 'regional_simple' mode distribution, call
:func:`plot_regional_simple_fit`.

If you have already fitted 'regional_shifted' mode distributions, call
:func:`plot_regional_shifted_fit` or :func:`plot_regional_shifted_fits`.
"""

import os

import numpy as np

from lib5c.util.counts import flatten_regional_counts
from lib5c.util.parallelization import parallelize_regions
from lib5c.algorithms.distributions_legacy.fitting import fit_distributions
from lib5c.plotters.fits import plot_fit


@parallelize_regions
def fit_and_plot(outfile, obs_matrix, exp_matrix, region, mode='obs_over_exp',
                 dist='nbinom', log=False, expected_value=None, tol=None):
    """
    Convenience function that fits distributions to an observed counts matrix
    given an expected counts matrix and a modeling strategy, then makes a plot
    showing the fit at one or all expected values.

    Parameters
    ----------
    outfile : str
        String reference to the file to write the plot to. If ``expected_value``
        is None and multiple plots will be drawn for different expected values,
        include a '%%s' in this string, which will be replaced by the expected
        value.
    obs_matrix : np.ndarray
        The matrix of observed counts.
    exp_matrix : np.ndarray
        The matrix of expected counts.
    region : str
        The region name as a string, to be used in the plot title.
    mode : {'obs_over_exp','log_log_fit','regional_simple','regional_shifted'}
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
    expected_value : Optional[float]
        The specific expected value to plot the expected for. If this kwarg is
        not passed, then a separate plot will be generated for every expected
        value. This kwarg doesn't apply when ``mode`` is 'regional_simple'.
    tol : Optional[float]
        Pass a float to allow counts values with expected values within this
        tolerance to be included when showing the distribution of the raw data.
        This kwarg only applies when ``mode`` is 'obs_over_exp' or
        'log_log_fit'.
    """
    frozen_dists = fit_distributions(
        obs_matrix, exp_matrix, mode=mode, dist=dist, log=log,
        expected_value=expected_value)
    plot_fits(outfile, obs_matrix, exp_matrix, frozen_dists, region, mode=mode,
              log=log, tol=tol)


def plot_fits(outfile, regional_obs, regional_exp, frozen_dists, region,
              mode='obs_over_exp', log=False, tol=None):
    """
    Helper function that calls the appropriate fit-drawing function based on the
    ``mode`` kwarg.

    Parameters
    ----------
    outfile : str
        String reference to the file to write the plot to. If ``frozen_dists``
        contains many distributions, include a '%%s' in this string, which will
        be replaced by the expected value that distribution is appropriate for.
    regional_obs : np.ndarray
        The matrix of observed counts.
    regional_exp : np.ndarray
        The matrix of expected counts.
    frozen_dists : Dict[float, scipy.stats.rv_frozen]
        A mapping from expected values to the appropriate frozen distribution to
        plot at that expected value.
    region : str
        The region name as a string, to be used in the plot title.
    mode : {'obs_over_exp','log_log_fit','regional_simple','regional_shifted'}
        The method to use to fit the distributions:
            * obs_over_exp: use quadratic mean-variance relationship estimated
              via sample variance of obs/exp counts across whole region
            * log_log_fit: use quadratic mean-variance relationship estimated
              via fitting quadratic curve in log-mean vs log-variance space
            * regional_simple: fit single distribution to obs/exp across whole
              region
            * regional_shifted: fit distributions by shifting counts from the
              whole region to the appropriate distance scale
    log : bool
        Pass True if the x-axis should represent log-scale counts. Pass this
        when the ``frozen_dists`` were fitted to logged data.
    tol : Optional[float]
        Pass a float to allow counts values with expected values within this
        tolerance to be included when showing the distribution of the raw data.
    """
    if mode == 'regional_simple':
        plot_regional_simple_fit(
            outfile, regional_obs, regional_exp, frozen_dists, region, log=log)
    elif mode == 'regional_shifted':
        plot_regional_shifted_fits(
            outfile, regional_obs, regional_exp, frozen_dists, region, log=log)
    elif mode in ['obs_over_exp', 'log_log_fit']:
        plot_partial_fits(
            outfile, regional_obs, regional_exp, frozen_dists, region, log=log,
            tol=tol)
    else:
        raise ValueError('invalid mode specified')


@parallelize_regions
def plot_regional_simple_fit(outfile, regional_obs, regional_exp, frozen_dist,
                             region, log=False):
    """
    Prepares data and plots a fit given some real data and a 'regional_simple'
    distribution to compare it with.

    Parameters
    ----------
    outfile : str
        String reference to a file to write the plot to.
    regional_obs : np.ndarray
        The matrix of observed counts.
    regional_exp : np.ndarray
        The matrix of expected counts.
    frozen_dist : scipy.stats.rv_frozen
        The theoretical distribution to be compared to the real data.
    region : str
        The region name as a string, to be used in the plot title.
    log : bool
        Pass True if the x-axis should represent log-scale counts. Pass this
        when ``frozen_dist`` was fitted to logged data.
    """
    # define xlabel
    xlabel = 'Observed over expected counts'

    # compute obs/exp
    obs_over_exp = regional_obs / regional_exp

    # log if appropriate
    if log:
        obs_over_exp = np.log(obs_over_exp)
        xlabel = 'Observed over expected counts (log scale)'

    # flatten
    flat_obs_over_exp = np.array(
        flatten_regional_counts(obs_over_exp, discard_nan=True))

    # plot
    plot_fit(outfile, flat_obs_over_exp, frozen_dist, xlabel=xlabel,
             title='Regional simple fit for %s region' % region)


@parallelize_regions
def plot_regional_shifted_fits(outfile_pattern, regional_obs, regional_exp,
                               frozen_dists, region, log=False):
    """
    Wrapper for making multiple calls to ``plot_regional_shifted_fit()`` when we
    want to plot multiple plots at several different expected values.

    Parameters
    ----------
    outfile_pattern : str
        Pattern describing where to write the plots to. '%%e' in the filename
        will be replaced with the expected value the plot is drawn for.
    regional_obs : np.ndarray
        The matrix of observed counts.
    regional_exp : np.ndarray
        The matrix of expected counts.
    frozen_dists : Dict[float, scipy.stats.rv_frozen]
        A mapping from expected values to the appropriate frozen distribution to
        plot at that expected value.
    region : str
        The region name as a string, to be used in the plot title.
    log : bool
        Pass True if the x-axis should represent log-scale counts. Pass this
        when the ``frozen_dists`` were fitted to logged data.
    """
    for exp_value in frozen_dists:
        outfile_head, outfile_tail = os.path.split(outfile_pattern)
        outfile_base, outfile_ext = os.path.splitext(outfile_tail)
        outfile = os.path.join(outfile_head,
                               outfile_base
                               .replace(r'%e', '%g' % exp_value) + outfile_ext)
        plot_regional_shifted_fit(
            outfile, exp_value, regional_obs, regional_exp,
            frozen_dists[exp_value], region, log=log)


def plot_regional_shifted_fit(outfile, exp_value, regional_obs, regional_exp,
                              frozen_dist, region, log=False):
    """
    Prepares data and plots a fit given some real data and a 'regional_shifted'
    distribution to compare it with.

    Parameters
    ----------
    outfile : str
        String reference to a file to write the plot to.
    exp_value : float
        The specific expected value to shift the real data to.
    regional_obs : np.ndarray
        The matrix of observed counts.
    regional_exp : np.ndarray
        The matrix of expected counts.
    frozen_dist : scipy.stats.rv_frozen
        The theoretical distribution to be compared to the real data.
    region : str
        The region name as a string, to be used in the plot title.
    log : bool
        Pass True if the x-axis should represent log-scale counts. Pass this
        when ``frozen_dist`` was fitted to logged data.
    """
    # define xlabel
    xlabel = 'Shifted counts'

    # shift entire region
    shifted_matrix = regional_obs * (exp_value / regional_exp)

    # log if appropriate
    if log:
        shifted_matrix = np.log(shifted_matrix)
        xlabel = 'Shifted counts (log scale)'

    # flatten shifted matrix
    shifted_flattened = np.array(
        flatten_regional_counts(shifted_matrix, discard_nan=True))

    # plot
    plot_fit(outfile, shifted_flattened, frozen_dist, xlabel=xlabel,
             title='Regional shifted fit for %s region at expected %.2f' %
                   (region, exp_value))


@parallelize_regions
def plot_partial_fits(outfile_pattern, regional_obs, regional_exp, frozen_dists,
                      region, log=False, tol=None):
    """
    Wrapper for making multiple calls to ``plot_partial_fit()`` when we want to
    plot multiple plots at several different expected values.

    Parameters
    ----------
    outfile_pattern : str
        Pattern describing where to write the plots to. '%%e' in the filename
        will be replaced with the expected value the plot is drawn for.
    regional_obs : np.ndarray
        The matrix of observed counts.
    regional_exp : np.ndarray
        The matrix of expected counts.
    frozen_dists : Dict[float, scipy.stats.rv_frozen]
        A mapping from expected values to the appropriate frozen distribution to
        plot at that expected value.
    region : str
        The region name as a string, to be used in the plot title.
    log : bool
        Pass True if the x-axis should represent log-scale counts. Pass this
        when the ``frozen_dists`` were fitted to logged data.
    tol : Optional[float]
        Pass a float to allow counts values with expected values within this
        tolerance to be included when showing the distribution of the raw data.
    """
    for exp_value in frozen_dists:
        outfile_head, outfile_tail = os.path.split(outfile_pattern)
        outfile_base, outfile_ext = os.path.splitext(outfile_tail)
        outfile = os.path.join(outfile_head,
                               outfile_base
                               .replace(r'%e', '%g' % exp_value) + outfile_ext)
        plot_partial_fit(
            outfile, exp_value, regional_obs, regional_exp,
            frozen_dists[exp_value], region, log=log, tol=tol)


def plot_partial_fit(outfile, exp_value, regional_obs, regional_exp,
                     frozen_dist, region, log=False, tol=None):
    """
    Prepares data and plots a fit given some real data and a 'obs_over_exp' or
    'log_log_fit' distribution to compare it with.

    Parameters
    ----------
    outfile : str
        String reference to a file to write the plot to.
    exp_value : float
        The specific expected value to shift the real data to.
    regional_obs : np.ndarray
        The matrix of observed counts.
    regional_exp : np.ndarray
        The matrix of expected counts.
    frozen_dist : scipy.stats.rv_frozen
        The theoretical distribution to be compared to the real data.
    region : str
        The region name as a string, to be used in the plot title.
    log : bool
        Pass True if the x-axis should represent log-scale counts. Pass this
        when ``frozen_dist`` was fitted to logged data.
    tol : Optional[float]
        Pass a float to allow counts values with expected values within this
        tolerance to be included when showing the distribution of the raw data.
    """
    # define xlabel
    xlabel = 'Counts'

    # create selection
    flat_obs = np.array(flatten_regional_counts(regional_obs))
    flat_exp = np.array(flatten_regional_counts(regional_exp))
    if tol is not None:
        selection = flat_obs[(np.isfinite(flat_obs)) &
                             (abs(flat_exp - exp_value) <= tol)]
    else:
        selection = flat_obs[(np.isfinite(flat_obs)) & (flat_exp == exp_value)]

    # log if appropriate
    if log:
        selection = np.log(selection)
        xlabel = 'Counts (log scale)'

    # plot
    plot_fit(outfile, selection, frozen_dist, xlabel=xlabel,
             title='Partial fit for %s region at expected %.2f' %
                   (region, exp_value))
