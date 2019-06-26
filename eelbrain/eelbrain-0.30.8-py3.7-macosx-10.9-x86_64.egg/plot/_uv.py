# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""Plot univariate data (:class:`~eelbrain.Var` objects)."""
from collections import Sequence

import logging

import numpy as np
import scipy.stats  # without this sp.stats is not available
import matplotlib as mpl
from matplotlib.artist import setp

from .._celltable import Celltable
from .._data_obj import asvar, ascategorial, assub, cellname
from .._stats import test, stats
from ._base import EelFigure, Layout, LegendMixin, YLimMixin, frame_title
from ._colors import find_cell_colors


defaults = dict(title_kwargs={'size': 14,
                                'family': 'serif'},
              mono=False,  # use monochrome instead of colors
              # defaults for color
              hatch=['', '', '//', '', '*', 'O', '.', '', '/', '//'],
              linestyle=['-', '-', '--', ':'],
              c={'pw': ['#00FF00', '#FFCC00', '#FF6600', '#FF3300'],
#                   'colors': ['.3', '.7', '1.', '1.'],
                   'colors': [(0.99609375, 0.12890625, 0.0),
                              (0.99609375, 0.5859375, 0.0),
                              (0.98046875, 0.99609375, 0.0),
                              (0.19921875, 0.99609375, 0.0)],
                   'markers': False,
                   },
              # defaults for monochrome
              cm={'pw': ['.6', '.4', '.2', '.0'],
                    'colors': ['.3', '.7', '1.', '1.'],
                    'markers': ['o', 'o', '^', 'o'],
                    },
                )  # set by __init__


def _mark_plot_pairwise(ax, ct, parametric, bottom, y_unit, corr, trend, markers,
                        levels=True, pwcolors=None, x0=0, top=None):
    """Mark pairwise significance

    Parameters
    ----------
    ax : Axes
        Axes to plot to.
    ct : Celltable
        Data for the tests.
    parametric : bool
        Whether to perform parametric tests.
    bottom : scalar
        Bottom of the space to use for the connectors (in data coordinates, i.e.
        highest point reached by the data plot).
    y_unit : scalar
        Suggested scale for half the vertical distance between connectors (only used
        if top is None).
    corr : None | 'hochberg' | 'bonferroni' | 'holm'
        Method for multiple comparison correction.
    trend : None | str
        Symbol to mark trends.
    markers : bool
        Plot markers indicating significance level (stars).
    ...
    top : scalar
        Impose a fixed top end of the y-axis.

    Returns
    -------
    top : scalar
        The top most value on the y axis.
    """
    if levels is not True:  # to avoid test.star() conflict
        trend = False

    # visual parameters
    if not pwcolors:
        if defaults['mono']:
            pwcolors = defaults['cm']['pw'][1 - bool(trend):]
        else:
            pwcolors = defaults['c']['pw'][1 - bool(trend):]
    font_size = mpl.rcParams['font.size'] * 1.5

    tests = test._pairwise(ct.get_data(), ct.all_within, parametric, corr, levels,
                           trend)

    # plan grid layout
    k = len(ct.cells)
    reservation = np.zeros((sum(range(1, k)), k - 1))
    connections = []
    for distance in range(1, k):
        for i in range(0, k - distance):
            # i, j are data indexes for the categories being compared
            j = i + distance
            index = tests['pw_indexes'][(i, j)]
            stars = tests['stars'][index]
            if not stars:
                continue

            free_levels = np.flatnonzero(reservation[:, i:j].sum(1) == 0)
            level = free_levels.min()
            reservation[level, i:j] = 1
            connections.append((level, i, j, index, stars))

    # plan spatial distances
    used_levels = np.flatnonzero(reservation.sum(1))
    if len(used_levels) == 0:
        if top is None:
            return bottom + y_unit
        else:
            return top
    n_levels = used_levels.max() + 1
    n_steps = n_levels * 2 + 1 + bool(markers)
    if top is None:
        top = bottom + y_unit * n_steps
    else:
        y_unit = (top - bottom) / n_steps

    # draw connections
    for level, i, j, index, stars in connections:
        c = pwcolors[stars - 1]
        y1 = bottom + y_unit * (level * 2 + 1)
        y2 = y1 + y_unit
        x1 = (x0 + i) + .025
        x2 = (x0 + j) - .025
        ax.plot([x1, x1, x2, x2], [y1, y2, y2, y1], color=c)
        if markers:
            symbol = tests['symbols'][index]
            ax.text((x1 + x2) / 2, y2, symbol, color=c, size=font_size,
                    ha='center', va='center', clip_on=False)

    return top


def _mark_plot_1sample(ax, ct, par, y_min, y_unit, popmean=0, corr='Hochberg',
                       trend="'", levels=True, pwcolors=None, x0=0):
    """Mark significance for one-sample test

    Returns
    -------
    y_max : float
        Top of space used on y axis.
    """
    if levels is not True:  # to avoid test.star() conflict
        trend = False
    # tests
    if not pwcolors:
        if defaults['mono']:
            pwcolors = defaults['cm']['pw'][1 - bool(trend):]
        else:
            pwcolors = defaults['c']['pw'][1 - bool(trend):]
    # mod
    ps = []
    if par:
        for d in ct.get_data():
            t, p = scipy.stats.ttest_1samp(d, popmean)
            ps.append(p)
    else:
        raise NotImplementedError("nonparametric 1-sample test")
    ps_adjusted = test.mcp_adjust(ps, corr)
    stars = test.star(ps_adjusted, int, levels, trend)
    stars_str = test.star(ps_adjusted, str, levels, trend)
    font_size = mpl.rcParams['font.size'] * 1.5
    if any(stars):
        y_stars = y_min + 1.75 * y_unit
        for i, n_stars in enumerate(stars):
            if n_stars > 0:
                c = pwcolors[n_stars - 1]
                ax.text(x0 + i, y_stars, stars_str[i], color=c, size=font_size,
                        ha='center', va='center', clip_on=False)
        return y_min + 4. * y_unit
    else:
        return y_min


