"""
Module for plotting visualizations of the results of principle component
analyses.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from lib5c.util.plotting import plotter


@plotter
def plot_pca(proj, pcs=(0, 1), legend=True, s=100, label_points=True,
             labels=None, levels=None, colors=None, hue_order=None, **kwargs):
    """
    Plots a PCA projection along two selected principal components.

    Parameters
    ----------
    proj : np.ndarray
        The matrix of PCA-projected replicates.
    pcs : Tuple[int]
        Which two (zero-indexed) principle components should be plotted.
    legend : bool
        Pass True to include a legend.
    s : float
        The area of the points to plot on the scatterplot.
    label_points : bool
        Pass True to annotate each point with its label.
    labels : Optional[List[str]]
        String names identifying the replicates (the rows of ``proj``). Pass
        None to simply label them with their row index within ``proj``.
    levels : Optional[Union[List[str], Dict[str, str]]]
        The "level" for each replicate. Can be passed as a list of string
        (matching the order of the rows of ``proj``), or a dict mapping the
        labels to levels. Each "level" gets one color and one entry in the
        legend. If None is passed each replicate gets its own level
        (``levels = labels``).
    colors : Optional[Dict[str, str]]
        Mapping from levels as strings to the color to use for that level. Pass
        None to use randomly assigned colors.
    hue_order : Optional[List[str]]
        Pass a list of the level names to determine their order in the legend.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    # resolve labels
    if labels is None:
        labels = [str(i) for i in range(len(proj))]

    # resolve levels
    if levels is None:
        levels = labels
    elif type(levels) == dict:
        levels = [levels[label] for label in labels]

    # resolve colors
    if colors is None:
        unique_levels = list(set(levels))
        palette = sns.color_palette('husl', len(unique_levels))
        colors = {unique_levels[i]: palette[i]
                  for i in range(len(unique_levels))}

    # plot, keeping track of the handles we encouter
    handles = [plt.scatter(proj[i, pcs[0]], proj[i, pcs[1]],
                           c=colors[levels[i]], s=s)
               for i in range(len(proj))]

    # add legend
    if legend:
        legend_labels = list(set(levels)) if hue_order is None else hue_order
        legend_handles = [handles[levels.index(l)] for l in legend_labels]
        plt.legend(legend_handles, legend_labels, scatterpoints=1,
                   loc='upper left', bbox_to_anchor=(1, 1.05))

    # add labels to points
    if label_points:
        for i in range(len(proj)):
            plt.annotate(labels[i], (proj[i, pcs[0]], proj[i, pcs[1]]))

    # add labels to axes
    plt.xlabel('PC %i' % (pcs[0] + 1))
    plt.ylabel('PC %i' % (pcs[1] + 1))


def _annotate(x, y, **kwargs):
    for i in range(len(x)):
        plt.text(x[i], y[i], x.index[i])


@plotter
def plot_multi_pca(proj, pcs=3, s=100, label_points=True, labels=None,
                   levels=None, colors=None, hue_order=None, **kwargs):
    """
    Create a multi-component grid of PCA plots.

    Parameters
    ----------
    proj : np.ndarray
        The matrix of PCA-projected replicates.
    pcs : int
        How many principle components should be plotted.
    s : float
        The area of the points to plot on the scatterplot.
    label_points : bool
        Pass True to annotate each point with its label.
    labels : Optional[List[str]]
        String names identifying the replicates (the rows of ``proj``). Pass
        None to simply label them with their row index within ``proj``.
    levels : Optional[Union[List[str], Dict[str, str]]]
        The "level" for each replicate. Can be passed as a list of string
        (matching the order of the rows of ``proj``), or a dict mapping the
        labels to levels. Each "level" gets one color and one entry in the
        legend. If None is passed each replicate gets its own level
        (``levels = labels``).
    colors : Optional[Dict[str, str]]
        Mapping from levels as strings to the color to use for that level. Pass
        None to use randomly assigned colors.
    hue_order : Optional[List[str]]
        Pass a list of the level names to determine their order in the legend.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.

    Notes
    -----
    If both ``log`` and ``scaled`` are True, the logarithm will be applied
    before scaling.

    PCA will always mean-center the data.
    """
    # resolve labels
    if labels is None:
        labels = [str(i) for i in range(len(proj))]

    # resolve levels
    if levels is None:
        levels = labels
    elif type(levels) == dict:
        levels = [levels[label] for label in labels]

    # resolve colors
    if colors is None:
        unique_levels = list(set(levels))
        palette = sns.color_palette('husl', len(unique_levels))
        colors = {unique_levels[i]: palette[i]
                  for i in range(len(unique_levels))}

    # make dataframe
    df = pd.DataFrame(proj, index=labels,
                      columns=['PC%i' % (i + 1) for i in range(proj.shape[1])])
    df['level'] = levels

    # plot
    g = sns.pairplot(df, hue='level', plot_kws=dict(s=s), palette=colors,
                     vars=['PC%i' % (i + 1) for i in range(pcs)],
                     hue_order=hue_order)
    if labels and label_points:
        g.map_upper(_annotate)
