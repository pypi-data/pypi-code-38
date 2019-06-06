# -*- coding: utf-8 -*-
# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""Color tools for plotting."""
from collections import Iterator
from itertools import product
import operator

import numpy as np
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.colorbar import ColorbarBase

from .._colorspaces import to_rgb, oneway_colors, twoway_colors, SymmetricNormalize
from .._data_obj import Factor, Interaction, cellname
from .._utils import IS_WINDOWS
from ._base import EelFigure, Layout, find_axis_params_data, fix_vlim_for_cmap
from functools import reduce


POINT_SIZE = 0.0138889  # 1 point in inches
LEGEND_SIZE = 1.2  # times font.size


def find_cell_colors(x, colors):
    """Process the colors arg from plotting functions

    Parameters
    ----------
    x : categorial
        Model for which colors are needed.
    colors : str | list | dict
        Colors for the plots if multiple categories of data are plotted.
        **str**: A colormap name; cells are mapped onto the colormap in
        regular intervals.
        **list**: A list of colors in the same sequence as cells.
        **dict**: A dictionary mapping each cell to a color.
        Colors are specified as `matplotlib compatible color arguments
        <http://matplotlib.org/api/colors_api.html>`_.
    """
    if isinstance(colors, (list, tuple)):
        cells = x.cells
        if len(colors) < len(cells):
            err = ("The `colors` argument %s does not supply enough "
                   "colors (%i) for %i "
                   "cells." % (str(colors), len(colors), len(cells)))
            raise ValueError(err)
        return dict(zip(cells, colors))
    elif isinstance(colors, dict):
        for cell in x.cells:
            if cell not in colors:
                raise KeyError("%s not in colors" % repr(cell))
        return colors
    elif colors is None:
        return colors_for_categorial(x, cmap=colors)
    else:
        raise TypeError("Invalid type: colors=%s" % repr(colors))


def colors_for_categorial(x, hue_start=0.2, cmap=None):
    """Automatically select colors for a categorial model

    Parameters
    ----------
    x : categorial
        Model defining the cells for which to define colors.
    hue_start : 0 <= scalar < 1
        First hue value (only for two-way or higher level models).
    cmap : str (optional)
        Name of a matplotlib colormap to use instead of default hue-based
        colors (only used for one-way models).

    Returns
    -------
    colors : dict {cell -> color}
        Dictionary providing colors for the cells in x.
    """
    if isinstance(x, Factor):
        return colors_for_oneway(x.cells, hue_start, cmap=cmap)
    elif isinstance(x, Interaction):
        return colors_for_nway([f.cells for f in x.base], hue_start)
    else:
        raise TypeError(f"x={x!r}: needs to be Factor or Interaction")


def colors_for_oneway(cells, hue_start=0.2, light_range=0.5, cmap=None,
                      light_cycle=None, always_cycle_hue=False, locations=None):
    """Define colors for a single factor design

    Parameters
    ----------
    cells : sequence of str
        Cells for which to assign colors.
    hue_start : 0 <= scalar < 1 | sequence of scalar
        First hue value (default 0.2) or list of hue values.
    light_range : scalar | tuple of 2 scalar
        Scalar that specifies the amount of lightness variation (default 0.5).
        If positive, the first color is lightest; if negative, the first color
        is darkest. A tuple can be used to specify exact end-points (e.g., 
        ``(1.0, 0.4)``). ``0.2`` is equivalent to ``(0.4, 0.6)``.
        The ``light_cycle`` parameter can be used to cycle between light and 
        dark more than once. 
    cmap : str
        Use a matplotlib colormap instead of the default color generation
        algorithm. Name of a matplotlib colormap to use (e.g., 'jet'). If
        specified, ``hue_start`` and ``light_range`` are ignored.
    light_cycle : int
        Cycle from light to dark in ``light_cycle`` cells to make nearby colors 
        more distinct (default cycles once).
    always_cycle_hue : bool
        Cycle hue even when cycling lightness. With ``False`` (default), hue
        is constant within a lightness cycle.
    locations : sequence of float
        Locations of the cells on the color-map (all in range [0, 1]; default is
        evenly spaced; example: ``numpy.linspace(0, 1, len(cells)) ** 0.5``).

    Returns
    -------
    dict : {str: tuple}
        Mapping from cells to colors.
    """
    if isinstance(cells, Iterator):
        cells = tuple(cells)
    n = len(cells)
    if cmap is None:
        colors = oneway_colors(n, hue_start, light_range, light_cycle, always_cycle_hue, locations)
    else:
        cm = mpl.cm.get_cmap(cmap)
        if locations is None:
            imax = n - 1
            locations = (i / imax for i in range(n))
        colors = (cm(x) for x in locations)
    return dict(zip(cells, colors))