class PairwiseLegend(EelFigure):
    """Legend for colors used in pairwise comparisons

    Parameters
    ----------
    size : scalar
        Side length in inches of a virtual square containing each bar.
    trend : bool
        Also include a bar for trends (p<0.1). Default is True.
    ...
        Also accepts :ref:`general-layout-parameters`.
    """
    def __init__(self, size=.3, trend=True, *args, **kwargs):
        if trend:
            levels = [.1, .05, .01, .001]
            colors = defaults['c']['pw']
        else:
            levels = [.05, .01, .001]
            colors = defaults['c']['pw'][1:]

        # layout
        n_levels = len(levels)
        ax_h = n_levels * size
        y_unit = size / 5
        ax_aspect = 4 / n_levels
        layout = Layout(0, ax_aspect, ax_h, False, *args, **kwargs)
        EelFigure.__init__(self, None, layout)
        ax = self.figure.add_axes((0, 0, 1, 1), frameon=False)
        ax.set_axis_off()

        x1 = .1 * size
        x2 = .9 * size
        x = (x1, x1, x2, x2)
        x_text = 1.2 * size
        for i, level, color in zip(range(n_levels), levels, colors):
            y1 = y_unit * (i * 5 + 2)
            y2 = y1 + y_unit
            ax.plot(x, (y1, y2, y2, y1), color=color)
            label = "p<%s" % (str(level)[1:])
            ax.text(x_text, y1 + y_unit / 2, label, ha='left', va='center')

        ax.set_ylim(0, self._layout.h)
        ax.set_xlim(0, self._layout.w)
        self._show()


class _SimpleFigure(EelFigure):
    def __init__(self, data_desc, *args, **kwargs):
        layout = Layout(1, 1, 5, *args, **kwargs)
        EelFigure.__init__(self, data_desc, layout)
        self._ax = ax = self._axes[0]

        # remove x-axis ticks
        xax = ax.get_xaxis()
        xax.set_ticks_position('none')

        # collector for handles for figure legend
        self._handles = []
        self._legend = None

    def _set_xlabel_categorial(self, xlabel, model):
        if xlabel is True:
            if model and model.name:
                xlabel = model.name.replace('_', ' ')
            else:
                xlabel = False

        if xlabel:
            self._ax.set_xlabel(xlabel)

    def _show(self):
        if self._has_frame and not self._layout.w_fixed:
            # make sure x axis labels don't overlap
            self.draw()
            labels = self._ax.get_xticklabels()
            n = len(labels)
            if len(labels) > 1:
                bbs = [l.get_window_extent(self.figure.canvas.renderer) for l in labels]
                overlap = max(bbs[i].x1 - bbs[i + 1].x0 for i in range(n - 1))
                extend = n * (overlap + 10)
                w, h = self._frame.GetSize()
                w += int(extend)
                self._frame.SetSize((w, h))
        EelFigure._show(self)


class Boxplot(YLimMixin, _SimpleFigure):
    r"""Boxplot for a continuous variable

    Parameters
    ----------
    y : Var
        Dependent variable.
    x : categorial
        Category definition (draw one box for every cell in ``x``).
    match : None | categorial
        Match cases for a repeated measures design.
    sub : None | index-array
        Use a subset of the data.
    cells : None | sequence of cells of x
        Cells to plot (optional). All entries have to be cells of ``x``). Can be
        used to change the order of the bars or plot only certain cells.
    datalabels : scalar
        Threshold for labeling outliers (in standard-deviation).
    bottom : scalar
        Lowest possible value on the y axis (default is 0 or slightly
        below the lowest value).
    top : scalar
        Set the upper x axis limit (default is to fit all the data).
    ylabel : str | None
        Y axis label (default is inferred from the data).
    xlabel : str | bool
        X axis label (default is ``x.name``).
    xticks : None | sequence of str
        X-axis tick labels describing the categories. None to plot no labels
        (Default uses cell names from ``x``).
    xtick_delim : str
        Delimiter for x axis category descriptors (default is ``'\n'``,
        i.e. the level on each Factor of ``x`` on a separate line).
    titlekwargs : dict
        Keyword arguments for the figure title.
    test : bool | scalar
        True (default): perform pairwise tests;  False/None: no tests;
        scalar: 1-sample tests against this value.
    par : bool
        Use parametric test for pairwise comparisons (use non-parametric
        tests if False).
    trend : None | str
        Marker for a trend in pairwise comparisons.
    test_markers : bool
        For pairwise tests, plot markers indicating significance level
        (stars).
    corr : None | 'hochberg' | 'bonferroni' | 'holm'
        Method for multiple comparison correction (default 'hochberg').
    hatch : bool | str
        Matplotlib Hatch pattern to fill boxes (True to use the module
        default; default is False).
    colors : bool | sequence | dict of matplitlib colors
        Matplotlib colors to use for boxes (True to use the module default;
        default is False, i.e. no colors).
    ds : None | Dataset
        If a Dataset is specified, all data-objects can be specified as
        names of Dataset variables
    frame : bool
        Draw a frame containing the figure from the top and the right
        (default ``True``).
    tight : bool
        Use matplotlib's tight_layout to resize all axes to fill the figure
        (default True).
    ...
        Also accepts :ref:`general-layout-parameters`.
    """
    def __init__(self, y, x=None, match=None, sub=None, cells=None, datalabels=None,
                 bottom=None, top=None, ylabel=True, xlabel=True,
                 xticks=True, xtick_delim='\n',
                 test=True, par=True, trend="'", test_markers=True, corr='Hochberg',
                 hatch=False, colors=False, ds=None, *args,
                 **kwargs):
        # get data
        ct = Celltable(y, x, match, sub, cells, ds, asvar)
        if ct.x is None and test is True:
            test = 0.

        # kwargs
        if hatch is True:
            hatch = defaults['hatch']

        if hatch and len(hatch) < ct.n_cells:
            raise ValueError(
                "hatch needs at least as many values as there are cells (%i) "
                "got %r" % (ct.n_cells, hatch))

        if colors is True:
            if defaults['mono']:
                colors = defaults['cm']['colors']
            else:
                colors = defaults['c']['colors']
        elif isinstance(colors, dict):
            colors = [colors[cell] for cell in ct.cells]

        if colors and len(colors) < ct.n_cells:
            raise ValueError(
                "colors needs at least as many values as there are cells (%i) "
                "got %r" % (ct.n_cells, colors))

        _SimpleFigure.__init__(self, frame_title(ct.y, ct.x), *args, **kwargs)
        self._set_xlabel_categorial(xlabel, ct.x)
        self._configure_yaxis(ct.y, ylabel)

        p = _plt_boxplot(self._ax, ct, colors, hatch, bottom, top, xticks,
                         xtick_delim, test, par, corr, trend, test_markers,
                         datalabels)
        p.set_ylim(p.bottom, p.top)
        p.ax.set_xlim(p.left, p.right)
        if p.top > 0 > p.bottom:
            p.ax.axhline(0, color='k')

        YLimMixin.__init__(self, (p,))
        self._show()


