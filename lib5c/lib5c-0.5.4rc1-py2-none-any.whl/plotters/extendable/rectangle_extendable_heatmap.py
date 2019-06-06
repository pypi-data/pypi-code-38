"""
Module for the RectangleExtendableHeatmap class, which adds rectangle outlining
functionality to the extendable heatmap system.
"""

import matplotlib.patches as patches

from lib5c.plotters.extendable import BaseExtendableHeatmap
from lib5c.util.bed import parse_feature_from_string, check_intersect


class RectangleExtendableHeatmap(BaseExtendableHeatmap):
    """
    ExtendableHeatmap mixin class providing rectangle outlining functionality.

    Unlike cluster outlining, which outlines specific pixels of the heatmap, or
    domain outlining, which outlines the upper or lower triangles of diagonal-
    aligned squares corresponding to domains, rectangle outlining simply draws a
    rectangle on the heatmap whose sides are described by genomic ranges.

    This can be used to outline cluster bounding boxes.
    """
    def add_rectangles(self, coords_list, color='#00FF00', weight='100x',
                       transpose=True):
        """
        Draw some rectangles (specified in genomic coordinates) on the heatmap.

        Parameters
        ----------
        coords_list : list of tuple of dict or list of str
            List of sets genomic coordinates (one set for each rectangle) to be
            plotted. The list can contain tuples::

                ({'chrom': str, 'start': int, 'end': int},
                 {'chrom': str, 'start': int, 'end': int})

            where the first dict specifies the genomic coordinates of one side
            of the rectangle, and the second dict specifies the genomic
            coordinates of the other side. The list can also contain strings of
            the form ``chrom:start-end_chrom:start-end``, where the ``_``
            separates genomic ranges which specify the coordinates of the two
            sides of the rectangle.
        color : valid matplotlib color
            The edge color to draw the rectangles with.
        weight : int or str
            The line width to use to draw the rectangles. Pass a string of the
            form ``'100x'`` to specify the line width as a multiple of the
            inverse of the size of this heatmap's array.
        transpose : bool
            Pass True to interpret the first feature in each tuple or string as
            the side of the rectangle parallel to the y-axis. Pass False to
            interpret it as the side parallel to the x-axis.
        """
        for coords in coords_list:
            self.add_rectangle(coords, color=color, weight=weight,
                               transpose=transpose)

    def add_rectangle(self, coords, color='#00FF00', weight='100x',
                      transpose=True):
        """
        Draw some rectangles (specified in genomic coordinates) on the heatmap.

        Parameters
        ----------
        coords : tuple of dict or str
            Genomic coordinates for the rectangle to be
            plotted. Can be a tuple::

                ({'chrom': str, 'start': int, 'end': int},
                 {'chrom': str, 'start': int, 'end': int})

            where the first dict specifies the genomic coordinates of one side
            of the rectangle, and the second dict specifies the genomic
            coordinates of the other side. Can also be a string of the form
            ``chrom:start-end_chrom:start-end``, where the ``_`` separates
            genomic ranges which specify the coordinates of the two sides of the
            rectangle.
        color : valid matplotlib color
            The edge color to draw the rectangle with.
        weight : int or str
            The line width to use to draw the rectangle. Pass a string of the
            form ``'100x'`` to specify the line width as a multiple of the
            inverse of the size of this heatmap's array.
        transpose : bool
            Pass True to interpret the first feature in ``coords`` as the side
            of the rectangle parallel to the y-axis. Pass False to interpret it
            as the side parallel to the x-axis.
        """
        # reference to root axis (heatmap)
        ax = self['root']

        # resolve line width
        linewidth = weight
        if type(weight) == str:
            linewidth = float(weight[:-1]) / len(self.array)

        # resolve coords
        if type(coords) == str:
            coords = map(parse_feature_from_string, coords.split('_'))

        # resolve transpose
        if transpose:
            y_coords, x_coords = coords
        else:
            x_coords, y_coords = coords

        # skip if not in the zoom window
        if not (check_intersect(x_coords, self.grange_x) and
                check_intersect(y_coords, self.grange_y)):
            return

        # transform to heatmap coordinates
        x_coords = self.transform_feature(x_coords, axis='x')
        y_coords = self.transform_feature(y_coords, axis='y')

        # plot rectangle
        ax.add_patch(patches.Rectangle(
            (x_coords['start'], y_coords['start']),
            x_coords['end'] - x_coords['start'],
            y_coords['end'] - y_coords['start'],
            fc='none', ec=color, lw=linewidth))
