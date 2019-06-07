"""
Module for plotting visualizations comparing fitted theoretical distributions to
real data.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from lib5c.util.counts import flatten_obs_and_exp
from lib5c.util.donut import make_donut_selector
from lib5c.util.plotting import plotter


@plotter
def plot_fit(data, frozen_dist, legend=True, **kwargs):
    """
    Base function for plotting fits.

    Parameters
    ----------
    data : np.ndarray
        The real data to be compared to the theoretical distribution.
    frozen_dist : scipy.stats.rv_frozen
        The theoretical distribution to be compared to the real data.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    # plot KDE of data
    try:
        sns.kdeplot(data, shade=True, color='r', label='data')
    except ZeroDivisionError:
        # when there isn't any data, the kdeplot fails with a ZeroDivisionError
        # we draw a line at zero from mu-2.5sigma to mu+2.5sigma labeled no data
        mean, variance = frozen_dist.stats(moments='mv')
        xmin = mean - 2.5 * np.sqrt(variance)
        xmax = mean + 2.5 * np.sqrt(variance)
        xvals = np.linspace(xmin, xmax, num=100)
        yvals = np.zeros_like(xvals)
        plt.plot(xvals, yvals, color='r', label='no data')
        plt.fill_between(xvals, 0, yvals, alpha=0.2, edgecolor='r',
                         facecolor='r', linewidth=0)
        plt.xlim([xmin, xmax])

    # get curve for the PDF of the frozen_dist
    xvals = np.linspace(*plt.xlim(), num=100)
    if hasattr(frozen_dist.dist, 'pdf'):
        yvals = frozen_dist.pdf(xvals)
    else:
        xvals = xvals.astype(int)
        yvals = frozen_dist.pmf(xvals)

    # plot and shade frozen_dist PDF curve
    plt.plot(xvals, yvals, color='b', label='fit')
    plt.fill_between(xvals, 0, yvals, alpha=0.2, edgecolor='b',
                     facecolor='b', linewidth=0)

    # force recalculation of limits
    plt.gca().relim()
    plt.gca().autoscale()


def plot_group_fit(obs, exp, i, j, frozen_dist, local=False, p=5, w=15,
                   group_fractional_tolerance=0.1, vst=False, log=False,
                   legend=True, **kwargs):
    """
    Convenience function to select a subset of some data and compare it to a
    frozen distribution via plot_fit().

    Parameters
    ----------
    obs : np.ndarray
        Regional matrix of the observed values.
    exp : np.ndarray
        Regional matrix of the expected values.
    i, j : int
        Row and column indices, respectively, of the target point.
    frozen_dist : scipy.stats.rv_frozen
        The theoretical distribution to be compared to the real data.
    local : bool
        Pass True to compare the theoretical distribution to observed data
        points in a donut window around the target point. Pass False to compare
        the theoretical distribution to observed data points with similar
        expected values to the target point.
    w : int
        The outer radius of the donut window to use when local=True.
    p : int
        The inner radius of the donut window to use when local=True.
    group_fractional_tolerance : float
        The fractional tolerance in expected value used to select points with
        "similar" expected values when local=False.
    vst : bool
        Pass True if a VST-style step has been performed upstream and the
        expected values should be interpreted as already logged.
    log : bool
        Pass True to log the selected observed data points before plotting.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    target_exp = exp[i, j]
    if local:
        idx = make_donut_selector(i, j, p, w, len(obs))
        obs = obs[idx]
        exp = exp[idx]
        if vst:
            data = obs + target_exp - exp
        else:
            data = obs * target_exp / exp
    else:
        obs, exp = flatten_obs_and_exp(obs, exp)
        if vst:
            target_exp = np.exp(target_exp) - 1
            exp = np.exp(exp) - 1
        data = obs[
            np.abs(target_exp - exp) / target_exp < group_fractional_tolerance]
    if log:
        data = np.log(data + 1)
    return plot_fit(data, frozen_dist, legend=legend, **kwargs)