class Barplot(YLimMixin, _SimpleFigure):
    r"""Barplot for a continuous variable

    Parameters
    ----------
    Y : Var
        Dependent variable.
    x : categorial
        Model (Factor or Interaction).
    match : None | categorial
        Match cases for a repeated measures design.
    sub : None | index-array
        Use a subset of the data.
    cells : None | sequence of cells of x
        Cells to plot (optional). All entries have to be cells of ``x``). Can be
        used to change the order of the bars or plot only certain cells.
    test : bool | scalar
        True (default): perform pairwise tests;  False: no tests;
        scalar: 1-sample tests against this value
    par : bool
        Use parametric test for pairwise comparisons (use non-parametric
        tests if False).
    corr : None | 'hochberg' | 'bonferroni' | 'holm'
        Method for multiple comparison correction (default 'hochberg').
    trend : None | str
        Marker for a trend in pairwise comparisons.
    test_markers : bool
        For pairwise tests, plot markers indicating significance level
        (stars).
    ylabel : str | None
        Y axis label (default is inferred from the data).
    error : str
        Measure of variability to display in the error bars (default: 1
        SEM). Examples:
        'ci': 95% confidence interval;
        '99%ci': 99% confidence interval (default);
        '2sem': 2 standard error of the mean.
    pool_error : bool
        Pool the errors for the estimate of variability (default is True
        for related measures designs, False for others). See Loftus & Masson
        (1994).
    ec : matplotlib color
        Error bar color.
    xlabel : str | bool
        X axis label (default is ``x.name``).
    xticks : None | sequence of str
        X-axis tick labels describing the categories. None to plot no labels
        (Default uses cell names from ``x``).
    xtick_delim : str
        Delimiter for x axis category descriptors (default is ``'\n'``,
        i.e. the level on each Factor of ``x`` on a separate line).
    hatch : bool | str
        Matplotlib Hatch pattern to fill boxes (True to use the module
        default; default is False).
    colors : bool | dict | sequence of matplitlib colors
        Matplotlib colors to use for boxes (True to use the module default;
        default is False, i.e. no colors).
    bottom : scalar
        Lower end of the y axis (default is 0).
    top : scalar
        Upper end of the y axis (default is determined from the data).
    origin : scalar
        Origin of the bars on the y-axis (the default is ``max(bottom, 0)``)
    c : matplotlib color
        Bar color (ignored if colors is specified).
    edgec : matplotlib color
        Barplot edge color.
    ds : None | Dataset
        If a Dataset is specified, all data-objects can be specified as
        names of Dataset variables
    frame : bool
        Draw a frame containing the figure from the top and the right
        (default ``True``).
    tight : bool
        Use matplotlib's tight_layout to resize all axes to fill the figure
        (default True).
    ...
        Also accepts :ref:`general-layout-parameters`.
    """
    def __init__(self, y, x=None, match=None, sub=None, cells=None, test=True, par=True,
                 corr='Hochberg', trend="'", test_markers=True, ylabel=True,
                 error='sem', pool_error=None, ec='k', xlabel=True, xticks=True,
                 xtick_delim='\n', hatch=False, colors=False, bottom=0, top=None,
                 origin=None, c='#0099FF', edgec=None, ds=None, *args, **kwargs):
        ct = Celltable(y, x, match, sub, cells, ds, asvar)

        if pool_error is None:
            pool_error = ct.all_within

        _SimpleFigure.__init__(self, frame_title(ct.y, ct.x), *args, **kwargs)
        self._set_xlabel_categorial(xlabel, ct.x)
        self._configure_yaxis(ct.y, ylabel)

        p = _plt_barplot(self._ax, ct, error, pool_error, hatch, colors,
                         bottom, top, origin, None, .5, c, edgec, ec, test, par,
                         trend, corr, test_markers, xticks, xtick_delim)
        p.set_ylim(p.bottom, p.top)
        p.ax.set_xlim(p.left, p.right)
        if p.top > 0 > p.bottom:
            p.ax.axhline(0, color='k')

        YLimMixin.__init__(self, (p,))
        self._show()


