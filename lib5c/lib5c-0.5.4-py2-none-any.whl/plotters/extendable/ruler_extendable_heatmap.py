"""
Module for the RulerExtendableHeatmap class, which adds ruler track plotting
functionality for the extendable heatmap system.
"""

import numpy as np

from lib5c.plotters.extendable import BaseExtendableHeatmap


class RulerExtendableHeatmap(BaseExtendableHeatmap):
    """
    ExtendableHeatmap mixin class providing ruler track plotting functionality.
    """
    def add_rulers(self, size='5%', pad=0.0, axis_limits=(1, 0),
                   ruler_tick_height=0.3, ruler_text_baseline=0.5,
                   no_ticks=False, fontsize=7, no_tick_precision=2):
        """
        Adds a ruler track to both the bottom and left side of the heatmap by
        calling ``add_ruler()`` twice.

        Parameters
        ----------
        size : str
            The size of the new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad : float
            The padding to use between the existing parts of the figure and the
            newly added axis.
        axis_limits : tuple of float
            Axis limits for the non-genomic axis of the ruler track.
        ruler_tick_height : float
            The height of the ruler ticks.
        ruler_text_baseline : float
            Controls how far away from the top of the new axis the text elements
            (chromosome name and region size) will be drawn.
        no_ticks : bool
            Pass True to skip plotting ruler ticks, and instead write the start
            and end coordinate of the plotted region in units of megabase pairs.
        fontsize : float
            The font size to use for adding labels to the ruler axis.
        no_tick_precision : int
            When ``no_ticks`` is True, round the start and end coordinates of
            the plotted region to this many digits after the decimal.

        Returns
        -------
        list of pyplot axes
            The newly added gene ruler axes.
        """
        ax_h = self.add_ruler(loc='bottom', size=size, pad=pad,
                              new_ax_name='h_ruler', axis_limits=axis_limits,
                              ruler_tick_height=ruler_tick_height,
                              ruler_text_baseline=ruler_text_baseline,
                              no_ticks=no_ticks, fontsize=fontsize,
                              no_tick_precision=no_tick_precision)
        ax_v = self.add_ruler(loc='left', size=size, pad=pad,
                              new_ax_name='v_ruler', axis_limits=axis_limits,
                              ruler_tick_height=ruler_tick_height,
                              ruler_text_baseline=ruler_text_baseline,
                              no_ticks=no_ticks, fontsize=fontsize,
                              no_tick_precision=no_tick_precision)
        return [ax_h, ax_v]

    def add_ruler(self, loc='bottom', size='5%', pad=0.0, new_ax_name='ruler',
                  axis_limits=(1, 0), ruler_tick_height=0.3,
                  ruler_text_baseline=0.5, no_ticks=False, fontsize=7,
                  no_tick_precision=2):
        """
        Adds one ruler track along either the x- or y-axis of the heatmap.

        Parameters
        ----------
        loc : {'top', 'bottom', 'left', 'right'}
            Which side of the heatmap to add the new ruler track to.
        size : str
            The size of the new axis as a percentage of the main heatmap width.
            Should be passed as a string ending in '%'.
        pad : float
            The padding to use between the existing parts of the figure and the
            newly added axis.
        new_ax_name : str
            The name for the newly created axis.
        axis_limits : tuple of float
            Axis limits for the non-genomic axis of the ruler track.
        ruler_tick_height : float
            The height of the ruler ticks.
        ruler_text_baseline : float
            Controls how far away from the top of the new axis the text elements
            (chromosome name and region size) will be drawn.
        no_ticks : bool
            Pass True to skip plotting ruler ticks, and instead write the start
            and end coordinate of the plotted region in units of megabase pairs.
        fontsize : float
            The font size to use for adding labels to the ruler axis.
        no_tick_precision : int
            When ``no_ticks`` is True, round the start and end coordinates of
            the plotted region to this many digits after the decimal.

        Returns
        -------
        pyplot axis
            The newly added ruler track axis.
        """
        # create new axis
        ax = self.add_margin_ax(loc=loc, size=size, pad=pad,
                                new_ax_name=new_ax_name,
                                axis_limits=axis_limits)

        # deduce orientation, either h or v, and save the correct grange
        if loc in ['bottom', 'top']:
            orientation = 'horizontal'
            grange = self.grange_x
        else:
            orientation = 'vertical'
            grange = self.grange_y

        # compute tick positions
        tick_positions = np.linspace(grange['start'], grange['end'], 5)

        # compute track_width, assuming horizontal orientation
        track_width = grange['end'] - grange['start']

        if not no_ticks:
            # plot ticks and labels
            for i in range(1, 4):
                # ticks
                tick_coords = [(tick_positions[i], tick_positions[i]),
                               (0, ruler_tick_height)]
                if orientation == 'vertical':
                    tick_coords.reverse()
                ax.plot(*tick_coords, c='k', lw=1.25)

                # labels
                label_coords = [tick_positions[i], ruler_text_baseline]
                ha = 'center'
                va = 'top'
                rotation = 0
                if orientation == 'vertical':
                    label_coords.reverse()
                    ha = 'right'
                    va = 'center'
                    rotation = 270
                ax.text(label_coords[0], label_coords[1],
                        str(int(tick_positions[i])),
                        fontsize=fontsize, ha=ha, va=va, rotation=rotation)

        # write chromosome
        chrom_coords = [grange['start'] + track_width / 80, ruler_text_baseline]
        ha = 'left'
        va = 'top'
        rotation = 0
        if orientation == 'vertical':
            chrom_coords.reverse()
            ha = 'right'
            rotation = 270
        if no_ticks:
            MB_SCALE = 1e6  # to divide start and end by. Float so get decimals
            chrom_str = '{chrom}:{startMb:.{prec}f}-{endMb:.{prec}f}Mb'
            chrom_str = chrom_str.format(chrom=grange['chrom'],
                                         startMb=grange['start']/MB_SCALE,
                                         endMb=grange['end']/MB_SCALE,
                                         prec=no_tick_precision)
        else:
            chrom_str = '{chrom}'.format(chrom=grange['chrom'])
        ax.text(chrom_coords[0], chrom_coords[1], chrom_str, fontsize=fontsize,
                ha=ha, va=va, rotation=rotation)

        # write window width
        width_coords = [grange['end'] - track_width / 80, ruler_text_baseline]
        ha = 'right'
        va = 'top'
        rotation = 0
        if orientation == 'vertical':
            width_coords.reverse()
            va = 'bottom'
            rotation = 270
        ax.text(width_coords[0], width_coords[1],
                '%ikb' % (track_width // 1000), fontsize=fontsize, ha=ha, va=va,
                rotation=rotation)

        return ax
