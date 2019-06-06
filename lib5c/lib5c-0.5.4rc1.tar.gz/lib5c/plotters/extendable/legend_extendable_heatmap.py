"""
Module for the LegendExtendableHeatmap class, which adds functionality for
adding a legend to the extendable heatmap system.
"""

from lib5c.plotters.extendable import BaseExtendableHeatmap

import matplotlib as mpl


class LegendExtendableHeatmap(BaseExtendableHeatmap):
    """
    ExtendableHeatmap mixin class providing functionality for adding a legend.
    """
    def add_legend(self, colors, **kwargs):
        """
        Adds a legend to the ExtendableHeatmap.

        Parameters
        ----------
        colors : dict
            The entries to add to the legend. Keys should be string labels to
            use in the legend, and values should be matplotlib colors.
        kwargs : kwargs
            Will be passed through to ``ax.legend()``.

        Returns
        -------
        matplotlib.legend.Legend
            The newly created Legend.
        """
        legend_kwargs = {
            'loc': 'upper right',
            'bbox_to_anchor': (-0.1, -0.1),
            'borderaxespad': 0.,
            'fontsize': 5
        }
        legend_kwargs.update(kwargs)
        patches = [mpl.patches.Patch(color=colors[label], label=label)
                   for label in sorted(colors.keys())]
        return self['root'].legend(handles=patches, **legend_kwargs)