def colors_for_twoway(x1_cells, x2_cells, hue_start=0.2, hue_shift=0.,
                      hues=None):
    """Define cell colors for a two-way design

    Parameters
    ----------
    x1_cells : tuple of str
        Cells of the major factor.
    x2_cells : tuple of str
        Cells of the minor factor.
    hue_start : 0 <= scalar < 1
        First hue value.
    hue_shift : 0 <= scalar < 1
        Use that part of the hue continuum between categories to shift hue
        within categories.
    hues : list of scalar
        List of hue values corresponding to the levels of the first factor
        (overrides regular hue distribution).

    Returns
    -------
    dict : {tuple: tuple}
        Mapping from cells to colors.
    """
    n1 = len(x1_cells)
    n2 = len(x2_cells)

    if n1 < 2 or n2 < 2:
        raise ValueError("Need at least 2 cells on each factor")

    clist = twoway_colors(n1, n2, hue_start, hue_shift, hues)
    return dict(zip(product(x1_cells, x2_cells), clist))


def colors_for_nway(cell_lists, hue_start=0.2):
    """Define cell colors for a two-way design

    Parameters
    ----------
    cell_lists : sequence of of tuple of str
        List of the cells for each factor. E.g. for ``A % B``:
        ``[('a1', 'a2'), ('b1', 'b2', 'b3')]``.
    hue_start : 0 <= scalar < 1
        First hue value.

    Returns
    -------
    dict : {tuple: tuple}
        Mapping from cells to colors.
    """
    if len(cell_lists) == 1:
        return colors_for_oneway(cell_lists[0])
    elif len(cell_lists) == 2:
        return colors_for_twoway(cell_lists[0], cell_lists[1], hue_start)
    elif len(cell_lists) > 2:
        ns = tuple(map(len, cell_lists))
        n_outer = reduce(operator.mul, ns[:-1])
        n_inner = ns[-1]

        # outer circle
        hues = np.linspace(hue_start, 1 + hue_start, ns[0], False)
        # subdivide for each  level
        distance = 1. / ns[0]
        for n_current in ns[1:-1]:
            new = []
            d = distance / 3
            for hue in hues:
                new.extend(np.linspace(hue - d, hue + d, n_current))
            hues = new
            distance = 2 * d / (n_current - 1)
        hues = np.asarray(hues)
        hues %= 1
        colors = twoway_colors(n_outer, n_inner, hues=hues)
        return dict(zip(product(*cell_lists), colors))
    else:
        return {}


def single_hue_colormap(hue):
    """Colormap based on single hue

    Parameters
    ----------
    hue : matplotlib color
        Base RGB color.

    Returns
    -------
    colormap : matplotlib Colormap
        Colormap from transparent to ``hue``.
    """
    name = str(hue)
    color = to_rgb(hue)
    start = color + (0.,)
    stop = color + (1.,)
    return LinearSegmentedColormap.from_list(name, (start, stop))


