"""
Module for plotting counts distributions.
"""

import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import seaborn as sns

from lib5c.util.counts import flatten_counts_to_list, flatten_regional_counts
from lib5c.util.parallelization import parallelize_regions
from lib5c.util.plotting import plotter


@plotter
def plot_global_distributions(counts_superdict, logged=True, drop_zeros=False,
                              shade=True, labels=None, levels=None, colors=None,
                              hue_order=None, **kwargs):
    """
    Plots overlayed global distributions for many replicates from a counts
    superdict.

    Parameters
    ----------
    counts_superdict : counts_superdict
        The data to plot distributions of.
    logged : bool
        Pass True to log the data before plotting.
    drop_zeros : bool
        Pass True to drop zeros from the distributions.
    shade : bool
        Pass True to fill in the area under the distribution curves.
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
    # infer reps
    reps = counts_superdict.keys()

    # resolve labels
    if labels is None:
        labels = {rep: rep for rep in reps}

    # resolve levels
    if levels is None:
        levels = {label: label for label in labels.values()}

    # resolve colors
    if colors is None:
        unique_levels = list(set(levels.values()))
        palette = sns.color_palette('husl', len(unique_levels))
        colors = {unique_levels[i]: palette[i]
                  for i in range(len(unique_levels))}

    # resolve xlabel
    xlabel = 'Counts (log scale)' if logged else 'Counts'

    # prepare counts
    flattened_counts = {rep: flatten_counts_to_list(counts_superdict[rep],
                                                    discard_nan=True)
                        for rep in reps}

    # drop zeros
    if drop_zeros:
        flattened_counts = {
            rep: flattened_counts[rep][flattened_counts[rep] > 0]
            for rep in reps}

    # log
    if logged:
        flattened_counts = {rep: np.log(flattened_counts[rep] + 1)
                            for rep in reps}

    # plot
    for rep in reps:
        sns.kdeplot(
            flattened_counts[rep],
            shade=shade,
            color=colors[levels[labels[rep]]],
            label=labels[rep]
        )
    plt.ylabel('Probability density')
    plt.xlabel(xlabel)

    # add legend
    legend_labels = list(set(levels.values())) if hue_order is None \
        else hue_order
    legend_handles = [mpatches.Patch(color=colors[l]) for l in legend_labels]
    plt.legend(legend_handles, legend_labels, scatterpoints=1, loc='upper left',
               bbox_to_anchor=(1, 1.05))


@plotter
def plot_regional_distribtions(regional_counts_superdict, logged=True,
                               drop_zeros=False, shade=True, labels=None,
                               levels=None, colors=None, hue_order=None,
                               **kwargs):
    """
    Plots overlayed distributions for many replicates from a regional counts
    superdict.

    Parameters
    ----------
    regional_counts_superdict : counts_superdict
        The data to plot distributions of.
    logged : bool
        Pass True to log the data before plotting.
    drop_zeros : bool
        Pass True to drop zeros from the distributions.
    shade : bool
        Pass True to fill in the area under the distribution curves.
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
    # infer reps
    reps = regional_counts_superdict.keys()

    # resolve labels
    if labels is None:
        labels = {rep: rep for rep in reps}

    # resolve levels
    if levels is None:
        levels = {label: label for label in labels.values()}

    # resolve colors
    if colors is None:
        unique_levels = list(set(levels.values()))
        palette = sns.color_palette('husl', len(unique_levels))
        colors = {unique_levels[i]: palette[i]
                  for i in range(len(unique_levels))}

    # resolve xlabel
    xlabel = 'Counts (log scale)' if logged else 'Counts'

    # prepare counts
    flattened_counts = {
        rep: flatten_regional_counts(regional_counts_superdict[rep],
                                     discard_nan=True)
        for rep in reps}

    # drop zeros
    if drop_zeros:
        flattened_counts = {
            rep: flattened_counts[rep][flattened_counts[rep] > 0]
            for rep in reps}

    # log
    if logged:
        flattened_counts = {rep: np.log(flattened_counts[rep] + 1)
                            for rep in reps}

    # plot
    for rep in reps:
        sns.kdeplot(
            flattened_counts[rep],
            shade=shade,
            color=colors[levels[labels[rep]]],
            label=labels[rep]
        )
    plt.legend()
    plt.ylabel('Probability density')
    plt.xlabel(xlabel)

    # add legend
    legend_labels = list(set(levels.values())) if hue_order is None \
        else hue_order
    legend_handles = [mpatches.Patch(color=colors[l]) for l in legend_labels]
    plt.legend(legend_handles, legend_labels, scatterpoints=1, loc='upper left',
               bbox_to_anchor=(1, 1.05))


plot_regional_distribtions_parallel = parallelize_regions(
    plot_regional_distribtions)