class _plt_uv_base:
    """Base for barplot and boxplot"""

    def __init__(self, ax, ct, xticks, xtick_delim):
        # figure decoration
        if xticks:
            if xticks is True:
                xticks = ct.cellnames(xtick_delim)
            ax.set_xticklabels(xticks)
            ax.set_xticks(np.arange(len(ct.cells)))
        elif xticks is False:
            ax.set_xticks(())

        self.vmin, self.vmax = ax.get_ylim()
        self.ax = ax

    def set_ylim(self, bottom, top):
        self.ax.set_ylim(bottom, top)
        self.vmin, self.vmax = self.ax.get_ylim()


class _plt_boxplot(_plt_uv_base):
    """Boxplot"""

    def __init__(self, ax, ct, colors, hatch, bottom, top, xticks, xtick_delim,
                 test, par, corr, trend, test_markers, datalabels):
        # determine ax lim
        if bottom is None:
            if np.min(ct.y.x) >= 0:
                bottom = 0
            else:
                d_min = np.min(ct.y.x)
                d_max = np.max(ct.y.x)
                d_range = d_max - d_min
                bottom = d_min - .05 * d_range

        # boxplot
        k = len(ct.cells)
        all_data = ct.get_data()
        bp = ax.boxplot(all_data, positions=np.arange(k))

        # Now fill the boxes with desired colors
        if hatch or colors:
            for i in range(ct.n_cells):
                box = bp['boxes'][i]
                box_x = box.get_xdata()[:5]  # []
                box_y = box.get_ydata()[:5]  # []
                box_coords = list(zip(box_x, box_y))
                if colors:
                    c = colors[i]
                else:
                    c = '.5'

                if hatch:
                    h = hatch[i]
                else:
                    h = ''

                poly = mpl.patches.Polygon(box_coords, facecolor=c, hatch=h, zorder=-999)
                ax.add_patch(poly)
        if defaults['mono']:
            for itemname in bp:
                bp[itemname].set_color('black')

        # tests
        y_min = max(x.max() for x in all_data)
        y_unit = (y_min - bottom) / 15
        if test is True:
            y_top = _mark_plot_pairwise(ax, ct, par, y_min, y_unit, corr, trend, test_markers)
        elif test is not False and test is not None:
            ax.axhline(test, color='black')
            y_top = _mark_plot_1sample(ax, ct, par, y_min, y_unit, test, corr, trend, x0=1)
        else:
            ax.autoscale()
            y_top = None

        if top is None:
            top = y_top

        # data labels
        if datalabels:
            for i, cell in enumerate(ct.cells):
                d = ct.data[cell]
                indexes = np.where(np.abs(d) / d.std() >= datalabels)[0]
                for index in indexes:
                    label = ct.matchlabels[cell][index]
                    ax.annotate(label, (i + 1, d[index]))

        # set ax limits
        self.left = -.5
        self.right = k - .5
        self.bottom = bottom
        self.top = ax.get_ylim()[1] if top is None else top
        _plt_uv_base.__init__(self, ax, ct, xticks, xtick_delim)


class _plt_barplot(_plt_uv_base):
    """Draw a barplot to axes ax for Celltable ct.

    Parameters
    ----------
    ax : mpl Axes
        Axes to which to plot
    ct : Celltable
        Data to plot.
    error : str
        Variability description (e.g., "95%ci").
    pool_error : bool
        Pool the errors for the estimate of variability.
    ...
    """
    def __init__(self, ax, ct, error, pool_error, hatch, colors, bottom, top=None,
                 origin=None, left=None, width=.5, c='#0099FF', edgec=None,
                 ec='k', test=True, par=True, trend="'", corr='Hochberg',
                 test_markers=True, xticks=None, xtick_delim=None):
        # kwargs
        if hatch is True:
            hatch = defaults['hatch']

        if colors is True:
            if defaults['mono']:
                colors = defaults['cm']['colors']
            else:
                colors = defaults['c']['colors']
        elif isinstance(colors, dict):
            colors = [colors[cell] for cell in ct.cells]

        # data means
        k = len(ct.cells)
        if left is None:
            left = np.arange(k) - width / 2
        height = np.array(ct.get_statistic(np.mean))

        # origin
        if origin is None:
            origin = max(0, bottom)

        # error bars
        if ct.x is None:
            error_match = None
        else:
            error_match = ct.match
        y_error = stats.variability(ct.y.x, ct.x, error_match, error, pool_error, ct.cells)

        # fig spacing
        plot_max = np.max(height + y_error)
        plot_min = np.min(height - y_error)
        plot_span = plot_max - plot_min
        y_bottom = min(bottom, plot_min - plot_span * .05)

        # main BARPLOT
        bars = ax.bar(left, height - origin, width, bottom=origin, align='edge',
                      color=c, edgecolor=edgec, ecolor=ec, yerr=y_error)

        # hatch
        if hatch:
            for bar, h in zip(bars, hatch):
                bar.set_hatch(h)
        if colors:
            for bar, c in zip(bars, colors):
                bar.set_facecolor(c)

        # pairwise tests
        if ct.x is None and test is True:
            test = 0.
        y_unit = (plot_max - y_bottom) / 15
        if test is True:
            y_top = _mark_plot_pairwise(ax, ct, par, plot_max, y_unit, corr, trend,
                                        test_markers, top=top)
        elif (test is False) or (test is None):
            y_top = plot_max + y_unit
        else:
            ax.axhline(test, color='black')
            y_top = _mark_plot_1sample(ax, ct, par, plot_max, y_unit, test, corr, trend)

        self.left = min(left) - .5 * width
        self.right = max(left) + 1.5 * width
        self.bottom = y_bottom
        self.top = y_top if top is None else top
        _plt_uv_base.__init__(self, ax, ct, xticks, xtick_delim)


