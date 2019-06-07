"""
Module for plotting curves fitted to x-y graphs.
"""

import numpy as np
import matplotlib.pyplot as plt

from lib5c.util.plotting import plotter, compute_hexbin_extent


@plotter
def plot_fit(x, y, fit, n_points=None, logx=True, logy=True, hexbin=True,
             colors=None, linewidth=4, xlim=None, ylim=None, **kwargs):
    """
    Plots a fit over data.

    Parameters
    ----------
    x, y : np.ndarray
        The data points.
    fit : function or np.ndarray or dict
        If a function is passed, it should return an estimate of y as a function
        of x. If an ``np.ndarray`` is passed, it should be parallel to ``x`` and
        should contain the estimate of y for each x value. Pass a dict of
        functions or ``np.ndarray`` to plot multiple estimates.
    n_points : int, optional
        Pass an integer to subsample ``x`` with this many points when drawing
        the curve. Pass None to draw the curve using all values in ``x``.
    logx, logy : bool
        Log the x- and/or y-axis.
    hexbin : bool
        Pass True to plot a hexbin plot instead of a scatterplot.
    colors : dict
        If ``fit`` is a dict, pass a dict mapping the keys of ``fit`` to valid
        matplotlib colors to force the colors of the curves.
    linewidth : float
        Line width to draw the fit with.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.

    Notes
    -----
    If both xlim and ylim are passed as kwargs and hexbin=True, this function
    will attempt to set the extent of the hexbin plot using the xlim and ylim.
    """
    assert np.all(np.isfinite(x))
    assert np.all(np.isfinite(y))
    sort_idx = np.argsort(x)
    if n_points is not None:
        curve_idx = np.floor(np.linspace(0, len(x)-1, n_points)).astype(int)
    else:
        curve_idx = np.arange(len(x))
    if hexbin:
        extent = compute_hexbin_extent(xlim, ylim, logx, logy)
        plt.hexbin(x, y, xscale='log' if logx else None,
                   yscale='log' if logy else None, bins='log', cmap='Blues',
                   linewidths=0.1, extent=extent)
    else:
        if logx:
            plt.gca().set_xscale('log')
        if logy:
            plt.gca().set_yscale('log')
        plt.scatter(x, y)
    curve_x = x[sort_idx][curve_idx]
    if hasattr(fit, 'keys'):
        for k in fit:
            if callable(fit[k]):
                plt.plot(curve_x, fit[k](curve_x), label=k, lw=linewidth,
                         color=colors[k] if colors else None)
            else:
                plt.plot(curve_x, fit[k][sort_idx][curve_idx], label=k,
                         lw=linewidth, color=colors[k] if colors else None)
        plt.legend()
    else:
        if callable(fit):
            plt.plot(curve_x, fit(curve_x), color='r', lw=linewidth)
        else:
            plt.plot(curve_x, fit[sort_idx][curve_idx], color='r', lw=linewidth)
