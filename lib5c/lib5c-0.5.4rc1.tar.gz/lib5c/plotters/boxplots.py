"""
Module for plotting locus boxplots that show the distribution of 5C counts at
each locus across a region.
"""

import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

from lib5c.util.parallelization import parallelize_regions
from lib5c.util.plotting import plotter


@parallelize_regions
@plotter
def plot_regional_locus_boxplot(regional_counts, color='darkgray',
                                median_color='firebrick', median_linewidth=5.0,
                                logged=True, sort=True, figsize=None,
                                scaling_factor=0.05, dpi=300, despine=False,
                                **kwargs):
    """
    Plots a locus boxplot visualization showing the distribution of 5C counts at
    each locus across a region.

    Parameters
    ----------
    regional_counts : np.ndarray
        The matrix of counts for this region.
    color : str
        Color to fill the boxplots.
    median_color : str
        Color to mark the medians of the boxplots with.
    median_linewidth : str
        Linewidth to draw the medians of the boxplots with.
    logged : bool
        Pass True to use a log-scale counts axis.
    sort : bool
        Pass True to sort the boxplots from left to right in order of increasing
        median value.
    figsize : Optional[Tuple[float, float]]
        Pass a tuple of the form ``(width, height)`` to force the size of the
        figure. If this kwarg is not passed, the figure size will be determined
        automatically as ``scaling_factor`` times the number of loci in the
        region.
    scaling_factor : float
        If ``figsize`` is not passed, the figure size will be determined
        automatically as ``scaling_factor`` times the number of loci in the
        region.
    dpi : int
        DPI to save figure at if auto-saving to a raster format.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    # honor median_color
    medianprops = {'color': median_color, 'linewidth': median_linewidth}

    # honor logged
    if logged:
        regional_counts = np.log2(regional_counts)

    # honor sort
    if sort:
        regional_counts = regional_counts[
            np.nanmedian(regional_counts, axis=1).argsort()].T

    # default figsize
    if figsize is None:
        width = scaling_factor * len(regional_counts)
        figsize = (width, 0.75 * width)

    # plot
    with sns.plotting_context(context='paper'), sns.axes_style('white'):
        plt.gcf().set_size_inches(figsize)
        sns.boxplot(data=regional_counts, color=color, medianprops=medianprops)

        # clear xticks
        plt.gca().get_xaxis().set_ticks([])
