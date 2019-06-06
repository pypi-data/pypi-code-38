"""
Module for plotting distance dependence curves.
"""

import numpy as np
import pandas as pd
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import seaborn as sns

from lib5c.structures.dataset import Dataset
from lib5c.util.parallelization import parallelize_regions
from lib5c.util.plotting import plotter


DEFAULT_BINS = np.arange(0, 620e3, 20e3)


@plotter
def plot_distance_dependence(counts_superdict, primermap, region=None,
                             bins=None, labels=None, levels=None, colors=None,
                             hue_order=None, **kwargs):
    """
    Plots distance dependence curves.

    Parameters
    ----------
    counts_superdict : counts_superdict
        The data to plot curves for.
    primermap : primermap
        The primermap associated with the counts_superdict.
    region : str or None
        Pass None to combine distance dependence information across all regions.
        Pass a region name to plot only that region's distance dependence curve.
    bins : list of numeric
        Bins to use to stratify interactions into distance groups. Should be in
        units of basepairs.
    labels : dict or None
        Pass a dict mapping the keys of counts_superdict to labels for plotting,
        or pass None to use the keys of counts_superdict as the labels.
    levels : dict or None
        Pass a dict mapping labels to levels to color-code the replicates by
        level. Pass None to give each replicate its own level.
    colors : dict or None
        Pass a dict mapping levels to matplotlib colors to decide what color to
        plot each level with. Pass None to automatically choose colors.
    hue_order : list of str or None
        Pass a list of the level names to determine their order in the legend.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    # resolve bins
    if bins is None:
        bins = DEFAULT_BINS

    # resolve labels
    if labels is None:
        labels = {rep: rep for rep in counts_superdict}

    # resolve levels
    if levels is None:
        levels = {label: label for label in labels.values()}

    # resolve colors
    if colors is None:
        unique_levels = list(set(levels.values()))
        palette = sns.color_palette('husl', len(unique_levels))
        colors = {unique_levels[i]: palette[i]
                  for i in range(len(unique_levels))}

    # compute palette (for seaborn functions)
    palette = {label: colors[levels[label]] for label in labels.values()}

    # make a Dataset
    d = Dataset.from_counts_superdict(counts_superdict, primermap)

    # slice region if appropriate
    if region is not None:
        d.df = d.df[d.df['region'] == region]

    # stratify on distance
    d.df['distance_stratum'] = pd.cut(d.df['distance'], bins)

    # reshape dataframe (stack replicates)
    stacked = pd.DataFrame(d.df['counts'].stack(), columns=['counts'])
    joined = stacked.join(d.df['distance_stratum'])
    joined.index.set_names('rep', level=1, inplace=True)
    joined.reset_index(inplace=True)

    # log counts
    joined['log_counts'] = np.log(joined['counts'] + 1)

    # honor labels and levels
    joined['rep'].replace(labels, inplace=True)

    # plot
    sns.pointplot(x='distance_stratum', y='log_counts', hue='rep',
                  data=joined, ci=None, palette=palette, hue_order=hue_order)
    plt.xticks([-0.5, len(bins) - 1.5], [0, int(bins[len(bins) - 1] / 1e3)])
    plt.xlabel('interaction distance (kb)')
    plt.ylabel('mean interaction frequency (log scale)')

    # add legend
    legend_labels = list(set(levels.values())) if hue_order is None \
        else hue_order
    legend_handles = [mlines.Line2D([], [], color=colors[l], marker='.',
                                    markersize=15)
                      for l in legend_labels]
    plt.legend(legend_handles, legend_labels, bbox_to_anchor=(1.05, 1), loc=2,
               borderaxespad=0.)


plot_distance_dependence_parallel = parallelize_regions(
    plot_distance_dependence)
