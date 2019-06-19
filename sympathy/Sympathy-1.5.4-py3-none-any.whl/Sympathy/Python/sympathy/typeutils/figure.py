# Copyright (c) 2015, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
API for working with the Figure type.

Import this module like this::

    from sympathy.api import figure

.. _`markerstyles`:

Markers
-------

The methods :meth:`SyAxes.plot` allow the following marker styles:

    ======  ===========
    marker  description
    ======  ===========
    "o"	    circle
    "x"	    x
    "*"	    star
    ","	    pixel
    "."	    point
    "+"	    plus
    "D"	    diamond
    "s"	    square
    "_"	    hline
    "|"	    vline
    "^"	    triangle_up
    "d"	    thin_diamond
    "h"	    hexagon1
    "H"	    hexagon2
    "1"	    tri_down
    "2"	    tri_up
    "3"	    tri_left
    "4"	    tri_right
    "8"	    octagon
    "p"	    pentagon
    "v"	    triangle_down
    "<"	    triangle_left
    ">"	    triangle_right
    0	    tickleft
    1	    tickright
    2	    tickup
    3	    tickdown
    4	    caretleft
    5	    caretright
    6	    caretup
    7	    caretdown
    ""      nothing
    " "     nothing
    "None"	nothing
    None	nothing
    ======  ===========

.. _`colors`:

Colors
------

All color parameters accept the standard `matplotlib` colors formats:

- color names (see `Named colors
  <http://matplotlib.org/examples/color/named_colors.html>`_)
- RGB(A) colors as integer or float (e.g. (255, 255, 255) or (1., 1., 1., 1.))
- hex colors (e.g. '#eeefff')

For further information see matplotlibs
`color api <http://matplotlib.org/api/colors_api.html>`_.

.. _`location types`:

Location
--------

Whenever a location parameter is allowed, the following name strings
can be used.

    ===============   =============
    Location String   Location Code
    ===============   =============
    'best'            0 (only for legend)
    'upper right'     1
    'upper left'      2
    'lower left'      3
    'lower right'     4
    'right'           5
    'center left'     6
    'center right'    7
    'lower center'    8
    'upper center'    9
    'center'          10
    ===============   =============


Class :class:`figure.File`
--------------------------
.. autoclass:: File
   :members:
   :special-members:

Class :class:`figure.SyAxes`
----------------------------
.. autoclass:: SyAxes
    :members:
    :special-members:

Class :class:`figure.SyArtist`
------------------------------
.. autoclass:: SyArtist
    :members:
    :special-members:
