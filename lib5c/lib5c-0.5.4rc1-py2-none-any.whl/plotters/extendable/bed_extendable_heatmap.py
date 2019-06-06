"""
Module for the BedExtendableHeatmap class, which adds bed track plotting
functionality for the extendable heatmap system.
"""

import matplotlib as mpl

from lib5c.plotters.extendable import BaseExtendableHeatmap
from lib5c.util.bed import check_intersect


class BedExtendableHeatmap(BaseExtendableHeatmap):
    """
    ExtendableHeatmap mixin class providing bed track plotting functionality.
    """
    def add_bed_tracks(self, bed_tracks, size='3%', pad=0.0, axis_limits=(0, 1),
                       intron_height=0.05, name=None, colors=None,
                       track_label=None):
        """
        Adds bed tracks for a single set of bed features to both the bottom and
        left side of the heatmap by calling ``add_bed_track()`` twice.

        Parameters
        ----------
        bed_tracks : list of dict
            Each dict should represent a bed feature and could have the
            following keys::

                {
                    'chrom' : str,
                    'start' : int,
                    'end'   : int,
                    'strand': '+' or '-'
                }

            The 'strand' key is optional and is only used for color-coding bed
            features when ``colors`` is passed.
        size : str
            The size of the new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad : float
            The padding to use between the existing parts of the figure and the
            newly added axis.
        axis_limits : tuple of float
            Axis limits for the non-genomic axis of the bed track.
        intron_height : float
            The height to draw each bed feature with.
        name : str
            Base name for the new axis. This name will be prefixed with the
            orientation of the track ('vertical' or 'horizontal').
        colors : dict, optional
            Map from the value of the 'strand' key in the ``bed_tracks`` dicts
            (usually '+' or '-') to color name for bed features with that strand
            value (i.e., orientation). If not provided for a given strand or if
            the bed feature doesn't have a 'strand' key the color is black by
            default.
        track_label : str, optional
            Pass a string to label the track.

        Returns
        -------
        list of pyplot axes
            The newly added bed track axes.
        """
        ax_h = self.add_bed_track(
            bed_tracks, loc='bottom', size=size, pad=pad, name=name,
            axis_limits=axis_limits, intron_height=intron_height, colors=colors,
            track_label=track_label
        )
        ax_v = self.add_bed_track(
            bed_tracks, loc='left', size=size, pad=pad, name=name,
            axis_limits=axis_limits, intron_height=intron_height, colors=colors,
            track_label=track_label
        )
        return [ax_h, ax_v]

    def add_bed_track(self, bed_tracks, loc='bottom', size='3%', pad=0.0,
                      name='bed', axis_limits=(0, 1), intron_height=0.05,
                      colors=None, track_label=None):
        """
        Adds one bed track along either the x- or y-axis of the heatmap.

        Parameters
        ----------
        bed_tracks : list of dict
            Each dict should represent a bed feature and could have the
            following keys::

                {
                    'chrom' : str,
                    'start' : int,
                    'end'   : int,
                    'strand': '+' or '-'
                }

            The 'strand' key is optional and is only used for color-coding bed
            features when ``colors`` is passed.
        loc : {'top', 'bottom', 'left', 'right'}
            Which side of the heatmap to add the new bed track to.
        size : str
            The size of the new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad : float
            The padding to use between the existing parts of the figure and the
            newly added axis.
        name : str
            Base name for the new axis. This name will be prefixed with the
            orientation of the track ('vertical' or 'horizontal').
        axis_limits : tuple of float
            Axis limits for the non-genomic axis of the bed track.
        intron_height : float
            The height to draw each bed feature with.
        colors : dict, optional
            Map from the value of the 'strand' key in the ``bed_tracks`` dicts
            (usually '+' or '-') to color name for bed features with that strand
            value (i.e., orientation). If not provided for a given strand or if
            the bed feature doesn't have a 'strand' key the color is black by
            default.
        track_label : str, optional
            Pass a string to label the track.

        Returns
        -------
        pyplot axis
            The newly added bed track axis.
        """
        # deduce orientation, either h or v, and save the correct grange
        if loc in ['bottom', 'top']:
            orientation = 'horizontal'
            grange = self.grange_x
        else:
            orientation = 'vertical'
            grange = self.grange_y

        # create new axis
        ax = self.add_margin_ax(loc=loc, size=size, pad=pad,
                                new_ax_name="{}_{}".format(orientation, name),
                                axis_limits=axis_limits)

        # deduce midpoint of the non-genomic axis
        midpoint = (axis_limits[0] + axis_limits[1]) / 2.

        # compute track_width and track_height, assuming horizontal orientation
        track_width = grange['end'] - grange['start']

        # create patches for each bed
        for bed in bed_tracks:
            # skip bed_tracks that don't intersect the window
            if not check_intersect(bed, grange):
                continue

            # get the color for this bed
            try:
                color = colors[bed['strand']]
            except (TypeError, KeyError):
                color = 'k'

            # plot small rectangle for length of bed
            intron_coords = [bed['start'], midpoint - intron_height / 2.]
            intron_dims = [bed['end'] - bed['start'], intron_height]
            if orientation == 'vertical':
                intron_coords.reverse()
                intron_dims.reverse()
            ax.add_artist(mpl.patches.Rectangle(intron_coords, *intron_dims,
                                                fc=color, ec=color))
        # done looping over all bed_tracks

        # write label of bed track, if specified
        if track_label:
            name_coords = [grange['start'] + track_width / 80, axis_limits[1]]
            ha = 'left'
            va = 'top'
            rotation = 0
            if orientation == 'vertical':
                name_coords.reverse()
                ha = 'right'
                rotation = 270
            ax.text(name_coords[0], name_coords[1], track_label, fontsize=7,
                    ha=ha, va=va, rotation=rotation)

        # return axis for this track
        return ax
