"""
Module for the SNPExtendableHeatmap class, which adds SNP track plotting
functionality for the extendable heatmap system.
"""

import numpy as np
import matplotlib as mpl

from lib5c.plotters.extendable import BaseExtendableHeatmap
from lib5c.util.bed import check_intersect


class SNPExtendableHeatmap(BaseExtendableHeatmap):
    """
    ExtendableHeatmap mixin class providing SNP track plotting functionality.
    """
    def add_snp_tracks(self, snps, size='3%', pad=0.0, axis_limits=(0, 1),
                       snp_height=0.5, name='snp', colors=None,
                       track_label=None):
        """
        Adds SNP tracks for a single set of SNPs to both the bottom and left
        side of the heatmap by calling ``add_snp_track()`` twice.

        Parameters
        ----------
        snps : list of dict
            Each dict should represent a SNP and should have at least the
            following keys::

                {
                    'chrom' : str,
                    'start' : int,
                    'end'   : int
                }

            If color-coding SNPs, include a 'name' or 'id' key.
        size : str
            The size of the new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad : float
            The padding to use between the existing parts of the figure and the
            newly added axis.
        axis_limits : tuple of float
            Limits for the non-genomic axis of the SNP track.
        snp_height : float
            Height of SNP arrowheads in same units as ``axis_limits``.
        name : str
            The name for the new axis. This name will be prefixed with the
            orientation of the track ('vertical' or 'horizontal').
        colors : dict, optional
            Maps SNP ids or names to color names. Defaults to black if not
            passed or if a SNP's name or id are not found in the dict.
        track_label : str, optional
            Pass a string to label the track.

        Returns
        -------
        list of pyplot axes
            The newly added SNP track axes.
        """
        ax_h = self.add_snp_track(
            snps, loc='bottom', size=size, pad=pad, name=name,
            axis_limits=axis_limits, snp_height=snp_height, colors=colors,
            track_label=track_label
        )
        ax_v = self.add_snp_track(
            snps, loc='left', size=size, pad=pad, name=name,
            axis_limits=axis_limits, snp_height=snp_height, colors=colors,
            track_label=track_label
        )
        return [ax_h, ax_v]

    def add_snp_track(self, snps, loc='bottom', size='3%', pad=0.0, name='snp',
                      axis_limits=(0, 1), snp_height=0.5, colors=None,
                      track_label=None):
        """
        Adds one SNP track along either the x- or y-axis of the heatmap.

        Parameters
        ----------
        snps : list of dict
            Each dict should represent a SNP and should have at least the
            following keys::

                {
                    'chrom' : str,
                    'start' : int,
                    'end'   : int
                }

            If color-coding SNPs, include a 'name' or 'id' key.
        loc : {'top', 'bottom', 'left', 'right'}
            Which side of the heatmap to add the new SNP track to.
        size : str
            The size of the new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad : float
            The padding to use between the existing parts of the figure and the
            newly added axis.
        name : str
            The name for the new axis. This name will be prefixed with the
            orientation of the track ('vertical' or 'horizontal').
        axis_limits : tuple of float
            Limits for the non-genomic axis of the SNP track.
        snp_height : float
            Height of SNP arrowheads in same units as ``axis_limits``.
        colors : dict, optional
            Maps SNP ids or names to color names. Defaults to black if not
            passed or if a SNP's name or id are not found in the dict.
        track_label : str, optional
            Pass a string to label the track.

        Returns
        -------
        pyplot axis
            The newly added SNP track axis.
        """
        # deduce orientation, either h or v, and save the correct grange
        if loc in ['bottom', 'top']:
            orientation = 'horizontal'
            grange = self.grange_x
        else:  # left/right
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

        # draw arrowheads for each snp
        for snp in snps:
            # skip snps that don't intersect the window
            if not check_intersect(snp, grange):
                continue

            # get the color for this snp
            try:
                color = colors[snp['id']]
            except TypeError:
                color = 'k'
            except KeyError:
                try:
                    color = colors[snp['name']]
                except KeyError:
                    color = 'k'
            # done getting color

            # plot a little arrow pointing at where the SNP is
            # take the average of start and end as SNP location...
            snp_location = (snp['start'] + snp['end']) / 2.
            # get radius of arrow (half its width)
            # make it take up 1/75 of genomic range
            arrow_radius = track_width / 150.
            # define coordinates for triangle/arrow
            arrow_coords = np.array(
                [[snp_location, midpoint + snp_height / 2.],
                 [snp_location - arrow_radius, midpoint - snp_height / 2.],
                 [snp_location + arrow_radius, midpoint - snp_height / 2.]])
            # flip coordinates if necessary
            if orientation == "vertical":
                arrow_coords = arrow_coords[:, ::-1]
            # make the matplotlib polygon and add it to the axis
            arrowhead = mpl.patches.Polygon(np.array(arrow_coords),
                                            closed=True, fc=color)
            ax.add_artist(arrowhead)

        # done looping over each snp

        # write name of snp track, if specified
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

        return ax
