"""
This module defines an altered implementation of ``sns.heatmap()`` that allows
the use of asymmetric colorbars.

Since seaborn 0.8.0, this fix is no longer necessary, and ``sns.heatmap()`` now
honors the ``center`` kwarg correctly. This module is only present for legacy
reasons.
"""

import matplotlib.pyplot as plt
from seaborn.matrix import _HeatMapper


class CustomHeatmapper(_HeatMapper):
    def _determine_cmap_params(self, plot_data, vmin, vmax, cmap, center,
                               robust):
        super(CustomHeatmapper, self)._determine_cmap_params(
            plot_data, vmin, vmax, cmap, center, robust)

        # Simple heuristics for whether these data should  have a divergent map
        divergent = ((vmin < 0) and (vmax > 0)) or center is not None

        # Now set center to 0 so math below makes sense
        if center is None:
            center = 0

        # A divergent map should be symmetric around the center value
        if divergent and not (vmin and vmax):
            vlim = max(abs(vmin - center), abs(vmax - center))
            vmin, vmax = -vlim, vlim
        self.divergent = divergent

        # Now add in the centering value and set the limits
        vmin += center
        vmax += center
        self.vmin = vmin
        self.vmax = vmax


def heatmap(data, vmin=None, vmax=None, cmap=None, center=None, robust=False,
            annot=False, fmt=".2g", annot_kws=None, linewidths=0,
            linecolor="white", cbar=True, cbar_kws=None, cbar_ax=None,
            square=False, ax=None, xticklabels=True, yticklabels=True,
            mask=None, **kwargs):
    # Initialize the plotter object
    plotter = CustomHeatmapper(data, vmin, vmax, cmap, center, robust, annot,
                               fmt, annot_kws, cbar, cbar_kws, xticklabels,
                               yticklabels, mask)

    # Add the pcolormesh kwargs here
    kwargs["linewidths"] = linewidths
    kwargs["edgecolor"] = linecolor

    # Draw the plot and return the Axes
    if ax is None:
        ax = plt.gca()
    if square:
        ax.set_aspect("equal")
    plotter.plot(ax, cbar_ax, kwargs)
    return ax
