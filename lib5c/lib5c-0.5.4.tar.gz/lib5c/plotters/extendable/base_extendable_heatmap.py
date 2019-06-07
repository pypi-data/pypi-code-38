"""
Module for the BaseExtendableHeatmap class, which provides the basic
functionality of the extendable heatmap plotter.
"""

from __future__ import division

import numpy as np
from matplotlib import colors
import seaborn as sns

from lib5c.plotters.colormaps import get_colormap
from lib5c.plotters.extendable import ExtendableFigure


class BaseExtendableHeatmap(ExtendableFigure):
    """
    Minimal implementation of an ExtendableFigure organized around a contact
    frequency heatmap.

    The heatmap is plotted using ``plt.imshow()`` using data from the ``array``
    attribute, colored using the other attributes, and the resulting axis is
    accessible at ``h['root']`` where ``h`` is the ExtendableHeatmap instance.

    New axes can be added to the margins of the heatmap by calling
    ``add_margin_ax()``. The axis of the new axis that is parallel to the
    heatmap will have its limits set to match the ``grange_x`` or ``grange_y``
    attributes. This allows plotting features on the margin axes using genomic
    coordinates instead of having to convert to pixel coordinates.

    The root heatmap axis is still kept in units of pixels. To make drawing on
    this axis easier, this class provides ``transform_feature()``, which will
    transform a genomic feature dict into heatmap pixel units.

    Attributes
    ----------
    array : np.ndarray
        Array of values to plot in the heatmap. Must be square.
    grange_x : dict
        The genomic range represented by the x-axis of this heatmap. The dict
        should have the form::

            {
                'chrom': str,
                'start': int,
                'end': int
            }

    grange_y : dict, optional
        The genomic range represented by the y-axis of this heatmap. If None,
        the heatmap is assumed to be symmetric.
    colorscale : tuple of float
        The (min, max) of the color range to plot the values in the array with.
    colormap : str or matplotlib colormap or dict of colors
        The colormap to use when drawing the heatmap. Strings will be passed to
        `lib5c.plotters.colormaps.get_colormap()`. If `array` contains strings,
        pass a dict mapping those strings to colors.
    norm : matplotlib.colors.Normalize, optional
        Pass an instance of ``matplotlib.colors.Normalize`` to apply this
        normalization to the heatmap and colorbar.
    """
    def __init__(self, array, grange_x, grange_y=None, colorscale=None,
                 colormap='obs', norm=None):
        super(BaseExtendableHeatmap, self).__init__()
        self.grange_x = grange_x
        self.grange_y = grange_y if grange_y is not None else grange_x
        self.categorical = str(array.dtype).startswith('|S')
        if self.categorical:
            keys = list(sorted(np.unique(array)))
            if colormap is None or type(colormap) == str:
                keys = list(sorted(set(keys) - {'', 'background'}))
                colormap = dict(zip(keys, sns.color_palette("husl", len(keys))))
                colormap[''] = '#333333'
                colormap['background'] = '#333333'
            else:
                for key in keys:
                    if key not in colormap:
                        colormap[key] = '#333333'
            self.cmap = colors.ListedColormap(
                [colormap[k] for k in sorted(colormap.keys())])
            self.color_keys = list(sorted(colormap.keys()))
            for k in self.color_keys:
                array = np.copy(array)
                array[array == k] = self.color_keys.index(k)
            array = array.astype(int)
            self.vmin = 0
            self.vmax = len(self.color_keys) - 1
        else:
            if colorscale is None:
                colorscale = (np.nanmin(array), np.nanmax(array))
            self.vmin = colorscale[0]
            self.vmax = colorscale[1]
            self.cmap = get_colormap(colormap) if type(colormap) == str \
                else colormap
            self.color_keys = None
        self.array = array
        self.im = self['root'].imshow(
            self.array, interpolation='none', vmin=self.vmin, vmax=self.vmax,
            cmap=self.cmap, extent=[0, len(array), len(array), 0], norm=norm)
        self.colorbar = None
        self['root'].autoscale(False)
        self['root'].get_xaxis().set_ticks([])
        self['root'].get_yaxis().set_ticks([])

    def add_colorbar(self, loc='right', size='10%', pad=0.1,
                     new_ax_name='colorbar'):
        """
        Adds a colorbar to the heatmap in a new axis.

        Parameters
        ----------
        loc : {'top', 'bottom', 'left', 'right'}
            Which side of the heatmap to add the new colorbar to.
        size : str
            The size of the new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad : float
            The padding to use between the existing parts of the figure and the
            newly added axis.
        new_ax_name : str
            A name for the new axis. The axis will be accessible as
            ``h[new_ax_name]`` where ``h`` is this ExtendableHeatmap instance.

        Returns
        -------
        pyplot colorbar
            The newly added colorbar.
        """
        self.add_ax(new_ax_name, loc, size, pad)
        self.colorbar = self.fig.colorbar(self.im, cax=self.axes[new_ax_name])
        if self.categorical:
            n = len(self.color_keys)
            self.colorbar.set_ticks((np.arange(n) + 0.5) * (n - 1) / float(n))
            self.colorbar.set_ticklabels(self.color_keys)
        return self.colorbar

    def add_margin_ax(self, loc='bottom', size='10%', pad=0.0,
                      new_ax_name='new_h_axis', axis_limits=(0, 1)):
        """
        Adds a new axis to the margin of this ExtendableHeatmap.

        Parameters
        ----------
        loc : {'top', 'bottom', 'left', 'right'}
            Which side of the figure to add the new axis to.
        size : str
            The size of the new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad : float
            The padding to use between the existing parts of the figure and the
            newly added axis.
        new_ax_name : str
            A name for the new axis. The axis will be accessible as
            ``h[new_ax_name]`` where ``h`` is this ExtendableHeatmap instance.

        Returns
        -------
        pyplot axis
            The newly added axis.
        """
        # create new axis
        ax = self.add_ax(new_ax_name, loc, size, pad)

        # force limits
        if loc in ['bottom', 'top']:
            ax.set_xlim([self.grange_x['start'], self.grange_x['end']])
            if axis_limits is not None:
                ax.set_ylim(axis_limits)
        else:
            ax.set_ylim([self.grange_y['end'], self.grange_y['start']])
            if axis_limits is not None:
                ax.set_xlim(axis_limits)

        # clean ticks or disable axis
        # ax.get_xaxis().set_ticks([])
        # ax.get_yaxis().set_ticks([])
        ax.axis('off')

        return ax

    def transform_coord(self, coord, axis='x'):
        """
        Convenience function for transforming genomic coordinates to heatmap
        pixel coordinates along a specified axis.

        Parameters
        ----------
        coord : int
            The genomic coordinate in base pairs.
        axis : {'x', 'y'}
            The axis to convert the coordinate for.

        Returns
        -------
        float
            The ``coord`` expressed in heatmap pixel coordinates along the
            requested axis.
        """
        grange = self.grange_x if axis == 'x' else self.grange_y
        return ((coord - grange['start'])
                * (len(self.array) / float(grange['end'] - grange['start'])))

    def transform_feature(self, feature, axis='x'):
        """
        Uses ``transform_coord()`` to transform an entire genomic feature dict
        to heatmap pixel coordinates.

        Parameters
        ----------
        feature : dict
            Represents a genomic feature. Should have 'chrom', 'start', and
            'end' keys. The values for 'start' and 'end' should be in base pair
            units.
        axis : {'x', 'y'}
            The axis to convert the feature for.

        Returns
        -------
        dict
            Will have keys 'chrom', 'start', and 'end', but the values for
            'start' and 'end' will now be in units of heatmap pixels along the
            specified axis.
        """
        return {
            'chrom': feature['chrom'],
            'start': self.transform_coord(feature['start'], axis=axis),
            'end'  : self.transform_coord(feature['end'], axis=axis)
        }