class ColorGrid(EelFigure):
    """Plot colors for a two-way design in a grid

    Parameters
    ----------
    row_cells : tuple of str
        Cells contained in the rows.
    column_cells : tuple of str
        Cells contained in the columns.
    colors : dict
        Colors for cells.
    size : scalar
        Size (width and height) of the color squares (the default is to
        scale them to fit the figure).
    column_label_position : 'top' | 'bottom'
        Where to place the column labels (default is 'top').
    row_first : bool
        Whether the row cell precedes the column cell in color keys. By
        default this is inferred from the existing keys.
    labels : dict (optional)
        Condition labels that are used instead of the keys in ``row_cells`` and
        ``column_cells``.
    shape : 'box' | 'line'
        Shape for color samples (default 'box').
    ...
        Also accepts :ref:`general-layout-parameters`.
    """
    def __init__(self, row_cells, column_cells, colors, size=None,
                 column_label_position='top', row_first=None, labels=None,
                 shape='box', *args, **kwargs):
        if row_first is None:
            row_cell_0 = row_cells[0]
            col_cell_0 = column_cells[0]
            if (row_cell_0, col_cell_0) in colors:
                row_first = True
            elif (col_cell_0, row_cell_0) in colors:
                row_first = False
            else:
                msg = ("Neither %s nor %s exist as a key in colors" %
                       ((row_cell_0, col_cell_0), (col_cell_0, row_cell_0)))
                raise KeyError(msg)

        if size is None:
            size = mpl.rcParams['font.size'] * LEGEND_SIZE * POINT_SIZE
        layout = Layout(0, 1, 3, False, *args, **kwargs)
        EelFigure.__init__(self, None, layout)
        ax = self.figure.add_axes((0, 0, 1, 1), frameon=False)
        ax.set_axis_off()
        self._ax = ax

        # reverse rows so we can plot upwards
        row_cells = tuple(reversed(row_cells))
        n_rows = len(row_cells)
        n_cols = len(column_cells)

        # color patches
        for col in range(n_cols):
            for row in range(n_rows):
                if row_first:
                    cell = (row_cells[row], column_cells[col])
                else:
                    cell = (column_cells[col], row_cells[row])

                if shape == 'box':
                    patch = mpl.patches.Rectangle((col, row), 1, 1, fc=colors[cell],
                                                  ec='none')
                    ax.add_patch(patch)
                elif shape == 'line':
                    y = row + 0.5
                    ax.plot([col, col + 1], [y, y], color=colors[cell])
                else:
                    raise ValueError("shape=%r" % (shape,))

        # prepare labels
        if labels:
            column_labels = [labels.get(c, c) for c in column_cells]
            row_labels = [labels.get(c, c) for c in row_cells]
        else:
            column_labels = column_cells
            row_labels = row_cells

        # column labels
        tilt_labels = any(len(label) > 1 for label in column_labels)
        self._labels = []
        if column_label_position == 'top':
            y = n_rows + 0.1
            va = 'bottom'
            rotation = 40 if tilt_labels else 0
            ymin = 0
            ymax = self._layout.h / size
        elif column_label_position == 'bottom':
            y = -0.1
            va = 'top'
            rotation = -40 if tilt_labels else 0
            ymax = n_rows
            ymin = n_rows - self._layout.h / size
        else:
            msg = "column_label_position=%s" % repr(column_label_position)
            raise ValueError(msg)

        for col, label in enumerate(column_labels):
            h = ax.text(col + 0.5, y, label, va=va,
                        ha='left' if tilt_labels else 'center',
                        rotation=rotation)
            self._labels.append(h)

        # row labels
        x = n_cols + 0.1
        for row, label in enumerate(row_labels):
            h = ax.text(x, row + 0.5, label, va='center', ha='left')
            self._labels.append(h)

        if size is not None:
            self._ax.set_xlim(0, self._layout.w / size)
            self._ax.set_ylim(ymin, ymax)

        self._show()

    def _tight(self):
        # arbitrary default with equal aspect
        self._ax.set_ylim(0, 1)
        self._ax.set_xlim(0, 1 * self._layout.w / self._layout.h)

        # draw to compute text coordinates
        self.draw()

        # find label bounding box
        xmax = 0
        ymax = 0
        for h in self._labels:
            bbox = h.get_window_extent()
            if bbox.xmax > xmax:
                xmax = bbox.xmax
                xpos = h.get_position()[0]
            if bbox.ymax > ymax:
                ymax = bbox.ymax
                ypos = h.get_position()[1]
        xmax += 2
        ymax += 2

        # transform from display coordinates -> data coordinates
        trans = self._ax.transData.inverted()
        xmax, ymax = trans.transform((xmax, ymax))

        # calculate required movement
        _, ax_xmax = self._ax.get_xlim()
        _, ax_ymax = self._ax.get_ylim()
        xtrans = ax_xmax - xmax
        ytrans = ax_ymax - ymax

        # calculate the scale factor:
        # new_coord = x * coord
        # new_coord = coord + trans
        # x = (coord + trans) / coord
        scale = (xpos + xtrans) / xpos
        scale_y = (ypos + ytrans) / ypos
        if scale_y <= scale:
            scale = scale_y

        self._ax.set_xlim(0, ax_xmax / scale)
        self._ax.set_ylim(0, ax_ymax / scale)


