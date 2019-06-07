"""
Module for the MotifExtendableHeatmap class, which adds motif track plotting
functionality for the extendable heatmap system.
"""

import matplotlib as mpl

from lib5c.plotters.extendable import BaseExtendableHeatmap
from lib5c.util.bed import check_intersect


class MotifExtendableHeatmap(BaseExtendableHeatmap):
    """
    ExtendableHeatmap mixin class providing motif track plotting functionality.
    """
    def add_motif_tracks(self, motifs, size='3%', pad=0.0, axis_limits=(0, 1),
                         intron_height=0.05, exon_height=0.5, name='motif',
                         motif_linewidth=1, colors=None, track_label=None):
        """
        Adds motif tracks for a single set of motifs to both the bottom and left
        side of the heatmap by calling ``add_motif_track()`` twice.

        Parameters
        ----------
        motifs : list of dict
            Each dict should represent a motif instance and could have the
            following keys::

                {
                    'chrom' : str,
                    'start' : int,
                    'end'   : int,
                    'strand': '+' or '-'
                }

        size : str
            The size of the new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad : float
            The padding to use between the existing parts of the figure and the
            newly added axis.
        axis_limits : tuple of float
            Axis limits for the non-genomic axis of the motif track.
        intron_height : float
            Controls height of the rectangle spanning the length of the motif.
        exon_height : float
            Controls the size of the arrowhead that indicates the motif
            orientation.
        name : str
            Base name for the new axis. This name will be prefixed with the
            orientation of the track ('vertical' or 'horizontal').
        motif_linewidth : float
            The linewidth to use when plotting.
        colors : dict, optional
            Map from the value of the 'strand' key in the ``motifs`` dicts
            (usually '+' or '-') to color name for motifs with that strand value
            (i.e., orientation). If not provided for a given strand, color is
            black by default.
        track_label : str, optional
            Pass a string to label the track.

        Returns
        -------
        list of pyplot axes
            The newly added motif track axes.
        """
        ax_h = self.add_motif_track(
            motifs, loc='bottom', size=size, pad=pad, name=name,
            axis_limits=axis_limits, intron_height=intron_height,
            exon_height=exon_height, colors=colors, track_label=track_label,
            motif_linewidth=motif_linewidth
        )
        ax_v = self.add_motif_track(
            motifs, loc='left', size=size, pad=pad, name=name,
            axis_limits=axis_limits, intron_height=intron_height,
            exon_height=exon_height, colors=colors, track_label=track_label,
            motif_linewidth=motif_linewidth
        )
        return [ax_h, ax_v]

    def add_motif_track(self, motifs, loc='bottom', size='3%', pad=0.0,
                        name='motif', axis_limits=(0, 1), intron_height=0.05,
                        motif_linewidth=1, exon_height=0.5, colors=None,
                        track_label=None):
        """
        Adds one motif track along either the x- or y-axis of the heatmap.

        Parameters
        ----------
        motifs : list of dict
            Each dict should represent a motif instance and could have the
            following keys::

                {
                    'chrom' : str,
                    'start' : int,
                    'end'   : int,
                    'strand': '+' or '-'
                }

        loc : {'top', 'bottom', 'left', 'right'}
            Which side of the heatmap to add the new motif track to.
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
            Axis limits for the non-genomic axis of the motif track.
        intron_height : float
            Controls height of the rectangle spanning the length of the motif.
        motif_linewidth : float
            The linewidth to use when plotting.
        exon_height : float
            Controls the size of the arrowhead that indicates the motif
            orientation.
        colors : dict, optional
            Map from the value of the 'strand' key in the ``motifs`` dicts
            (usually '+' or '-') to color name for motifs with that strand value
            (i.e., orientation). If not provided for a given strand, color is
            black by default.
        track_label : str, optional
            Pass a string to label the track.

        Returns
        -------
        pyplot axis
            The newly added motif track axis.
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
        track_height = abs(axis_limits[1] - axis_limits[0])

        # create patches for each motif
        for motif in motifs:
            # skip motifs that don't intersect the window
            if not check_intersect(motif, grange):
                continue

            # get the color for this motif
            try:
                color = colors[motif['strand']]
            except (TypeError, KeyError):
                color = 'k'

            # plot small rectangle for length of motif
            intron_coords = [motif['start'], midpoint - intron_height / 2.]
            intron_dims = [motif['end'] - motif['start'], intron_height]
            if orientation == 'vertical':
                intron_coords.reverse()
                intron_dims.reverse()
            ax.add_artist(mpl.patches.Rectangle(
                intron_coords, *intron_dims, fc=color, ec=color,
                lw=motif_linewidth))

            # plot a little arrow based on the strand information if present
            # TODO: figure out why this factor of 40 is necessary
            arrow_size = (exon_height / 60.) * (track_width / track_height)
            if motif['strand'] == '+':
                xs = [motif['start'], motif['start'] - arrow_size]
                upper_ys = [midpoint, midpoint + exon_height / 2.]
                lower_ys = [midpoint, midpoint - exon_height / 2.]
            elif motif['strand'] == '-':
                xs = [motif['end'], motif['end'] + arrow_size]
                upper_ys = [midpoint, midpoint + exon_height / 2.]
                lower_ys = [midpoint, midpoint - exon_height / 2.]
            else:
                continue
            if orientation == 'vertical':
                ax.plot(upper_ys, xs, lw=motif_linewidth, color=color)
                ax.plot(lower_ys, xs, lw=motif_linewidth, color=color)
            else:
                ax.plot(xs, upper_ys, lw=motif_linewidth, color=color)
                ax.plot(xs, lower_ys, lw=motif_linewidth, color=color)

        # done looping over all motifs

        # write label of motif track, if specified
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