class Timeplot(LegendMixin, YLimMixin, EelFigure):
    """Plot a variable over time

    Parameters
    ----------
    y : Var
        Dependent variable.
    categories : categorial
        Model (Factor or Interaction)
    time : Var
        Variable describing the time.
    match : None | categorial
        Match cases for a repeated measures design.
    sub : None | index-array
        Use a subset of the data.
    ds : None | Dataset
        If a Dataset is specified, all data-objects can be specified as
        names of Dataset variables
    main : numpy function
        draw lines to connect values across time (default: np.mean).
        Can be 'bar' for barplots or False.
    error : str | False
        How to indicate estimate error. For complete within-subject designs,
        the within-subject measures are displayed (see Loftus & Masson, 1994).
        Options:
        'box': boxplots;
        '[x]sem': x standard error of the means (e.g. 'sem', '2sem');
        '[x]std': x standard deviations.
    x_jitter : bool
        When plotting error bars, jitter their location on the x-axis to
        increase readability.
    bottom : scalar
        Lower end of the y axis (default is 0).
    top : scalar
        Upper end of the y axis (default is determined from the data).
    ylabel : str | None
        y axis label (default is inferred from the data).
    xlabel : str | bool
        x axis label (default is inferred from the data).
    timelabels : sequence | dict | 'all'
        Labels for the x (time) axis. Exact labels can be specified in the form 
        of a list of labels corresponsing to all unique values of ``time``, or a 
        ``{time_value: label}`` dictionary. For 'all', all values of ``time`` 
        are marked. The default is normal matplotlib ticks.
    legend : str | int | 'fig' | None
        Matplotlib figure legend location argument or 'fig' to plot the
        legend in a separate figure.
    labels : dict
        Alternative labels for legend as ``{cell: label}`` dictionary (preserves
        order).
    colors : str | list | dict
        Colors for the categories.
        **str**: A colormap name; cells are mapped onto the colormap in
        regular intervals.
        **list**: A list of colors in the same sequence as the cells.
        **dict**: A dictionary mapping each cell to a color.
        Colors are specified as `matplotlib compatible color arguments
        <http://matplotlib.org/api/colors_api.html>`_.
    frame : bool
        Draw a frame containing the figure from the top and the right
        (default ``True``).
    tight : bool
        Use matplotlib's tight_layout to resize all axes to fill the figure
        (default True).
    ...
        Also accepts :ref:`general-layout-parameters`.
    """
    def __init__(self, y, categories, time, match=None, sub=None, ds=None,
                 # data plotting
                 main=np.mean, error='sem', x_jitter=False,
                 bottom=None, top=None,
                 # labelling
                 ylabel=True, xlabel=True, timelabels=None, legend='upper right',
                 labels=None,
                 colors=None, hatch=False, markers=True, *args, **kwargs):
        if 'spread' in kwargs:  # deprecated 0.27
            raise ValueError("The `spread` argument has been removed from "
                             "plot.Timeplot. Use the `error` argument instead")
        sub = assub(sub, ds)
        y = asvar(y, sub, ds)
        categories = ascategorial(categories, sub, ds)
        time = asvar(time, sub, ds)
        if match is not None:
            match = ascategorial(match, sub, ds)

        # transform to 3 kwargs:
        # - local_plot ('bar' or 'box')
        # - line_plot (function for values to connect)
        # - error
        if main == 'bar':
            assert error != 'box'
            local_plot = 'bar'
            line_plot = None
        else:
            line_plot = main
            if error == 'box':
                local_plot = 'box'
                error = None
            else:
                local_plot = None

        if not line_plot:
            legend = False

        # hatch/marker
        if hatch is True:
            hatch = defaults['hatch']
        if markers is True:
            if defaults['mono']:
                markers = defaults['cm']['markers']
            else:
                markers = defaults['c']['markers']

        # colors: {category index -> color, ...}
        colors = find_cell_colors(categories, colors)

        # get axes
        layout = Layout(1, 1, 5, *args, **kwargs)
        EelFigure.__init__(self, frame_title(y, categories), layout)
        self._configure_yaxis(y, ylabel)
        self._configure_xaxis(time, xlabel)

        plot = _ax_timeplot(self._axes[0], y, categories, time, match, colors,
                            hatch, markers, line_plot, error, local_plot,
                            timelabels, x_jitter, bottom, top)

        YLimMixin.__init__(self, (plot,))
        LegendMixin.__init__(self, legend, plot.legend_handles, labels)
        self._show()

    def _fill_toolbar(self, tb):
        LegendMixin._fill_toolbar(self, tb)


