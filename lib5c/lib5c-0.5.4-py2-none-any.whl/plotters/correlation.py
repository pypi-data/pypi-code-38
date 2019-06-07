"""
Module for plotting pairwise correlation matrices.
"""

import matplotlib.pyplot as plt
import seaborn as sns

from lib5c.util.plotting import plotter


@plotter
def plot_correlation_matrix(matrix, label_values=None, cluster=False,
                            cbar=False, cmap='rocket_r', colorscale=None,
                            despine=False, style='dark', **kwargs):
    """
    Plots a pairwise corrrelation matrix as a heatmap.

    Parameters
    ----------
    matrix : np.ndarray
        The pairwise correlation matrix to visualize.
    label_values : Optional[List[str]]
        A list of strings labeling the columns of the matrix. If not passed, no
        labels will be included.
    cluster : bool
        Pass True to perform heirarchical clustering on the rows and columns of
        the matrix.
    cbar : bool
        Pass True to include a colorbar.
    cmap : matplotlib colormap
        Choose the colormap to use in the heatmap.
    colorscale : Optional[Tuple[int]]
        Pass a colorscale to use for the plot.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    # resolve vmin and vmax from colorscale
    if colorscale is not None:
        vmin, vmax = colorscale
    else:
        vmin, vmax = (None, None)

    if len(matrix) > 6:
        plt.figure(figsize=(len(matrix), len(matrix)))
    if cluster:
        cm = sns.clustermap(data=matrix, metric='cosine', square=True,
                            annot=True, xticklabels=label_values, cmap=cmap,
                            yticklabels=label_values, vmin=vmin, vmax=vmax)
        if label_values is not None:
            plt.setp(cm.ax_heatmap.yaxis.get_majorticklabels(), rotation=0)
            plt.setp(cm.ax_heatmap.xaxis.get_majorticklabels(), rotation=45)
            plt.setp(cm.ax_heatmap.xaxis.get_majorticklabels(), ha='right')
    else:
        sns.heatmap(data=matrix, square=True, annot=True,
                    xticklabels=label_values, yticklabels=label_values,
                    cbar=cbar, cmap=cmap, vmin=vmin, vmax=vmax)
        if label_values is not None:
            plt.yticks(rotation=0)
            plt.xticks(rotation=45, ha='right')
