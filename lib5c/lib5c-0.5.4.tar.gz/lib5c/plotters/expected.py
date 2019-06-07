"""
Module for visualization of one-dimensional distance-dependent expected models.

Two convenience functions are exposed:

* ``plot_bin_expected()``
* ``plot_fragment_expected()``

which are bin- and fragment-level wrappers around ``plot_log_log_expected()``.
The other functions are utility functions.

These functions are all overloaded so that an arg called ``distance_expected``
can be replaced with a dict of named distance expecteds. This will result in an
overlayed comparison of all the expected models in the dict.

The other functions in this module are private helper functions.
"""

from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np

from lib5c.util.parallelization import parallelize_regions
from lib5c.util.plotting import plotter


@parallelize_regions
def plot_bin_expected(obs_matrix, distance_expected, hexbin=False, kde=False,
                      color='r', semilog=False, linewidth=4,
                      title='1-D expected model', ylabel='log counts',
                      xlabel='log distance', legend=True, **kwargs):
    """
    Convenience function for plotting a visualization of a one-dimensional
    distance-dependent expected model defined over bin-level data.

    Parameters
    ----------
    obs_matrix : np.ndarray
        The matrix of real interaction data that the model will be compared to.
    distance_expected : List[float]
        The one-dimensional distance-dependence model. The ``i`` th element of
        the list should correspond to the expected value for interactions
        between loci separated by ``i`` bins. To compare multiple expected
        models to the same observed data, pass a dict or an OrderedDict whose
        keys are string names for the models.
    hexbin : bool
        Pass True to use a hexbin plot to represent the density of the real
        data.
    kde : bool
        Pass True to use a kernel density estimate to represent the density of
        the real data.
    color : str
        The color to draw the expected model line with. When comparing multiple
        models, this can be a dict or OrderedDict with the same keys as
        ``distance_expected``.
    semilog : bool
        Pass True to leave the distance axis unlogged.
    linewidth : float
        Line width to draw the model with.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    real_data = np.asarray(
        [[i - j, obs_matrix[i, j]]
         for i in range(len(obs_matrix))
         for j in range(i + 1)
         if np.isfinite(obs_matrix[i, j])]
    )
    exp_distances, exp_values = _bin_distance_expected_to_arrays(
        distance_expected)
    return plot_log_log_expected(
        real_data[:, 0],
        real_data[:, 1],
        exp_distances,
        exp_values,
        hexbin=hexbin, kde=kde, color=color, semilog=semilog,
        linewidth=linewidth, title=title, ylabel=ylabel, xlabel=xlabel,
        legend=legend, **kwargs)


@parallelize_regions
def plot_fragment_expected(obs_matrix, distance_expected, distance_matrix,
                           hexbin=False, kde=False, color='r', semilog=False,
                           linewidth=4, title='1-D expected model',
                           ylabel='log counts', xlabel='log distance',
                           legend=True, **kwargs):
    """
    Convenience function for plotting a visualization of a one-dimensional
    distance-dependent expected model defined over fragment-level data.

    Parameters
    ----------
    obs_matrix : np.ndarray
        The matrix of real interaction data that the model will be compared to.
    distance_expected : Dict[int, float]
        A mapping from interaction distances in units of base pairs to the
        expected value at that distance. To compare multiple expected models to
        the same observed data, pass a dict or an OrderedDict whose keys are
        string names for the models.
    distance_matrix : np.ndarray
        The pairwise distance matrix for the fragments in this region.
    hexbin : bool
        Pass True to use a hexbin plot to represent the density of the real
        data.
    kde : bool
        Pass True to use a kernel density estimate to represent the density of
        the real data.
    color : str
        The color to draw the expected model line with. When comparing multiple
        models, this can be a dict or OrderedDict with the same keys as
        ``distance_expected``.
    semilog : bool
        Pass True to leave the distance axis unlogged.
    linewidth : float
        Line width to draw the model with.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    real_data = np.asarray(
        [[distance_matrix[i, j], obs_matrix[i, j]]
         for i in range(len(obs_matrix))
         for j in range(i + 1)
         if np.isfinite(obs_matrix[i, j])]
    )
    exp_distances, exp_values = _fragment_distance_expected_to_arrays(
        distance_expected)
    return plot_log_log_expected(
        real_data[:, 0],
        real_data[:, 1],
        exp_distances,
        exp_values,
        hexbin=hexbin, kde=kde, color=color, semilog=semilog,
        linewidth=linewidth, title=title, ylabel=ylabel, xlabel=xlabel,
        legend=legend, **kwargs)