class ColorList(EelFigure):
    """Plot colors with labels

    Parameters
    ----------
    colors : dict
        Colors for cells.
    cells : tuple
        Cells for which to plot colors (default is ``colors.keys()``).
    labels : dict (optional)
        Condition labels that are used instead of the keys in ``colors``. This
        is useful if ``colors`` uses abbreviated labels, but the color legend
        should contain more intelligible labels.
    h : 'auto' | scalar
        Height of the figure in inches. If 'auto' (default), the height is
        automatically increased to fit all labels.
    ...
        Also accepts :ref:`general-layout-parameters`.
    """
    def __init__(self, colors, cells=None, labels=None, h='auto', *args,
                 **kwargs):
        if cells is None:
            cells = tuple(colors.keys())
        elif isinstance(cells, Iterator):
            cells = tuple(cells)

        if h == 'auto':
            h = len(cells) * mpl.rcParams['font.size'] * POINT_SIZE * LEGEND_SIZE

        if labels is None:
            labels = {cell: cellname(cell) for cell in cells}
        elif not isinstance(labels, dict):
            raise TypeError("labels=%s" % repr(labels))

        layout = Layout(0, 1.5, 2, False, False, h, *args, **kwargs)
        EelFigure.__init__(self, None, layout)

        ax = self.figure.add_axes((0, 0, 1, 1), frameon=False)
        ax.set_axis_off()

        n = len(cells)
        self._labels = []
        for i, cell in enumerate(cells):
            bottom = n - i - 1
            y = bottom + 0.5
            patch = mpl.patches.Rectangle((0, bottom), 1, 1, fc=colors[cell],
                                          ec='none', zorder=1)
            ax.add_patch(patch)
            h = ax.text(1.1, y, labels.get(cell, cell), va='center', ha='left', zorder=2)
            self._labels.append(h)

        ax.set_ylim(0, n)
        ax.set_xlim(0, n * self._layout.w / self._layout.h)

        # resize figure to match legend
        if not self._layout.w_fixed:
            self.draw()
            # all calculation in pixels
            fig_bb = self.figure.get_window_extent()
            x_max = max(h.get_window_extent().x1 for h in self._labels)
            w0, h0 = self._frame.GetSize()
            new_w = w0 + (x_max - fig_bb.x1) + 5
            self._frame.SetSize((new_w, h0))
            # adjust x-limits
            # self.draw()
            ax_bb = ax.get_window_extent()
            ax.set_xlim(0, n * ax_bb.width / ax_bb.height)

        self._ax = ax
        self._show()
        if IS_WINDOWS:
            self._frame.Fit()


