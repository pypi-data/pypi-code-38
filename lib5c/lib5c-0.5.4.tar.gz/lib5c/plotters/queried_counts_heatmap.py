"""
Module for plotting contact frequency heatmaps for fragment-level 5C data.
"""

import matplotlib.pyplot as plt

from lib5c.util.parallelization import parallelize_regions
from lib5c.util.system import check_outdir


@parallelize_regions
def plot_queried_counts_heatmap(array, outfile, colorscale=(0, 0.98),
                                colorbar=False, cmap=None):
    """
    Plot a fragment-level contact frequency heatmap of only the interactions
    actually queried by the 5C assay.

    Parameters
    ----------
    array : np.ndarray
        The non-symmetric, non-square matrix of queried counts for this region.
    outfile : str
        String reference to the file to write the heatmap to.
    colorscale : Tuple[float]
        The min and the max of the colormap, as a tuple of the form
        ``(min, max)``.
    colorbar : bool
        Pass True to include a colorbar on the plot.
    cmap : Optional[matplotlib.colors.Colormap]
        The colormap to use for the heatmap. If this kwarg is not passed,
        ``pyplot.cm.coolwarm`` will be used as a default.
    """
    # default cmap
    if cmap is None:
        cmap = plt.cm.coolwarm

    # prepare to plot
    plt.clf()
    ax = plt.gca()
    heatmap = ax.imshow(array, interpolation='none',
                        vmin=colorscale[0], vmax=colorscale[1], cmap=cmap,
                        extent=[0, array.shape[1], array.shape[0], 0])
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])

    # resolve colorbar
    if colorbar:
        plt.colorbar(heatmap, ticks=[colorscale[0], colorscale[1]])

    check_outdir(outfile)
    plt.savefig(outfile, bbox_inches='tight', dpi=800)