def _bin_distance_expected_to_arrays(distance_expected):
    if isinstance(distance_expected, dict):
        exp_distances = np.arange(
            len(distance_expected[distance_expected.keys()[0]]))
        exp_values = OrderedDict([(model, np.array(distance_expected[model]))
                                  for model in distance_expected])
    else:
        exp_distances = np.arange(len(distance_expected))
        exp_values = np.array(distance_expected)
    return exp_distances, exp_values


def _fragment_distance_expected_to_arrays(distance_expected):
    if isinstance(distance_expected[distance_expected.keys()[0]], dict):
        exp_distances = np.array(
            distance_expected[distance_expected.keys()[0]].keys())
        exp_values = OrderedDict([(model,
                                   np.array(distance_expected[model].values())
                                   [exp_distances.argsort()])
                                  for model in distance_expected])
    else:
        exp_distances = np.array(distance_expected.keys())
        exp_values = np.array(
            distance_expected.values())[exp_distances.argsort()]
    exp_distances.sort()
    return exp_distances, exp_values


@plotter
def plot_log_log_expected(obs_distances, obs_values, exp_distances, exp_values,
                          hexbin=False, kde=False, color='r', pseudocount=1,
                          semilog=False, linewidth=4,
                          title='1-D expected model', ylabel='log counts',
                          xlabel='log distance', legend=True, **kwargs):
    """
    Plot a visualization of an expected model over real data.

    Parameters
    ----------
    obs_distances : np.ndarray
        Flat array of the distances of the ``obs_values``.
    obs_values : np.ndarray
        Flat array of the real data values.
    exp_distances : np.ndarray
        Flat array of the distances of the ``exp_values``.
    exp_values : np.ndarray
        Flat array of the expected data values predicted by the model. To
        compare multiple expected models to the same observed data, pass a dict
        or an OrderedDict whose keys are string names for the models.
    title : str
        Title to write on the plot.
    ylabel : str
        Label for the y-axis on the plot.
    xlabel : str
        Label for the x-axis on the plot.
    hexbin : bool
        Pass True to use a hexbin plot to represent the density of the real
        data.
    kde : bool
        Pass True to use a kernel density estimate to represent the density of
        the real data.
    color : str
        The color to draw the expected model line with. When comparing multiple
        models, this can be a dict or OrderedDict with the same keys as
        ``distance_expected``.
    pseudocount : int
        Pseudocount to add to distances if called with ``semilog=True``.
    semilog : bool
        Pass True to leave the distance axis unlogged.
    linewidth : float
        Line width to draw the model with.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    if not semilog:
        obs_distances = np.log(obs_distances + pseudocount)
        exp_distances = np.log(exp_distances + pseudocount)
    obs_values = np.log(obs_values + pseudocount)
    if isinstance(exp_values, dict):
        exp_values = OrderedDict([(model,
                                   np.log(exp_values[model] + pseudocount))
                                  for model in exp_values])
    else:
        exp_values = np.log(exp_values + pseudocount)
    if kde:
        import seaborn as sns
        sns.kdeplot(obs_distances, obs_values, cmap='Blues', shade=True,
                    shade_lowest=False, n_levels=30)
    elif hexbin:
        from seaborn.distributions import _freedman_diaconis_bins
        x_bins = _freedman_diaconis_bins(obs_distances)
        y_bins = _freedman_diaconis_bins(obs_values)
        gridsize = int(np.mean([x_bins, y_bins]))
        plt.hexbin(obs_distances, obs_values, cmap='Blues', bins='log',
                   gridsize=gridsize, label='real data')
        xlim = plt.xlim()
        ylim = plt.ylim()
    else:
        plt.scatter(obs_distances, obs_values, label='real data')
    if isinstance(exp_values, dict):
        if isinstance(color, dict):
            for model in exp_values:
                plt.plot(exp_distances[exp_values[model] >= 0],
                         exp_values[model][exp_values[model] >= 0],
                         c=color[model],
                         lw=linewidth,
                         label=model)
        else:
            ax = plt.gca()
            ax.set_prop_cycle(
                'color',
                plt.get_cmap('Set1')(np.linspace(0, 1,
                                                 max(len(exp_values), 8))))
            for model in exp_values:
                plt.plot(exp_distances[exp_values[model] >= 0],
                         exp_values[model][exp_values[model] >= 0],
                         lw=linewidth,
                         label=model)
    else:
        plt.plot(exp_distances, exp_values, c=color, lw=linewidth,
                 label='model')
    if hexbin:
        plt.xlim(xlim)
        plt.ylim(ylim)

    # unbelievable hack to dodge a strange ValueError on legend creation
    handles, _ = plt.gca().get_legend_handles_labels()
    if hasattr(handles[-1], '_original_edgecolor'):
        handles[-1]._original_edgecolor = None