class ColorBar(EelFigure):
    """A color-bar for a matplotlib color-map

    Parameters
    ----------
    cmap : str | Colormap | array
        Name of the color-map, or a matplotlib Colormap, or LUT.
    vmin : scalar
        Lower end of the scale mapped onto cmap.
    vmax : scalar
        Upper end of the scale mapped onto cmap.
    label : bool | str
        Label for the x-axis (default is the unit, or if no unit is provided
        the name of the colormap).
    label_position : 'left' | 'right' | 'top' | 'bottom'
        Position of the axis label. Valid values depend on orientation.
    label_rotation : scalar
        Angle of the label in degrees (For horizontal colorbars, the default is
        0; for vertical colorbars, the default is 0 for labels of 3 characters
        and shorter, and 90 for longer labels).
    clipmin : scalar
        Clip the color-bar below this value.
    clipmax : scalar
        Clip the color-bar above this value.
    orientation : 'horizontal' | 'vertical'
        Orientation of the bar (default is horizontal).
    unit : str
        Unit for the axis to determine tick labels (for example, ``u'µV'`` to
        label 0.000001 as '1').
    contours : iterator of scalar (optional)
        Plot contour lines at these values.
    width : scalar
        Width of the color-bar in inches.
    ticks : {float: str} dict | sequence of float
        Customize tick-labels on the colormap; either a dictionary with
        tick-locations and labels, or a sequence of tick locations. To draw no
        ticks, set to ``()``.
    threshold : scalar
        Set the alpha of values below ``threshold`` to 0 (as well as for
        negative values above ``abs(threshold)``).
    ticklocation : 'auto', 'top', 'bottom', 'left', 'right'
        Where to place ticks and label.
    background : matplotlib color
        Background color (for colormaps including transparency).
    ...
        Also accepts :ref:`general-layout-parameters`.
    """
    def __init__(self, cmap, vmin, vmax=None, label=True, label_position=None,
                 label_rotation=None,
                 clipmin=None, clipmax=None, orientation='horizontal',
                 unit=None, contours=(), width=None, ticks=None, threshold=None,
                 ticklocation='auto', background='white', tight=True,
                 h=None, w=None, *args, **kwargs):
        # get Colormap
        if isinstance(cmap, np.ndarray):
            if threshold is not None:
                raise NotImplementedError("threshold parameter with cmap=array")
            if cmap.max() > 1:
                cmap = cmap / 255.
            cm = mpl.colors.ListedColormap(cmap, 'LUT')
        else:
            cm = mpl.cm.get_cmap(cmap)

        # prepare layout
        if orientation == 'horizontal':
            if h is None and w is None:
                h = 1
            ax_aspect = 4
        elif orientation == 'vertical':
            if h is None and w is None:
                h = 4
            ax_aspect = 0.3
        else:
            raise ValueError("orientation=%s" % repr(orientation))

        layout = Layout(1, ax_aspect, 2, tight, False, h, w, *args, **kwargs)
        EelFigure.__init__(self, cm.name, layout)
        ax = self._axes[0]

        # translate between axes and data coordinates
        if isinstance(vmin, Normalize):
            norm = vmin
        else:
            vmin, vmax = fix_vlim_for_cmap(vmin, vmax, cm.name)
            norm = Normalize(vmin, vmax)

        # value ticks
        if ticks is False:
            ticks = ()
            tick_labels = None
        elif isinstance(ticks, dict):
            tick_dict = ticks
            ticks = sorted(tick_dict)
            tick_labels = [tick_dict[t] for t in ticks]
        else:
            tick_labels = None

        if orientation == 'horizontal':
            axis = ax.xaxis
            contour_func = ax.axhline
        else:
            axis = ax.yaxis
            contour_func = ax.axvline

        if label is True:
            if unit:
                label = unit
            else:
                label = cm.name
        elif not label:
            label = ''

        # show only part of the colorbar
        if clipmin is not None or clipmax is not None:
            if isinstance(norm, SymmetricNormalize):
                raise NotImplementedError(
                    "clipmin or clipmax with SymmetricNormalize")
            boundaries = norm.inverse(np.linspace(0, 1, cm.N + 1))
            if clipmin is None:
                start = None
            else:
                start = np.digitize(clipmin, boundaries, True)
            if clipmax is None:
                stop = None
            else:
                stop = np.digitize(clipmax, boundaries) + 1
            boundaries = boundaries[start:stop]
        else:
            boundaries = None

        colorbar = ColorbarBase(ax, cm, norm, boundaries=boundaries,
                                orientation=orientation,
                                ticklocation=ticklocation, ticks=ticks,
                                label=label)

        # fix tick location
        if isinstance(norm, SymmetricNormalize) and ticks is not None:
            tick_norm = Normalize(norm.vmin, norm.vmax, norm.clip)
            axis.set_ticks(tick_norm(ticks))

        # unit-based tick-labels
        if unit and tick_labels is None:
            formatter, label = find_axis_params_data(unit, label)
            tick_labels = tuple(map(formatter, colorbar.get_ticks()))

        if tick_labels is not None:
            if clipmin is not None:
                tick_labels = [l for l, t in zip(tick_labels, ticks) if t >= clipmin]
            axis.set_ticklabels(tick_labels)

        # label position/rotation
        if label_position is not None:
            axis.set_label_position(label_position)
        if label_rotation is not None:
            axis.label.set_rotation(label_rotation)
            if orientation == 'vertical':
                if (label_rotation + 10) % 360 < 20:
                    axis.label.set_va('center')
        elif orientation == 'vertical' and len(label) <= 3:
            axis.label.set_rotation(0)
            axis.label.set_va('center')

        self._contours = [contour_func(c, c='k') for c in contours]
        self._draw_hooks.append(self.__fix_alpha)
        self._draw_hooks.append(self.__update_bar_tickness)

        self._background = background
        self._colorbar = colorbar
        self._orientation = orientation
        self._width = width
        self._show()

    def __fix_alpha(self):
        # fix cmaps with alpha https://stackoverflow.com/q/15003353/166700
        if self._background is not False:
            lut = self._colorbar.solids.get_facecolor()
            bg_color = to_rgb(self._background)
            lut[:, :3] *= lut[:, 3:]
            lut[:, :3] += (1 - lut[:, 3:]) * bg_color
            lut[:, 3] = 1.
            self._colorbar.solids.set_facecolor(lut)
            return True

    def _tight(self):
        # make sure ticklabels have space
        ax = self._axes[0]
        if self._orientation == 'vertical' and not self._layout.w_fixed:
            self.draw()
            labels = ax.get_yticklabels()
            # wmax = max(l.get_window_extent().width for l in labels)
            x0 = min(l.get_window_extent().x0 for l in labels)
            if x0 < 0:
                w, h = self.figure.get_size_inches()
                w -= (x0 / self._layout.dpi)
                self.figure.set_size_inches(w, h, forward=True)
        super(ColorBar, self)._tight()

    def __update_bar_tickness(self):
        # Override to keep bar thickness
        if not self._width:
            return
        ax = self._axes[0]
        x = (self._width, self._width)
        x = self.figure.dpi_scale_trans.transform(x)
        x = self.figure.transFigure.inverted().transform(x)
        pos = ax.get_position()
        xmin, ymin, width, height = pos.xmin, pos.ymin, pos.width, pos.height
        if self._orientation == 'vertical':
            if self._layout._margins_arg and 'right' in self._layout._margins_arg:
                xmin += width - x[0]
            width = x[0]
        else:
            if self._layout._margins_arg and 'top' in self._layout._margins_arg:
                ymin += height - x[1]
            height = x[1]
        ax.set_position((xmin, ymin, width, height))
        return True