class _ax_timeplot:

    def __init__(self, ax, y, categories, time, match, colors, hatch, markers,
                 line_plot, error, local_plot, timelabels, x_jitter, bottom,
                 top):
        color_list = [colors[i] for i in categories.cells]
        # categories
        n_cat = len(categories.cells)
        # find time points
        time_points = np.unique(time.x)
        # n_time_points = len(time_points)
        # determine whether spread can be plotted
        celltables = [Celltable(y, categories, match=match, sub=(time == t)) for
                      t in time_points]
        line_values = np.array([ct.get_statistic(line_plot) for ct in celltables]).T
        # all_within = all(ct.all_within for ct in celltables)
        if error and all(ct.n_cases > ct.n_cells for ct in celltables):
            spread_values = np.array([ct.variability(error) for ct in celltables]).T
        else:
            error = spread_values = False

        time_step = min(np.diff(time_points))
        if local_plot in ['box', 'bar']:
            within_spacing = time_step / (2 * n_cat)
            padding = (2 + n_cat / 2) * within_spacing
        else:
            within_spacing = time_step / (8 * n_cat)
            padding = time_step / 4  # (2 + n_cat/2) * within_spacing

        rel_pos = np.arange(0, n_cat * within_spacing, within_spacing)
        rel_pos -= np.mean(rel_pos)

        t_min = min(time_points) - padding
        t_max = max(time_points) + padding

        # local plots
        for t, ct in zip(time_points, celltables):
            pos = rel_pos + t
            if local_plot == 'box':
                # boxplot
                bp = ax.boxplot(ct.get_data(out=list), positions=pos, widths=within_spacing)
                # make outlines black
                for lines in bp.values():
                    setp(lines, color='black')
                # Now fill the boxes with desired colors
                for i, cell in enumerate(ct.cells):
                    box = bp['boxes'][i]
                    box_x = box.get_xdata()[:5]
                    box_y = box.get_ydata()[:5]
                    patch = mpl.patches.Polygon(
                        zip(box_x, box_y),
                        facecolor=colors[cell],
                        hatch=hatch[i] if hatch else '',
                        zorder=-999)
                    ax.add_patch(patch)
            elif local_plot == 'bar':
                _plt_barplot(ax, ct, error, False, hatch, color_list, 0, left=pos,
                             width=within_spacing, test=False)

        legend_handles = {}
        if line_plot:
            # plot means
            x = time_points
            for i, cell in enumerate(categories.cells):
                y = line_values[i]
                name = cellname(cell)
                color = colors[cell]

                if hatch:
                    ls = defaults['linestyle'][i]
                    if color == '1.':
                        color = '0.'
                else:
                    ls = '-'

                if ls == '-':
                    mfc = color
                else:
                    mfc = '1.'

                if not markers or len(markers) <= i:
                    marker = None
                else:
                    marker = markers[i]

                handles = ax.plot(x, y, color=color, linestyle=ls, label=name,
                                  zorder=6, marker=marker, mfc=mfc)
                legend_handles[cell] = handles[0]

                if error:
                    if x_jitter:
                        x_errbars = x + rel_pos[i]
                    else:
                        x_errbars = x
                    ax.errorbar(x_errbars, y, yerr=spread_values[i], fmt='none',
                                zorder=5, ecolor=color, linestyle=ls, label=name)

        # x-ticks
        if timelabels is not None:
            if isinstance(timelabels, dict):
                locations = [t for t in time_points if t in timelabels]
                labels = [timelabels[t] for t in locations]
            elif isinstance(timelabels, str):
                if timelabels == 'all':
                    locations = time_points
                    labels = None
                else:
                    raise ValueError("timelabels=%r" % (timelabels,))
            elif (not isinstance(timelabels, Sequence) or
                  not len(timelabels) == len(time_points)):
                raise TypeError(
                    "timelabels needs to be a sequence whose length equals the "
                    "number of time points (%i); got %r" %
                    (len(time_points), timelabels))
            else:
                locations = time_points
                labels = [str(l) for l in timelabels]
            ax.set_xticks(locations)
            if labels is not None:
                ax.set_xticklabels(labels)

        # data-limits
        data_max = line_values.max()
        data_min = line_values.min()
        if error:
            max_spread = max(spread_values.max(), -spread_values.min())
            data_max += max_spread
            data_min -= max_spread
        pad = (data_max - data_min) / 20.
        if bottom is None:
            bottom = data_min - pad
        if top is None:
            top = data_max + pad

        # finalize
        ax.set_xlim(t_min, t_max)
        self.ax = ax
        self.legend_handles = legend_handles
        self.set_ylim(bottom, top)

    def set_ylim(self, vmin, vmax):
        self.ax.set_ylim(vmin, vmax)
        self.vmin, self.vmax = self.ax.get_ylim()


def _reg_line(y, reg):
    coeff = np.hstack([np.ones((len(reg), 1)), reg[:, None]])
    (a, b), residues, rank, s = np.linalg.lstsq(coeff, y)
    regline_x = np.array([min(reg), max(reg)])
    regline_y = a + b * regline_x
    return regline_x, regline_y