"""
import os
import base64
import pickle
import warnings
import itertools
import collections

import numpy as np

from sympathy.platform.exceptions import sywarn
from ..utils import filebase
from ..utils.context import inherit_doc


def is_figure(scheme, filename):
    return File.is_type(filename, scheme)


def axes_wrapper(axes):
    if isinstance(axes, (collections.Sequence, np.ndarray)):
        wrapped = []
        for ax in axes:
            wrapped.append(axes_wrapper(ax))
        return wrapped
    else:
        return SyAxes(axes)


def _matplotlib():
    """
    Avoid pre-loading matplotlib since it takes too much time.

    Matplotlib import also has issues loading when python is installed on a
    unicode path causing unnecessary errors.
    """
    import matplotlib
    import matplotlib.backends.backend_agg
    import matplotlib.figure
    import matplotlib.tight_layout
    return matplotlib


@filebase.typeutil('sytypealias figure = sytext')
@inherit_doc
class File(filebase.TypeAlias):
    """
    A Figure.

    Any node port with the *Figure* type will produce an object of this type.
    """

    def init(self):
        self.__figure = None
        self.__ro_figure = None

    @staticmethod
    def _decode(text_data):
        figure = pickle.loads(base64.decodestring(text_data.encode('ascii')))
        for ax in figure.axes:
            SyAxes(ax).rotate_xlabels_if_date()
        return figure

    @staticmethod
    def _encode(fig):
        return base64.encodestring(pickle.dumps(
            fig, protocol=pickle.HIGHEST_PROTOCOL)).decode('ascii')

    def __deepcopy_figure(self, figure=None):
        figure = figure or self.__figure
        if figure is not None:
            return self._decode(self._encode(figure))
        return None

    def source(self, other, shallow=False):
        """Copy the contents from ``other`` :class:`figure.File`.
        Equivalent to :meth:`update`.
        """
        self._data.source(other._data, shallow=shallow)
        self.__ro_figure = other._ro_figure
        self.__figure = None

    def sync(self):
        figure = self.__figure or self.__ro_figure

        if figure is not None:
            self._data.set(self._encode(figure))
        self.__figure = None

    def __copy__(self):
        raise NotImplementedError

    def __deepcopy__(self, memo=None):
        obj = super(File, self).__deepcopy__()
        obj.__ro_figure = self._ro_figure
        obj.__figure = None
        return obj

    def _init_figure(self):
        if self.__figure is not None:
            return
        if self.__ro_figure:
            self.__figure = self.__deepcopy_figure(self.__ro_figure)
            self.__ro_figure = None
            return
        text_data = self._data.get()
        if text_data:
            self.__figure = self._decode(text_data)
        else:
            self.__figure = _matplotlib().figure.Figure(tight_layout=True)

    @property
    def _figure(self):
        self._init_figure()
        return self.__figure

    @property
    def _ro_figure(self):
        if self.__ro_figure is not None:
            return self.__ro_figure
        else:
            return self._figure

    @classmethod
    def viewer(cls):
        from .. platform import figure_viewer
        return figure_viewer.FigureViewer

    @classmethod
    def icon(cls):
        return 'ports/figure.svg'

    def get_mpl_figure(self):
        """Return the underlying matplotlib Figure object.

        Warnings
        --------
           When using this function you will get access to the entire
           matplotlib API. That API is likely to change slightly over time
           completely outside of our control. If you want to be sure that the
           code you are writing continues to work as expected in upcoming
           versions of Sympathy you should not use this method.
        """
        return self._figure

    # Figure interface
    @property
    def axes(self):
        return axes_wrapper(self._figure.axes)

    def set_dpi(self, dpi):
        """Set the dots-per-inch of the figure."""
        return self._figure.set_dpi(dpi)

    def set_title(self, title, fontsize=None):
        """
        Add a centered title to the figure.

        Parameters
        ----------
        fontsize : int or float or str, optional
            Controls the font size of the legend. If given as string,
            following strings are possible {'xx-small', 'x-small',
            'small', 'medium', 'large', 'x-large', 'xx-large'}.
            If the value is numeric the size will be the absolute
            font size in points. String values are relative to the
            current default font size.
        """
        return self._figure.suptitle(title, fontsize=fontsize)

    def subplots(self, nrows, ncols, sharex=False, sharey=False):
        """
        Create subplot axes.

        Parameters
        ----------
        nrows : int
            Number of rows of subplots.

        ncols : int
            Number of columns of subplots.

        sharex : bool, optional
            Defines if x-axis are shared amongst all subplots.

        sharey : bool, optional
            Defines if y-axis are shared amongst all subplots.

        Returns
        -------
        axes : list
            Returns a list of :class:`SyAxes` axes.
        """
        axes = np.zeros((nrows, ncols), dtype=object)
        sharex_ax = [None] * ncols
        sharey_ax = [None] * nrows
        for i, (xi, yi) in enumerate(
                itertools.product(range(nrows), range(ncols))):
            sharex_arg = sharex_ax[yi] if sharex else None
            sharey_arg = sharey_ax[xi] if sharey else None
            ax = self._figure.add_subplot(
                nrows, ncols, i + 1, sharex=sharex_arg, sharey=sharey_arg)
            axes[xi, yi] = ax
            if sharex_ax[yi] is None:
                sharex_ax[yi] = ax
            if sharey_ax[xi] is None:
                sharey_ax[xi] = ax
        return axes_wrapper(axes)

    def tight_layout(self):
        self._figure.tight_layout()

    def subplots_adjust(self, *args, **kwargs):
        self._figure.subplots_adjust(*args, **kwargs)

    def first_subplot(self):
        """Returns the first axes of the figure or creates one."""
        if self._figure.axes:
            ax = self._figure.axes[0]
        else:
            ax = self._figure.add_subplot(1, 1, 1)
        return SyAxes(ax)

    def colorbar(self, artist, orientation='vertical', label=None,
                 fraction=0.05, extend=None):
        """
        Add a colorbar to a Figure.

        A row/column will be added to the bottom/right of the subplot Gridspec
        layout depending on the specified orientation (horizontal/vertical).

        Parameters
        ----------
        artist : matplotlib.artist.Artist
            The artist which the colorbar should be linked to.
        orientation : unicode, optional
            The orientation of the colorbar. Options: vertical or horizontal.
            Default: vertical
        label : unicode or None, optional
            The label added to the long axis of colorbar. Default: None
        fraction : float, optional
            The faction of the colorbar should take within the whole figure.
            Default: 0.05 (5%)
        """
        # TODO: This function should possibly also handle adding colorbars to
        # subplots and not only to the whole figure.
        # first we need to extend the GridSpec to add column/row for the
        # colorbar axes
        subplotspec_list = _matplotlib().tight_layout.get_subplotspec_list(
            self._figure.axes)
        subplotspec = subplotspec_list[0]
        gridspec = subplotspec.get_gridspec()

        ncols = int(gridspec._ncols)
        nrows = int(gridspec._nrows)
        if orientation == 'vertical':
            gridspec._ncols += 1
            for sps in subplotspec_list:
                num1 = sps.num1
                sps.num1 = num1 + (num1 // ncols)
                # assume that each subplot covers a single cell of the grid
                sps.num2 = sps.num1
            gridspec.set_width_ratios(
                [(1 - fraction) / ncols] * ncols + [fraction])
            gridspec.update()
            cax = self._figure.add_subplot(gridspec[:, ncols])
        else:
            gridspec._nrows += 1
            gridspec.set_height_ratios(
                [(1 - fraction) / nrows] * nrows + [fraction])
            gridspec.update()
            cax = self._figure.add_subplot(gridspec[nrows, :])

        # hook back the changed gridspec into all subplotspecs
        for sps in subplotspec_list:
            sps._gridspec = gridspec

        # create the colorbar
        if isinstance(artist, SyArtist):
            artist = artist.get_mpl_artist()
        kw = {'cax': cax,
              'orientation': orientation}
        if extend is not None:
            kw['extend'] = extend
        if label is not None:
            kw['label'] = label
        colorbar = self._figure.colorbar(artist, **kw)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            self._figure.tight_layout()
        return SyArtist(colorbar)

    def rotate_xlabels_for_dates(self):
        """Rotates labels for all x axes if one is a datetime axis."""
        for syaxes in self.axes:
            syaxes.rotate_xlabels_if_date()

    def _get_qtcanvas(self):
        """Warning: This method will create a QApplication. It should not be
        called in the execute method of any node.
        """
        from sympathy.api import qt
        qt.backend.use_matplotlib_qt()
        from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
        return FigureCanvasQTAgg(self._ro_figure)

    def save_figure(self, filename, size, dpi=None):
        """Save figure to file.

        Parameters
        ----------
        filename : str
            The full path with filename including the extension.

        size : array_like, shape (2,)
            Tuple of width and height in pixels.

        dpi : int
            The dots-per-inch of the figure.
        """
        if dpi is None:
            dpi = self._ro_figure.dpi
        size_inches = (size[0] / float(dpi), size[1] / float(dpi))

        # This actually changes the figure so we should normally use
        # self._figure, but we don't really care about this minor change.
        self._ro_figure.set_dpi(dpi)
        self._ro_figure.set_size_inches(size_inches)

        ext = os.path.splitext(filename)[1][1:]
        # to support tiff, jpg etc pillow is required
        if ext in ['eps', 'pdf', 'pgf', 'png', 'ps', 'raw', 'rgba',
                   'svg', 'svgz']:
            canvas = _matplotlib().backends.backend_agg.FigureCanvasAgg(
                self._ro_figure)
            canvas.print_figure(filename, dpi=dpi)
        else:
            sywarn('The format "{}" is currently not '
                   'supported.'.format(ext))


class SyAxes(object):
    """Wrapper around matplotlib Axes."""

    def __init__(self, axes):
        self._axes = axes

    def get_mpl_axes(self):
        """Return the underlying matplotlib Axes object.

        Warnings
        --------
           When using this function you will get access to the entire
           matplotlib API. That API is likely to change slightly over time
           completely outside of our control. If you want to be sure that the
           code you are writing continues to work as expected in upcoming
           versions of Sympathy you should not use this method.
        """
        return self._axes

    def bar(self, left, height, width=0.8, bottom=None, color=None):
        """
        Make a bar plot.

        Make a bar plot with rectangles bounded by:

            left, left + width, bottom, bottom + height
                (left, right, bottom and top edges)

        Parameters
        ----------
        left : sequence of scalars
            the x coordinates of the left sides of the bars

        height : sequence of scalars
            the heights of the bars

        width : scalar or array-like, optional
            the width(s) of the bars
            default: 0.8

        bottom : scalar or array-like, optional
            the y coordinate(s) of the bars
            default: None

        color : scalar or array-like, optional
            face color of the bars

        Returns
        -------
        list
            List of :class:`SyArtist` s.
        """
        patches = self._axes.bar(left, height, width=width, bottom=bottom,
                                 color=color)
        return [SyArtist(patch) for patch in patches]

    def hist(self, x, bins=10, range=None, normed=False, weights=None,
             cumulative=False, bottom=None, histtype='bar', align='mid',
             orientation='vertical', rwidth=None, log=False,
             color=None, label=None, stacked=False):
        """
        Plot a histogram.

        Compute and draw the histogram of *x*. The return value is a
        tuple (*n*, *bins*, *patches*) or ([*n0*, *n1*, ...], *bins*,
        [*patches0*, *patches1*,...]) if the input contains multiple
        data.

        Multiple data can be provided via *x* as a list of datasets
        of potentially different length ([*x0*, *x1*, ...]), or as
        a 2-D ndarray in which each column is a dataset.  Note that
        the ndarray form is transposed relative to the list form.

        Masked arrays are not supported at present.

        Parameters
        ----------
        x : (n,) array or sequence of (n,) arrays
            Input values, this takes either a single array or a sequency of
            arrays which are not required to be of the same length

        bins : integer or array_like, optional
            If an integer is given, `bins + 1` bin edges are returned,
            consistently with :func:`numpy.histogram` for numpy version >=
            1.3.

            Unequally spaced bins are supported if `bins` is a sequence.

            default is 10

        range : tuple or None, optional
            The lower and upper range of the bins. Lower and upper outliers
            are ignored. If not provided, `range` is (x.min(), x.max()). Range
            has no effect if `bins` is a sequence.

            If `bins` is a sequence or `range` is specified, autoscaling
            is based on the specified bin range instead of the
            range of x.

            Default is ``None``

        normed : boolean, optional
            If `True`, the first element of the return tuple will
            be the counts normalized to form a probability density, i.e.,
            ``n/(len(x)`dbin)``, i.e., the integral of the histogram will sum
            to 1. If *stacked* is also *True*, the sum of the histograms is
            normalized to 1.

            Default is ``False``

        weights : (n, ) array_like or None, optional
            An array of weights, of the same shape as `x`.  Each value in `x`
            only contributes its associated weight towards the bin count
            (instead of 1).  If `normed` is True, the weights are normalized,
            so that the integral of the density over the range remains 1.

            Default is ``None``

        cumulative : boolean, optional
            If `True`, then a histogram is computed where each bin gives the
            counts in that bin plus all bins for smaller values. The last bin
            gives the total number of datapoints.  If `normed` is also `True`
            then the histogram is normalized such that the last bin equals 1.
            If `cumulative` evaluates to less than 0 (e.g., -1), the direction
            of accumulation is reversed.  In this case, if `normed` is also
            `True`, then the histogram is normalized such that the first bin
            equals 1.

            Default is ``False``

        bottom : array_like, scalar, or None
            Location of the bottom baseline of each bin.  If a scalar,
            the base line for each bin is shifted by the same amount.
            If an array, each bin is shifted independently and the length
            of bottom must match the number of bins.  If None, defaults to 0.

            Default is ``None``

        histtype : {'bar', 'barstacked', 'step',  'stepfilled'}, optional
            The type of histogram to draw.

            - 'bar' is a traditional bar-type histogram.  If multiple data
              are given the bars are aranged side by side.

            - 'barstacked' is a bar-type histogram where multiple
              data are stacked on top of each other.

            - 'step' generates a lineplot that is by default
              unfilled.

            - 'stepfilled' generates a lineplot that is by default
              filled.

            Default is 'bar'

        align : {'left', 'mid', 'right'}, optional
            Controls how the histogram is plotted.

            - 'left': bars are centered on the left bin edges.

            - 'mid': bars are centered between the bin edges.

            - 'right': bars are centered on the right bin edges.

            Default is 'mid'

        orientation : {'horizontal', 'vertical'}, optional
            If 'horizontal', the *bottom* kwarg will be the left edges.

        rwidth : scalar or None, optional
            The relative width of the bars as a fraction of the bin width.  If
            `None`, automatically compute the width.

            Ignored if `histtype` is 'step' or 'stepfilled'.

            Default is ``None``

        log : boolean, optional
            If `True`, the histogram axis will be set to a log scale. If `log`
            is `True` and `x` is a 1D array, empty bins will be filtered out
            and only the non-empty (`n`, `bins`, `patches`) will be returned.

            Default is ``False``

        color : color or array_like of colors or None, optional
            Color spec or sequence of color specs, one per dataset.  Default
            (`None`) uses the standard line color sequence.

            Default is ``None``

        label : string or None, optional
            String, or sequence of strings to match multiple datasets.  Bar
            charts yield multiple patches per dataset, but only the first gets
            the label, so that the legend command will work as expected.

            default is ``None``

        stacked : boolean, optional
            If `True`, multiple data are stacked on top of each other If
            `False` multiple data are aranged side by side if histtype is
            'bar' or on top of each other if histtype is 'step'

            Default is ``False``

        Returns
        -------
        n : array or list of arrays
            The values of the histogram bins. See **normed** and **weights**
            for a description of the possible semantics. If input **x** is an
            array, then this is an array of length **nbins**. If input is a
            sequence arrays ``[data1, data2,..]``, then this is a list of
            arrays with the values of the histograms for each of the arrays
            in the same order.

        bins : array
            The edges of the bins. Length nbins + 1 (nbins left edges and right
            edge of last bin).  Always a single array even when multiple data
            sets are passed in.
        """
        n, bins, patches = self._axes.hist(x, bins, range, normed, weights,
                                           cumulative, bottom, histtype, align,
                                           orientation, rwidth, log,
                                           color, label, stacked)

        # TODO: return patches (can be a list or list of lists)
        return n, bins

    def axvline(self, x=0, ymin=0, ymax=1, color=None,
                linewidth=1., linestyle='-'):
        """
        Add a vertical line across the axes.

        Parameters
        ----------
        x : scalar, optional, default: 0
            x position in data coordinates of the vertical line.

        ymin : scalar, optional, default: 0
            Should be between 0 and 1, 0 being the bottom
            of the plot, 1 the top of the plot.

        ymax : scalar, optional, default: 0
            Should be between 0 and 1, 0 being the bottom
            of the plot, 1 the top of the plot.

        linestyle : str, optional, default: '-'
            Any of ['solid' | 'dashed', 'dashdot', 'dotted' |
            '-' | '--' | '-.' | ':' | 'None' | ' ' | '']

        linewidth : float, optional
            Float value in points.

        color : color
            Any matplotlib color. See :ref:`colors`.

        Returns
        -------
        SyArtist
            Line2D wrapped in :class:`SyArtist`.
        """
        kwargs = {}
        if color is not None:
            kwargs['color'] = color
        if linewidth is not None:
            kwargs['linewidth'] = linewidth
        if linestyle is not None:
            kwargs['linestyle'] = linestyle
        return SyArtist(self._axes.axvline(x=x, ymin=ymin, ymax=ymax,
                                           **kwargs))

    def axhline(self, y=0, xmin=0, xmax=1, color=None,
                linewidth=1., linestyle='-'):
        """
        Add a horizontal line across the axis.

        Parameters
        ----------
        y : scalar, optional, default: 0
            y position in data coordinates of the horizontal line.

        xmin : scalar, optional, default: 0
            Should be between 0 and 1, 0 being the far left
            of the plot, 1 the far right of the plot.

        xmax : scalar, optional, default: 0
            Should be between 0 and 1, 0 being the far left
            of the plot, 1 the far right of the plot.

        linestyle : str, optional, default: '-'
            Any of ['solid' | 'dashed', 'dashdot', 'dotted' |
            '-' | '--' | '-.' | ':' | 'None' | ' ' | '']

        linewidth : float, optional
            Float value in points.

        color : color
            Any matplotlib color. See :ref:`colors`.

        Returns
        -------
        SyArtist
            Line2D wrapped in :class:`SyArtist`.
        """
        kwargs = {}
        if color is not None:
            kwargs['color'] = color
        if linewidth is not None:
            kwargs['linewidth'] = linewidth
        if linestyle is not None:
            kwargs['linestyle'] = linestyle
        return SyArtist(self._axes.axhline(y=y, xmin=xmin, xmax=xmax,
                                           **kwargs))

    def text(self, x, y, s, color=None, fontsize=None,
             bold=False, horizontalalignment='left',
             verticalalignment='top', data_coordinates=True):
        """
        Add text to the axes.

        Parameters
        ----------
        x : scalars
            x data coordinates.

        y : scalars
            y data coordinates.

        s : unicode
            The text to be shown.

        color : color, optional
            Any matplotlib color. See :ref:`colors`.

        bold : boolean, optional
            If ``True``, use a bold font. If ``False`` (the default), use a
            normal font.

        fontsize : int or float or str, optional
            Controls the font size of the legend. If given as string,
            following strings are possible {'xx-small', 'x-small',
            'small', 'medium', 'large', 'x-large', 'xx-large'}.
            If the value is numeric the size will be the absolute
            font size in points. String values are relative to the
            current default font size.

        horizontalalignment : {'center', 'right', 'left'}, optional

        verticalalignment : {'center', 'top', 'bottom', 'baseline'}, optional

        data_coordinates : bool, optional, default True
            If ``True``, `x` and `y` are assumed to be in data coordinates. If
            ``False``, they are assumed to be in axes coordinates.

        Returns
        -------
        SyArtist
            The text wrapped in a :class:`SyArtist`.
        """
        if data_coordinates:
            transform = self._axes.transData
        else:
            transform = self._axes.transAxes
        if bold:
            fontweight = 'bold'
        else:
            fontweight = 'normal'
        return SyArtist(self._axes.text(x=x, y=y, s=s, color=color,
                                        fontsize=fontsize,
                                        fontweight=fontweight,
                                        ha=horizontalalignment,
                                        va=verticalalignment,
                                        transform=transform))

    def scatter(self, x, y, size=20, color=None, marker='o',
                cmap=None, norm=None, vmin=None, vmax=None, alpha=None,
                linewidths=None, linestyles=None, edgecolors=None,
                label=None, zorder=None):
        """
        Make a scatter plot of x vs y, where x and y are sequence like objects
        of the same lengths.

        Parameters
        ----------
        x, y : array_like, shape (n, )
            Input data

        size : scalar or array_like, shape (n, ), optional, default: 20
            size in points^2.

        color : color or sequence of color, optional, default : 'b'
            `color` can be a single color format string, or a sequence of color
            specifications of length `N`, or a sequence of `N` numbers to be
            mapped to colors using the `cmap` and `norm` specified via kwargs
            (see below). Note that `color` should not be a single numeric RGB
            or RGBA sequence because that is indistinguishable from an array of
            values to be colormapped.  `color` can be a 2-D array in which the
            rows are RGB or RGBA, however, including the case of a single
            row to specify the same color for all points.
            See also :ref:`colors`.

        marker : marker, optional, default: 'o'
            See :ref:`markerstyles` for more information on the different
            styles of markers scatter supports. `marker` can be either
            an instance of the class or the text shorthand for a particular
            marker.

        cmap : `~matplotlib.colors.Colormap`, optional, default: None
            A `~matplotlib.colors.Colormap` instance or registered name.
            `cmap` is only used if `color` is an array of floats.

        norm : `~matplotlib.colors.Normalize`, optional, default: None
            A `~matplotlib.colors.Normalize` instance is used to scale
            luminance data to 0, 1. `norm` is only used if `color` is an array
            of floats. If `None`, use the default :func:`normalize`.

        vmin, vmax : scalar, optional, default: None
            `vmin` and `vmax` are used in conjunction with `norm` to normalize
            luminance data.  If either are `None`, the min and max of the
            color array is used.  Note if you pass a `norm` instance, your
            settings for `vmin` and `vmax` will be ignored.

        alpha : scalar, optional, default: None
            The alpha blending value, between 0 (transparent) and 1 (opaque)

        linewidths : scalar or array_like, optional, default: None

        edgecolors : color or sequence of color, optional, default: None
            If 'face', the edge color will always be the same as
            the face color.  If it is 'none', the patch boundary will not
            be drawn.  For non-filled markers, the `edgecolors` kwarg
            is ignored; color is determined by `color`.

        label : unicode, optional
            The label of the line.

        zorder : int, optional
            Define the z-order for this artist.
        """
        kwargs = {}
        if color is not None:
            kwargs['c'] = color
        if size is not None:
            kwargs['s'] = size
        if marker is not None:
            kwargs['marker'] = marker
        if label is not None:
            kwargs['label'] = label
        if cmap is not None:
            kwargs['cmap'] = cmap
        if norm is not None:
            kwargs['norm'] = norm
        if vmin is not None:
            kwargs['vmin'] = vmin
        if vmax is not None:
            kwargs['vmax'] = vmax
        if alpha is not None:
            kwargs['alpha'] = alpha
        if linewidths is not None:
            kwargs['linewidths'] = linewidths
        if linestyles is not None:
            kwargs['linestyles'] = linestyles
        if edgecolors is not None:
            kwargs['edgecolors'] = edgecolors
        if zorder is not None:
            kwargs['zorder'] = zorder

        scatter = self._axes.scatter(x, y, **kwargs)
        return SyArtist(scatter)

    def plot(self, x, y, label=None, color=None,
             marker=None, markersize=None, markeredgecolor=None,
             markeredgewidth=None, markerfacecolor=None,
             linestyle='-', linewidth=1., alpha=1.,
             drawstyle='default', zorder=None):
        """
        Plot lines and/or markers to the axes.

        Parameters
        ----------
        x : array_like, shape (n,)
            The data for the x axis.

        y : array_like, shape (n,)
            The data for the y axis.

        label : unicode, optional
            The label of the line.

        color : color, optional
            Any matplotlib color. See :ref:`colors`.

        marker : str, optional
            Defines the marker style. See :ref:`Markers <markerstyles>` for
            all available markers.

        markersize : float, optional
            Defines the marker size.s

        markeredgecolor : color, optional
            Any matplotlib color. See :ref:`colors`.

        markeredgewidth : float, optional
            Float value in points.

        markerfacecolor : color, optional
            Any matplotlib color. See :ref:`colors`.

        linestyle : str, optional
            Any of ['solid' | 'dashed', 'dashdot', 'dotted' |
            '-' | '--' | '-.' | ':' | 'None' | ' ' | '']

        linewidth : float, optional
            Float value in points.

        alpha : float, optional
            Defines the transparency. Float value between 0. and 1.
            Default is 1.

        drawstyle : str, optional
            Defines the drawstyle of the plot. Accepts:
            ['default', 'steps', 'steps-pre', 'steps-mid',
            'steps-post']

        zorder : int, optional
            Define the z-order for this artist.

        Returns
        -------
        artists : list
            Returns a list of :class:`SyArtist` s.
        """
        kwargs = {}
        if color is not None:
            kwargs['color'] = color
        if marker is not None:
            kwargs['marker'] = marker
        if linestyle is not None:
            kwargs['linestyle'] = linestyle
        if alpha is not None:
            kwargs['alpha'] = alpha
        if markersize is not None:
            kwargs['markersize'] = markersize
        if markeredgecolor is not None:
            kwargs['markeredgecolor'] = markeredgecolor
        if markeredgewidth is not None:
            kwargs['markeredgewidth'] = markeredgewidth
        if markerfacecolor is not None:
            kwargs['markerfacecolor'] = markerfacecolor
        if linewidth is not None:
            kwargs['linewidth'] = linewidth
        if drawstyle is not None:
            kwargs['drawstyle'] = drawstyle
        if label is not None:
            kwargs['label'] = label
        if zorder is not None:
            kwargs['zorder'] = zorder
        artists = self._axes.plot(x, y, **kwargs)
        return [SyArtist(a) for a in artists]

    def heatmap(self, x, y, c, cmap=None, vmin=None, vmax=None,
                edgecolor=None, linewidth=None):
        """
        Create a heatmap from

        Parameters
        ----------
        x : array_like, shape (m+1,)
            *x* is 1D arrays of length *nc* +1 giving the x boundaries
            of the cells.
        y : array_like, shape (n+1,)
            *y* is 1D arrays of length *nr* +1 giving the y boundaries
            of the cells.
        c : array_like, shape (m, n)
            A 2D array of color values.

        cmap : { *None* | Colormap }
            A :class:`matplotlib.colors.Colormap` instance. If *None*, use
            rc settings.

        edgecolor: {*None* | ``'None'`` | ``'face'`` | color | color sequence}
            If *None*, the rc setting is used by default.
            If ``'None'``, edges will not be visible.
            If ``'face'``, edges will have the same color as the faces.
            An mpl color or sequence of colors will set the edge color

        linewidth : float, optional
            Float value in points.

        Returns
        -------
        SyArtist
            :class:`SyArtist` of the matplotlib collection.
        """
        return SyArtist(self._axes.pcolormesh(x, y, c,
                                              cmap=cmap,
                                              vmin=vmin,
                                              vmax=vmax,
                                              edgecolor=edgecolor,
                                              linewidth=linewidth))

    def twinx(self):
        """Create a twin SyAxes with shared x-axis."""
        return SyAxes(self._axes.twinx())

    def twiny(self):
        """Create a twin SyAxes with shared y-axis."""
        return SyAxes(self._axes.twiny())

    def grid(self, b=None, which='major', axis='both',
             color=None, linestyle=None, linewidth=None):
        """
        Turn the axes grids on or off.

        Parameters
        ----------
        b : bool, optional
            Set the axes grids on or off. *None* with *len(kwargs)*
            toggles the grid state.

        which : str, optional
            Can be 'major' (default), 'minor', or 'both'. Controls
            whether only major, only minor, or both tick grids are
            affected.

        axis : str, optional
            Can be 'both' (default), 'x', or 'y'. Controls which set
            of gridlines are drawn.

        color : color, optional
            Any matplotlib color. See :ref:`colors`.

        linestyle : str
            Any of ['solid' | 'dashed', 'dashdot', 'dotted' |
            '-' | '--' | '-.' | ':' | 'None' | ' ' | '']

        linewidth : float, optional
            Float value in points.
        """
        supported_linestyles = ['solid', 'dashed', 'dashdot', 'dotted',
                                '-', '--', '-.', ':', 'None', ' ', '']
        kwargs = {}
        if color is not None:
            kwargs['color'] = color
        if linestyle is not None and linestyle in supported_linestyles:
            kwargs['linestyle'] = linestyle
        if linewidth is not None and isinstance(linewidth, (int, float)):
            kwargs['linewidth'] = linewidth
        self._axes.grid(b, which, axis, **kwargs)

    def set_axis(self, state):
        """Sets the axes frame/ticks/labels visibility on/off."""
        if state:
            self._axes.set_axis_on()
        else:
            self._axes.set_axis_off()

    def set_xlim(self, left=None, right=None):
        """
        Set the data limits for the x-axis.

        Examples
        --------
        >>> set_xlim((left, right))
        >>> set_xlim(left, right)
        >>> set_xlim(left=1)  # right unchanged
        >>> set_xlim(right=1)  # left unchanged
        """
        self._axes.set_xlim(left, right)

    def set_ylim(self, bottom=None, top=None):
        """
        Set the data limits for the y-axis.

        Examples
        --------
        >>> set_ylim((bottom, top))
        >>> set_ylim(bottom, top)
        >>> set_ylim(bottom=1)  # top unchanged
        >>> set_ylim(top=1)  # bottom unchanged
        """
        self._axes.set_ylim(bottom, top)

    def set_xticklabels(self, labels):
        """Set the x-tick labels with list of strings *labels*."""
        self._axes.set_xticklabels(labels)

    def set_yticklabels(self, labels):
        """Set the y-tick labels with list of strings *labels*."""
        self._axes.set_yticklabels(labels)

    def set_title(self, title, fontsize=None):
        """
        Set the title of the axes.

        Parameters
        ----------
        fontsize : int or float or str, optional
            Controls the font size of the legend. If given as string,
            following strings are possible {'xx-small', 'x-small',
            'small', 'medium', 'large', 'x-large', 'xx-large'}.
            If the value is numeric the size will be the absolute
            font size in points. String values are relative to the
            current default font size.
        """
        self._axes.set_title(title, fontsize=fontsize)

    def set_xlabel(self, label, fontsize=None):
        """
        Set the label for the x-axis.

        Parameters
        ----------
        fontsize : int or float or str, optional
            Controls the font size of the legend. If given as string,
            following strings are possible {'xx-small', 'x-small',
            'small', 'medium', 'large', 'x-large', 'xx-large'}.
            If the value is numeric the size will be the absolute
            font size in points. String values are relative to the
            current default font size.
        """
        self._axes.set_xlabel(label, fontsize=fontsize)

    def set_ylabel(self, label, fontsize=None):
        """
        Set the label for the y-axis.

        Parameters
        ----------
        fontsize : int or float or str, optional
            Controls the font size of the legend. If given as string,
            following strings are possible {'xx-small', 'x-small',
            'small', 'medium', 'large', 'x-large', 'xx-large'}.
            If the value is numeric the size will be the absolute
            font size in points. String values are relative to the
            current default font size.
        """
        self._axes.set_ylabel(label, fontsize=fontsize)

    def legend(self, handles=None, labels=None, loc='upper right',
               ncol=1, fontsize=None, frameon=None, title=None):
        """
        Places a legend on the axes.

        Parameters
        ----------
        handles : array_like, shape (n,)
            List of Artist handles.

        labels : array_like, shape (n,)
            List of Artist labels.

        loc : str or int, optional
            The location of the legend. See :ref:`location types`.
            Default is 'upper right'.

        ncol : int, optional
            The number of columns that the legend has. Default is 1.

        fontsize : int or float or str, optional
            Controls the font size of the legend. If given as string,
            following strings are possible {'xx-small', 'x-small',
            'small', 'medium', 'large', 'x-large', 'xx-large'}.
            If the value is numeric the size will be the absolute
            font size in points. String values are relative to the
            current default font size.

        frameon : bool or None, optional
            Controls whether a frame should be drawn around the
            legend. Default is None which will take the value from
            the legend.frameon rcParam.

        title : str or None, optional
            The legend's title. Default is no title (*None*).
        """
        kwargs = {}
        if handles is not None and labels is not None:
            kwargs['handles'] = handles
            kwargs['labels'] = labels
        if loc is not None:
            kwargs['loc'] = loc
        if ncol is not None:
            kwargs['ncol'] = ncol
        if fontsize is not None:
            kwargs['fontsize'] = fontsize
        if frameon is not None:
            kwargs['frameon'] = frameon
        if title is not None:
            kwargs['title'] = title
        self._axes.legend(**kwargs)

    def rotate_xlabels_if_date(self, ha='right', rotation=30):
        from matplotlib import dates
        axes = self.get_mpl_axes()
        if isinstance(axes.xaxis.get_major_locator(), dates.AutoDateLocator):
            for label in axes.get_xticklabels():
                label.set_ha(ha)
                label.set_rotation(rotation)
            return True
        return False

    def __eq__(self, other):
        if isinstance(other, SyAxes):
            return self._axes == other._axes
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result


class SyArtist(object):
    """Wrapper around matplotlib Artist."""

    def __init__(self, artist):
        self._artist = artist

    def get_mpl_artist(self):
        """Returns the underlying matplotlib Artist object.

        Warnings
        --------
           When using this function you will get access to the entire
           matplotlib API. That API is likely to change slightly over time
           completely outside of our control. If you want to be sure that the
           code you are writing continues to work as expected in upcoming
           versions of Sympathy you should not use this method.
        """
        return self._artist

    def __eq__(self, other):
        if isinstance(other, SyArtist):
            return self._artist == other._artist
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
