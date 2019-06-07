"""
Module for plotting bar charts illustrating motif convergency quantification
results computed using the ``lib5c.algorithms.convergency`` module.
"""

import matplotlib.pyplot as plt
import seaborn as sns

from lib5c.util.plotting import plotter


@plotter
def plot_convergency(convergency_results, **kwargs):
    """
    Plots a convergency bar plot.

    Parameters
    ----------
    convergency_results : dict
        Return value of ``lib5c.algorithms.convergency.compute_convergency()``.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    type_order = ['+-', '-+', '++', '--']
    sns.barplot(
        x=type_order,
        y=[convergency_results[t]['foldchange'] for t in type_order],
        color='k'
    )
    plt.axhline(1, linestyle='--', color='#666666', linewidth=3.0)