class Correlation(EelFigure, LegendMixin):
    """Plot the correlation between two variables

    Parameters
    ----------
    y : Var
        Variable for the y-axis.
    x : Var
        Variable for the x-axis.
    cat : categorial
        Plot the correlation separately for different categories.
    sub : None | index-array
        Use a subset of the data.
    ds : None | Dataset
        If a Dataset is specified, all data-objects can be specified as
        names of Dataset variables
    c : list
        List of colors for cells.
    legend : str | int | 'fig' | None
        Matplotlib figure legend location argument or 'fig' to plot the
        legend in a separate figure.
    labels : dict
        Alternative labels for legend as ``{cell: label}`` dictionary (preserves
        order).
    xlabel, ylabel : str
        Label for the x- and y-axis (default based on data).
    tight : bool
        Use matplotlib's tight_layout to expand all axes to fill the figure
        (default True)
    ...
        Also accepts :ref:`general-layout-parameters`.
    """
    def __init__(self, y, x, cat=None, sub=None, ds=None,
                 c=['b', 'r', 'k', 'c', 'm', 'y', 'g'], legend='upper right',
                 labels=None, xlabel=True, ylabel=True, *args, **kwargs):
        sub, n = assub(sub, ds, return_n=True)
        y, n = asvar(y, sub, ds, n, return_n=True)
        x = asvar(x, sub, ds, n)
        if cat is not None:
            cat = ascategorial(cat, sub, ds, n)

        # figure
        layout = Layout(1, 1, 5, *args, autoscale=True, **kwargs)
        EelFigure.__init__(self, frame_title(y, x, cat), layout)
        self._configure_yaxis(y, ylabel)
        self._configure_xaxis(x, xlabel)

        ax = self._axes[0]
        legend_handles = {}
        if cat is None:
            legend = False
            ax.scatter(x.x, y.x, alpha=.5)
        else:
            for color, cell in zip(c, cat.cells):
                idx = (cat == cell)
                label = cellname(cell)
                h = ax.scatter(x[idx].x, y[idx].x, c=color, label=label, alpha=.5)
                legend_handles[label] = h

        LegendMixin.__init__(self, legend, legend_handles, labels)
        self._show()

    def _fill_toolbar(self, tb):
        LegendMixin._fill_toolbar(self, tb)


class Regression(EelFigure, LegendMixin):
    """Plot the regression of ``y`` on ``x``

    parameters
    ----------
    y : Var
        Variable for the y-axis.
    x : Var
        Variable for the x-axis.
    cat : categorial
        Plot the regression separately for different categories.
    match : None | categorial
        Match cases for a repeated measures design.
    sub : None | index-array
        Use a subset of the data.
    ds : None | Dataset
        If a Dataset is specified, all data-objects can be specified as
        names of Dataset variables
    ylabel : str
        Y-axis label (default is ``y.name``).
    alpha : scalar
        alpha for individual data points (to control visualization of
        overlap)
    legend : str | int | 'fig' | None
        Matplotlib figure legend location argument or 'fig' to plot the
        legend in a separate figure.
    labels : dict
        Alternative labels for legend as ``{cell: label}`` dictionary (preserves
        order).
    c : color | sequence of colors
        Colors.
    tight : bool
        Use matplotlib's tight_layout to expand all axes to fill the figure
        (default True)
    ...
        Also accepts :ref:`general-layout-parameters`.
    """
    def __init__(self, y, x, cat=None, match=None, sub=None, ds=None,
                 xlabel=True, ylabel=True, alpha=.2, legend='upper right', labels=None,
                 c=['#009CFF', '#FF7D26', '#54AF3A', '#FE58C6', '#20F2C3'],
                 *args, **kwargs):
        sub, n = assub(sub, ds, return_n=True)
        y, n = asvar(y, sub, ds, n, return_n=True)
        x = asvar(x, sub, ds, n)
        if cat is not None:
            cat = ascategorial(cat, sub, ds, n)
        if match is not None:
            raise NotImplementedError("match kwarg")

        if ylabel is True:
            ylabel = y.name

        # figure
        layout = Layout(1, 1, 5, *args, autoscale=True, **kwargs)
        EelFigure.__init__(self, frame_title(y, x, cat), layout)
        self._configure_xaxis(x, xlabel)
        self._configure_yaxis(y, ylabel)

        ax = self._axes[0]
        legend_handles = {}
        if cat is None:
            legend = False
            if type(c) in [list, tuple]:
                color = c[0]
            else:
                color = c
            ax.scatter(x.x, y.x, edgecolor=color, facecolor=color, s=100,
                       alpha=alpha, marker='o', label='_nolegend_')
            reg_x, reg_y = _reg_line(y.x, x.x)
            ax.plot(reg_x, reg_y, c=color)
        else:
            for i, cell in enumerate(cat.cells):
                idx = (cat == cell)
                # scatter
                y_i = y.x[idx]
                x_i = x.x[idx]
                color = c[i % len(c)]
                h = ax.scatter(x_i, y_i, edgecolor=color, facecolor=color, s=100,
                               alpha=alpha, marker='o', label='_nolegend_')
                legend_handles[cell] = h
                # regression line
                reg_x, reg_y = _reg_line(y_i, x_i)
                ax.plot(reg_x, reg_y, c=color, label=cellname(cell))

        LegendMixin.__init__(self, legend, legend_handles, labels)
        self._show()

    def _fill_toolbar(self, tb):
        LegendMixin._fill_toolbar(self, tb)


# MARK: Requirements for Statistical Tests

def _difference(data, names):
    "Data condition x subject"
    data_differences = []; diffnames = []; diffnames_2lines = []
    for i, (name1, data1) in enumerate(zip(names, data)):
        for name2, data2 in zip(names[i + 1:], data[i + 1:]):
            data_differences.append(data1 - data2)
            diffnames.append('-'.join([name1, name2]))
            diffnames_2lines.append('-\n'.join([name1, name2]))
    return data_differences, diffnames, diffnames_2lines


