"""
Module for plotting scatterplots of x-y graphs.
"""

import matplotlib.pyplot as plt

from lib5c.util.plotting import plotter, compute_hexbin_extent


@plotter
def scatter(x, y, logx=True, logy=True, hexbin=True, xlim=None, ylim=None,
            **kwargs):
    """
    Plots a scatterplot of data, either as a scatterplot or a hexbin plot.

    Parameters
    ----------
    x, y : np.ndarray
        The data points.
    logx, logy : bool
        Log the x- and/or y-axis.
    hexbin : bool
        Pass True to plot a hexbin plot instead of a scatterplot.
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
