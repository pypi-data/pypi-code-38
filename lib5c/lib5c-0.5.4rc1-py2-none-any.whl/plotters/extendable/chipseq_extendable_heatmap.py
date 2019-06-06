"""
Module for the ChipSeqExtendableHeatmap class, which adds ChIP-seq track
plotting functionality for the extendable heatmap system.
"""

import numpy as np
import matplotlib.collections as collections

from lib5c.plotters.extendable import BaseExtendableHeatmap
from lib5c.util.bed import check_intersect


class ChipSeqExtendableHeatmap(BaseExtendableHeatmap):
    """
    ExtendableHeatmap mixin class providing ChIP-seq track plotting
    functionality.
    """
    def add_chipseq_tracks(self, features, size='10%', pad=0.05,
                           axis_limits=None, linewidth=0.4, name='chipseq',
                           color='k', track_label=None):
        """
        Adds ChIP-seq tracks for a single set of features to both the bottom and
        left side of the heatmap by calling ``add_chipseq_track()`` twice.

        Parameters
        ----------
        features : list of dict
            Each feature should be a dict with at least the following keys::

                {
                    'chrom': str,
                    'start': int,
                    'end': int,
                    'value': float
                }

            Each feature will be drawn as a rectangle on the heatmap from
            'start' to 'end' with height 'value'. If the 'value' key is missing,
            it will be assumed to be one for all features. To get data in this
            form from bigwig files, consult
            ``lib5c.contrib.pybigwig.bigwig.BigWig.query()``.
        size : str
            The size of the new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad : float
            The padding to use between the existing parts of the figure and the
            newly added axis.
        axis_limits : tuple of float, optional
            Axis limits for the 'value' of the plotted features (heights of the
            rectangles) as a (min, max) tuple. Pass None to automatically scale
            the axis limits.
        linewidth : float
            The linewidth to use when drawing the rectangles. Pass smaller
            values for sharper features/peaks.
        name : str
            Base name for the new axis. This name will be prefixed with the
            orientation of the track ('vertical' or 'horizontal').
        color : matplotlib color
            The color to draw the rectangles with.
        track_label : str, optional
            Pass a string to label the track.

        Returns
        -------
        list of pyplot axes
            The newly added ChIP-seq track axes.
        """
        ax_h = self.add_chipseq_track(
            features, loc='bottom', size=size, pad=pad, axis_limits=axis_limits,
            linewidth=linewidth, name=name, color=color,
            track_label=track_label)
        ax_v = self.add_chipseq_track(
            features, loc='left', size=size, pad=pad, axis_limits=axis_limits,
            linewidth=linewidth, name=name, color=color,
            track_label=track_label)
        return [ax_h, ax_v]

    def add_chipseq_track(self, features, loc='bottom', size='10%', pad=0.05,
                          axis_limits=None, linewidth=0.4, name='chipseq',
                          color='k', track_label=None):
        """
        Adds one ChIP-seq track along either the x- or y-axis of the heatmap.

        Parameters
        ----------
        features : list of dict
            Each feature should be a dict with at least the following keys::

                {
                    'chrom': str,
                    'start': int,
                    'end': int,
                    'value': float
                }

            Each feature will be drawn as a rectangle on the heatmap from
            'start' to 'end' with height 'value'. If the 'value' key is missing,
            it will be assumed to be one for all features. To get data in this
            form from bigwig files, consult
            ``lib5c.contrib.pybigwig.bigwig.BigWig.query()``.
        loc : {'top', 'bottom', 'left', 'right'}
            Which side of the heatmap to add the new ChIP-seq track to.
        size : str
            The size of the new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad : float
            The padding to use between the existing parts of the figure and the
            newly added axis.
        axis_limits : tuple of float, optional
            Axis limits for the 'value' of the plotted features (heights of the
            rectangles) as a (min, max) tuple. Pass None to automatically scale
            the axis limits.
        linewidth : float
            The linewidth to use when drawing the rectangles. Pass smaller
            values for sharper features/peaks.
        name : str
            Base name for the new axis. This name will be prefixed with the
            orientation of the track ('vertical or 'horizontal').
        color : matplotlib color
            The color to draw the rectangles with.
        track_label : str, optional
            Pass a string to label the track.

        Returns
        -------
        pyplot axis
            The newly added ChIP-seq track axis.
        """
        # deduce orientation, either h or v, and save the correct grange
        if loc in ['bottom', 'top']:
            orientation = 'horizontal'
            grange = self.grange_x
        else:
            orientation = 'vertical'
            grange = self.grange_y

        # compute track_width , assuming horizontal orientation
        track_width = grange['end'] - grange['start']

        # create the new axis
        ax = self.add_margin_ax(loc=loc, size=size, pad=pad,
                                new_ax_name='%s_%s' % (orientation, name),
                                axis_limits=axis_limits)

        # add value to features if not present
        features = [f if 'value' in f else dict(f, value=1) for f in features]

        # extract positions, widths, and heights for all features
        pwh_tuples = [
            (f['start'], f['end'] - f['start'], f['value'])
            for f in features if check_intersect(f, grange) and f['value'] != 0
            and np.isfinite(f['value'])
        ]
        positions, widths, heights = zip(*pwh_tuples) if pwh_tuples \
            else [[0], [0], [0]]

        # handle track height
        if axis_limits is not None:
            track_height = axis_limits[1]
        else:
            track_height = np.ceil(np.max(heights))
            if orientation == 'vertical':
                ax.set_xlim((0, track_height))
            else:
                ax.set_ylim((0, track_height))

        # prepare rectangle kwargs
        rect_kwargs = {'edgecolors': color, 'facecolors': color,
                       'linewidths': linewidth}

        # plot
        verts = []
        for i in range(len(positions)):
            hverts = [
                (positions[i], 0),
                (positions[i]+widths[i], 0),
                (positions[i]+widths[i], heights[i]),
                (positions[i], heights[i])
            ]
            if orientation == 'horizontal':
                verts.append(hverts)
            else:
                verts.append([(y, x) for x, y in hverts])
        ax.add_collection(collections.PolyCollection(verts, **rect_kwargs))

        # add back only left y axis
        ax.axis('on')
        ax.set_frame_on(False)
        num_ticks = 3
        tick_positions = np.linspace(0, track_height, num_ticks)
        tick_labels = [''] * (num_ticks-1) + [int(track_height)]
        if orientation == 'vertical':
            ax.axes.get_yaxis().set_visible(False)
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, rotation=270, fontsize=7)
            ax.xaxis.set_ticks_position('bottom')
            ax.get_xaxis().set_tick_params(direction='out')
        else:
            ax.axes.get_xaxis().set_visible(False)
            ax.set_yticks(tick_positions)
            ax.set_yticklabels(tick_labels, fontsize=7)
            ax.yaxis.set_ticks_position('left')
            ax.get_yaxis().set_tick_params(direction='out')

        # write name of track
        if track_label:
            name_coords = [grange['start'] + track_width / 80, track_height]
            ha = 'left'
            va = 'top'
            rotation = 0
            if orientation == 'vertical':
                name_coords.reverse()
                ha = 'right'
                rotation = 270
            ax.text(name_coords[0], name_coords[1], track_label, fontsize=7,
                    ha=ha, va=va, rotation=rotation)

        return ax