def _ax_histogram(ax, data, density, test_normality, **kwargs):
    """Create normality test figure"""
    n, bins, patches = ax.hist(data, density=density, **kwargs)

    if test_normality:
        # normal line
        mu = np.mean(data)
        sigma = np.std(data)
        y = scipy.stats.norm.pdf(bins, mu, sigma)
        if not density:
            y *= len(data) * np.diff(bins)[0]
        ax.plot(bins, y, 'r--', linewidth=1)

        # TESTS
        # test Anderson
        a2, thresh, sig = scipy.stats.morestats.anderson(data)
        index = sum(a2 >= thresh)
        if index > 0:
            ax.text(.95, .95, '$^{*}%s$' % str(sig[index - 1] / 100), color='r', size=11,
                    horizontalalignment='right',
                    verticalalignment='top',
                    transform=ax.transAxes,)
        logging.debug(" Anderson: %s, %s, %s" % (a2, thresh, sig))
        # test Lilliefors
        n_test = test.lilliefors(data)
        ax.set_xlabel(r"$D=%.3f$, $p_{est}=%.2f$" % n_test)  # \chi ^{2}

    # finalize axes
    ax.autoscale()


class Histogram(EelFigure):
    """
    Histogram plots with tests of normality

    Parameters
    ----------
    Y : Var
        Dependent variable.
    x : categorial
        Categories for separate histograms.
    match : None | categorial
        Match cases for a repeated measures design.
    sub : None | index-array
        Use a subset of the data.
    ds : None | Dataset
        If a Dataset is specified, all data-objects can be specified as
        names of Dataset variables
    pooled : bool
        Add one plot with all values/differences pooled.
    density : bool
        Norm counts to approximate a probability density (default False).
    test : bool
        Test for normality.
    tight : bool
        Use matplotlib's tight_layout to expand all axes to fill the figure
        (default True)
    ...
        Also accepts :ref:`general-layout-parameters`.
    """
    def __init__(self, y, x=None, match=None, sub=None, ds=None, pooled=True,
                 density=False, test=False, tight=True, title=None, xlabel=True,
                 *args, **kwargs):
        ct = Celltable(y, x, match=match, sub=sub, ds=ds, coercion=asvar)

        # layout
        if x is None:
            nax = 1
            if title is True:
                title = "Test for Normality" if test else "Histogram"
        elif ct.all_within:
            n_comp = len(ct.cells) - 1
            nax = n_comp ** 2
            kwargs['nrow'] = n_comp
            kwargs['ncol'] = n_comp
            self._make_axes = False
            self._default_ylabel_ax = -1
            if title is True:
                title = ("Tests for Normality of the Differences" if test else
                         "Histogram of Pairwise Difference")
        else:
            nax = len(ct.cells)
            if title is True:
                title = "Tests for Normality" if test else "Histogram"

        layout = Layout(nax, 1, 3, tight, title, *args, **kwargs)
        EelFigure.__init__(self, frame_title(ct.y, ct.x), layout)

        if x is None:
            _ax_histogram(self._axes[0], ct.y.x, density, test)
        elif ct.all_within:  # distribution of differences
            data = [v.x for v in ct.get_data()]
            names = ct.cellnames()

            pooled_data = []
            # i: row
            # j: -column
            for i in range(n_comp + 1):
                for j in range(i + 1, n_comp + 1):
                    difference = data[i] - data[j]
                    pooled_data.append(difference)
                    ax_i = n_comp * i + (n_comp + 1 - j)
                    ax = self.figure.add_subplot(n_comp, n_comp, ax_i)
                    self._axes.append(ax)
                    _ax_histogram(ax, difference, density, test)
                    if i == 0:
                        ax.set_title(names[j], size=12)
                    if j == n_comp:
                        ax.set_ylabel(names[i], size=12)
            pooled_data = np.hstack(pooled_data)
            # pooled diffs
            if pooled and len(names) > 2:
                ax = self.figure.add_subplot(n_comp, n_comp, n_comp ** 2)
                self._axes.append(ax)
                _ax_histogram(ax, pooled_data, density, test, facecolor='g')
                ax.set_title("Pooled Differences")
        else:  # independent measures
            for cell, ax in zip(ct.cells, self._axes):
                ax.set_title(cellname(cell))
                _ax_histogram(ax, ct.data[cell].x, density, test)

        if test:
            self.figure.text(.99, .01, "$^{*}$ Anderson and Darling test "
                             "thresholded at $[.15, .10, .05, .025, .01]$.",
                             color='r', verticalalignment='bottom',
                             horizontalalignment='right')
            xlabel = False  # xlabel is used for test result

        if density:
            self._configure_yaxis('p', 'probability density')
        else:
            self._configure_yaxis('n', 'count')
        self._configure_xaxis(ct.y, xlabel)
        self._show()


def boxcox_explore(y, params=[-1, -.5, 0, .5, 1], crange=False, ax=None, box=True):
    """
    Plot the distribution resulting from a Box-Cox transformation

    Parameters
    ----------
    y : array-like
        array containing data whose distribution is to be examined
    crange :
        correct range of transformed data
    ax :
        ax to plot to (``None`` creates a new figure)
    box :
        use Box-Cox family

    """
    if hasattr(y, 'x'):
        y = y.x
    else:
        y = np.ravel(y)

    if np.any(y == 0):
        raise ValueError("data contains 0")

    y = []
    for p in params:
        if p == 0:
            if box:
                xi = np.log(y)
            else:
                xi = np.log10(y)
                # xi = np.log1p(x)
        else:
            if box:
                xi = (y ** p - 1) / p
            else:
                xi = y ** p
        if crange:
            xi -= min(xi)
            xi /= max(xi)
        y.append(xi)

    if not ax:
        import matplotlib.pyplot as plt
        plt.figure()
        ax = plt.subplot(111)

    ax.boxplot(y)
    ax.set_xticks(np.arange(1, 1 + len(params)))
    ax.set_xticklabels(params)
    ax.set_xlabel("p")
    if crange:
        ax.set_ylabel("Value (Range Corrected)")
