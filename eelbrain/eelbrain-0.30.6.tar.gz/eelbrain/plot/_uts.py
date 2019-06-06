# -*- coding: utf-8 -*-
# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""Plot uniform time-series of one variable."""
import operator

import matplotlib as mpl
import numpy as np

from .._celltable import Celltable
from .._data_obj import ascategorial, asndvar, assub, cellname, longname
from .._stats import stats
from . import _base
from ._base import (
    EelFigure, PlotData, Layout,
    LegendMixin, YLimMixin, XAxisMixin, TimeSlicerEF, frame_title)
from ._colors import colors_for_oneway, find_cell_colors
from .._colorspaces import oneway_colors
from functools import reduce


class UTSStat(LegendMixin, XAxisMixin, YLimMixin, EelFigure):
    """
    Plot statistics for a one-dimensional NDVar

    Parameters
    ----------
    y : 1d-NDVar
        Dependent variable (one-dimensional NDVar).
    x : categorial or None
        Model: specification of conditions which should be plotted separately.
    xax : None | categorial
        Make separate axes for each category in this categorial model.
    match : Factor
        Identifier for repeated measures data.
    sub : None | index array
        Only use a subset of the data provided.
    ds : None | Dataset
        If a Dataset is specified, all data-objects can be specified as
        names of Dataset variables.
    main : func | None
        Measure for the central tendency (function that takes an ``axis``
        argument). The default is numpy.mean.
    error : None | str
        Measure of variability to plot (default: 1 SEM). Examples:
        'ci': 95% confidence interval;
        '99%ci': 99% confidence interval (default);
        '2sem': 2 standard error of the mean;
        'all': plot all traces.
    pool_error : bool
        Pool the errors for the estimate of variability (default is True
        for related measures designs, False otherwise). See Loftus & Masson
        (1994).
    legend : str | int | 'fig' | None
        Matplotlib figure legend location argument or 'fig' to plot the
        legend in a separate figure.
    labels : dict
        Alternative labels for legend as ``{cell: label}`` dictionary (preserves
        order).
    axtitle : bool | sequence of str
        Title for the individual axes. The default is to show the names of the
        epochs, but only if multiple axes are plotted.
    xlabel : bool | str
        X-axis label. By default the label is inferred from the data.
    ylabel : bool | str
        Y-axis label. By default the label is inferred from the data.
    xticklabels : bool | int | list of int
        Specify which axes should be annotated with x-axis tick labels.
        Use ``int`` for a single axis (default ``-1``), a sequence of
        ``int`` for multiple specific axes, or ``bool`` for all/none.
    invy : bool
        Invert the y axis (if ``bottom`` and/or ``top`` are specified explicitly
        they take precedence; an inverted y-axis can also be produced by
        specifying ``bottom > top``).
    bottom, top | None | scalar
        Set an absolute range for the plot's y axis.
    hline : None | scalar | (value, kwarg-dict) tuple
        Add a horizontal line to each plot. If provided as a tuple, the second
        element can include any keyword arguments that should be submitted to
        the call to matplotlib axhline call.
    xdim : str
        dimension for the x-axis (default is 'time')
    xlim : scalar | (scalar, scalar)
        Initial x-axis view limits as ``(left, right)`` tuple or as ``length``
        scalar (default is the full x-axis in the data).
    clip : bool
        Clip lines outside of axes (the default depends on whether ``frame`` is
        closed or open).
    color : matplotlib color
        Color if just a single category of data is plotted.
    colors : str | list | dict
        Colors for the plots if multiple categories of data are plotted.
        **str**: A colormap name; Cells of ``x`` are mapped onto the colormap in
        regular intervals.
        **list**: A list of colors in the same sequence as ``x.cells``.
        **dict**: A dictionary mapping each cell in ``x`` to a color.
        Colors are specified as `matplotlib compatible color arguments
        <http://matplotlib.org/api/colors_api.html>`_.
    error_alpha : float
        Alpha of the error plot (default 0.3).
    clusters : None | Dataset
        Clusters to add to the plots. The clusters should be provided as
        Dataset, as stored in test results' :py:attr:`.clusters`.
    pmax : scalar
        Maximum p-value of clusters to plot as solid.
    ptrend : scalar
        Maximum p-value of clusters to plot as trend.
    tight : bool
        Use matplotlib's tight_layout to expand all axes to fill the figure
        (default True)
    title : str | None
        Figure title.
    frame : bool | 't'
        How to frame the plots.
        ``True`` (default): normal matplotlib frame;
        ``False``: omit top and right lines;
        ``'t'``: draw spines at x=0 and y=0, common for ERPs.
    ...
        Also accepts :ref:`general-layout-parameters`.

    Notes
    -----
    Navigation:
     - ``↑``: scroll up
     - ``↓``: scroll down
     - ``r``: y-axis zoom in (reduce y-axis range)
     - ``c``: y-axis zoom out (increase y-axis range)
    """
    def __init__(self, y, x=None, xax=None, match=None, sub=None, ds=None,
                 main=np.mean, error='sem', pool_error=None, legend='upper right', labels=None,
                 axtitle=True, xlabel=True, ylabel=True, xticklabels=-1,
                 invy=False, bottom=None, top=None, hline=None, xdim='time',
                 xlim=None, clip=None, color='b', colors=None, error_alpha=0.3,
                 clusters=None, pmax=0.05, ptrend=0.1, *args, **kwargs):
        # coerce input variables
        sub, n = assub(sub, ds, return_n=True)
        y, n = asndvar(y, sub, ds, n, return_n=True)
        if x is not None:
            x = ascategorial(x, sub, ds, n)
        if xax is not None:
            xax = ascategorial(xax, sub, ds, n)
        if match is not None:
            match = ascategorial(match, sub, ds, n)

        if error and error != 'all' and \
                (pool_error or (pool_error is None and match is not None)):
            all_x = [i for i in (xax, x) if i is not None]
            if len(all_x) > 0:
                full_x = reduce(operator.mod, all_x)
                ct = Celltable(y, full_x, match)
                dev_data = stats.variability(ct.y.x, ct.x, ct.match, error, True)
                error = 'data'
            else:
                dev_data = None
        else:
            dev_data = None

        if xax is None:
            nax = 1
            ct = Celltable(y, x, match)
            if x is None:
                color_x = None
            else:
                color_x = ct.x
        else:
            ct = Celltable(y, xax)
            if x is None:
                color_x = None
                X_ = None
            else:
                Xct = Celltable(x, xax)
                color_x = Xct.y
            if match is not None:
                matchct = Celltable(match, xax)
            nax = len(ct.cells)

        # assemble colors
        if color_x is None:
            colors = {None: color}
        else:
            colors = find_cell_colors(color_x, colors)

        layout = Layout(nax, 2, 4, *args, autoscale='y', **kwargs)
        EelFigure.__init__(self, frame_title(y, x, xax), layout)
        if clip is None:
            clip = layout.frame is True

        # create plots
        self._plots = []
        legend_handles = {}
        if xax is None:
            p = _ax_uts_stat(self._axes[0], ct, colors, main, error, dev_data,
                             xdim, invy, bottom, top, hline, clusters,
                             pmax, ptrend, clip, error_alpha)
            self._plots.append(p)
            legend_handles.update(p.legend_handles)
            if len(ct) < 2:
                legend = False
        else:
            for i, ax, cell in zip(range(nax), self._axes, ct.cells):
                if x is not None:
                    X_ = Xct.data[cell]

                if match is not None:
                    match = matchct.data[cell]

                ct_ = Celltable(ct.data[cell], X_, match=match, coercion=asndvar)
                p = _ax_uts_stat(ax, ct_, colors, main, error, dev_data,
                                 xdim, invy, bottom, top, hline, clusters,
                                 pmax, ptrend, clip, error_alpha)
                self._plots.append(p)
                legend_handles.update(p.legend_handles)
            self._set_axtitle(axtitle, names=map(cellname, ct.cells))

        self._configure_yaxis(ct.y, ylabel)
        self._configure_xaxis_dim(ct.y.get_dim(xdim), xlabel, xticklabels)
        XAxisMixin._init_with_data(self, ((y,),), xdim, xlim)
        YLimMixin.__init__(self, self._plots)
        LegendMixin.__init__(self, legend, legend_handles, labels)
        self._update_ui_cluster_button()
        self._show()

    def _fill_toolbar(self, tb):
        from .._wxgui import wx

        btn = self._cluster_btn = wx.Button(tb, wx.ID_ABOUT, "Clusters")
        btn.Enable(False)
        tb.AddControl(btn)
        btn.Bind(wx.EVT_BUTTON, self._OnShowClusterInfo)

        LegendMixin._fill_toolbar(self, tb)

    def _OnShowClusterInfo(self, event):
        from .._wxgui import show_text_dialog

        if len(self._plots) == 1:
            clusters = self._plots[0].cluster_plt.clusters
            all_plots_same = True
        else:
            all_clusters = [p.cluster_plt.clusters is None for p in self._plots]
            clusters = all_clusters[0]
            if all(c is clusters for c in all_clusters[1:]):
                all_plots_same = True
            else:
                all_plots_same = False

        if all_plots_same:
            info = str(clusters)
        else:
            info = []
            for i, clusters in enumerate(all_clusters):
                if clusters is None:
                    continue
                title = "Axes %i" % i
                info.append(title)
                info.append('\n')
                info.append('-' * len(title))
                info.append(str(clusters))
            info = '\n'.join(info)

        show_text_dialog(self._frame, info, "Clusters")

    def _update_ui_cluster_button(self):
        if hasattr(self, '_cluster_btn'):
            enable = not all(p.cluster_plt.clusters is None for p in self._plots)
            self._cluster_btn.Enable(enable)

    def set_clusters(self, clusters, pmax=0.05, ptrend=None, color='.7', ax=None, y=None, dy=None):
        """Add clusters from a cluster test to the plot (as shaded area).

        Parameters
        ----------
        clusters : None | Dataset
            The clusters, as stored in test results' :py:attr:`.clusters`.
            Use ``None`` to remove the clusters plotted on a given axis.
        pmax : scalar
            Only plot clusters with ``p <= pmax``.
        ptrend : scalar
            Maximum p-value of clusters to plot as trend.
        color : matplotlib color | dict
            Color for the clusters, or a ``{effect: color}`` dict.
        ax : None | int
            Index of the axes to which the clusters are to be added. If None,
            add the clusters to all axes.
        y : scalar | dict
            Y level at which to plot clusters (default is boxes spanning the
            whole y-axis).
        dy : scalar
            Height of bars.
        """
        axes = range(len(self._axes)) if ax is None else [ax]

        # update plots
        for ax in axes:
            p = self._plots[ax].cluster_plt
            p.set_clusters(clusters, False)
            p.set_color(color, False)
            p.set_y(y, dy, False)
            p.set_pmax(pmax, ptrend)
        self.draw()

        self._update_ui_cluster_button()


class UTS(TimeSlicerEF, LegendMixin, YLimMixin, XAxisMixin, EelFigure):
    """Value by time plot for UTS data

    Parameters
    ----------
    y : (list of) NDVar
        Uts data  to plot.
    xax : None | categorial
        Make separate axes for each category in this categorial model.
    axtitle : bool | sequence of str
        Title for the individual axes. The default is to show the names of the
        epochs, but only if multiple axes are plotted.
    ds : None | Dataset
        If a Dataset is specified, all data-objects can be specified as
        names of Dataset variables.
    sub : str | array
        Specify a subset of the data.
    xlabel, ylabel : str | None
        X- and y axis labels. By default the labels will be inferred from
        the data.
    xticklabels : bool | int | list of int
        Specify which axes should be annotated with x-axis tick labels.
        Use ``int`` for a single axis (default ``-1``), a sequence of
        ``int`` for multiple specific axes, or ``bool`` for all/none.
    bottom, top : scalar
        Y-axis limits.
    legend : str | int | 'fig' | None
        Matplotlib figure legend location argument or 'fig' to plot the
        legend in a separate figure.
    labels : dict
        Alternative labels for legend as ``{cell: label}`` dictionary (preserves
        order).
    xlim : scalar | (scalar, scalar)
        Initial x-axis view limits as ``(left, right)`` tuple or as ``length``
        scalar (default is the full x-axis in the data).
    tight : bool
        Use matplotlib's tight_layout to expand all axes to fill the figure
        (default True)
    ...
        Also accepts :ref:`general-layout-parameters`.

    Notes
    -----
    Navigation:
     - ``↑``: scroll up
     - ``↓``: scroll down
     - ``←``: scroll left
     - ``→``: scroll right
     - ``home``: scroll to beginning
     - ``end``: scroll to end
     - ``f``: x-axis zoom in (reduce x axis range)
     - ``d``: x-axis zoom out (increase x axis range)
     - ``r``: y-axis zoom in (reduce y-axis range)
     - ``c``: y-axis zoom out (increase y-axis range)
    """
    def __init__(self, y, xax=None, axtitle=True, ds=None, sub=None,
                 xlabel=True, ylabel=True, xticklabels=-1, bottom=None,
                 top=None, legend='upper right', labels=None, xlim=None, color=None, *args,
                 **kwargs):
        data = PlotData.from_args(y, (None,), xax, ds, sub)
        xdim = data.dims[0]
        layout = Layout(data.plot_used, 2, 4, *args, **kwargs)
        EelFigure.__init__(self, data.frame_title, layout)
        self._set_axtitle(axtitle, data)
        self._configure_xaxis_dim(data.y0.get_dim(xdim), xlabel, xticklabels)
        self._configure_yaxis(data, ylabel)

        self.plots = []
        legend_handles = {}
        vlims = _base.find_fig_vlims(data.data, top, bottom)

        n_colors = max(map(len, data.data))
        if color is None:
            colors = oneway_colors(n_colors)
        else:
            colors = (color,) * n_colors

        for ax, layers in zip(self._axes, data.data):
            h = _ax_uts(ax, layers, xdim, vlims, colors)
            self.plots.append(h)
            legend_handles.update(h.legend_handles)

        self.epochs = data.data
        XAxisMixin._init_with_data(self, data.data, xdim, xlim)
        YLimMixin.__init__(self, self.plots)
        LegendMixin.__init__(self, legend, legend_handles, labels)
        TimeSlicerEF.__init__(self, xdim, data.time_dim)
        self._show()

    def _fill_toolbar(self, tb):
        LegendMixin._fill_toolbar(self, tb)


class _ax_uts_stat:

    def __init__(self, ax, ct, colors, main, error, dev_data, xdim,
                 invy, bottom, top, hline, clusters, pmax, ptrend, clip,
                 error_alpha):
        # stat plots
        self.ax = ax
        self.stat_plots = []
        self.legend_handles = {}

        x = ct.y.get_dim(xdim)
        for cell in ct.cells:
            ndvar = ct.data[cell]
            y = ndvar.get_data(('case', xdim))
            plt = _plt_uts_stat(ax, x, y, main, error, dev_data, colors[cell],
                                cellname(cell), clip, error_alpha)
            self.stat_plots.append(plt)
            if plt.main is not None:
                self.legend_handles[cell] = plt.main[0]

        # hline
        if hline is not None:
            if isinstance(hline, tuple):
                if len(hline) != 2:
                    raise ValueError("hline must be None, scalar or length 2 tuple")
                hline, hline_kw = hline
                hline_kw = dict(hline_kw)
            else:
                hline_kw = {'color': 'k'}

            hline = float(hline)
            ax.axhline(hline, **hline_kw)

        # cluster plot
        self.cluster_plt = _plt_uts_clusters(ax, clusters, pmax, ptrend)

        # format y axis
        if invy:
            y0, y1 = ax.get_ylim()
            if bottom is None:
                bottom = y1

            if top is None:
                top = y0
        self.set_ylim(bottom, top)

    @property
    def title(self):
        return self.ax.get_title()

    def set_ylim(self, vmin, vmax):
        self.ax.set_ylim(vmin, vmax)
        self.vmin, self.vmax = self.ax.get_ylim()


class UTSClusters(EelFigure):
    """Plot permutation cluster test results

    Parameters
    ----------
    res : testnd.anova
        ANOVA with permutation cluster test result object.
    pmax : scalar
        Maximum p-value of clusters to plot as solid.
    ptrend : scalar
        Maximum p-value of clusters to plot as trend.
    axtitle : bool | sequence of str
        Title for the individual axes. The default is to show the names of the
        epochs, but only if multiple axes are plotted.
    cm : str
        Colormap to use for coloring different effects.
    overlay : bool
        Plot epochs (time course for different effects) on top of each
        other (as opposed to on separate axes).
    xticklabels : bool | int | list of int
        Specify which axes should be annotated with x-axis tick labels.
        Use ``int`` for a single axis (default ``-1``), a sequence of
        ``int`` for multiple specific axes, or ``bool`` for all/none.
    tight : bool
        Use matplotlib's tight_layout to expand all axes to fill the figure
        (default True)
    ...
        Also accepts :ref:`general-layout-parameters`.
    """
    def __init__(self, res, pmax=0.05, ptrend=0.1, axtitle=True, cm=None,
                 overlay=False, xticklabels=-1, *args, **kwargs):
        clusters_ = res.clusters

        data = PlotData.from_args(res, (None,))
        xdim = data.dims[0]
        # create figure
        layout = Layout(1 if overlay else data.plot_used, 2, 4, *args, **kwargs)
        EelFigure.__init__(self, data.frame_title, layout)
        self._set_axtitle(axtitle, data)

        colors = colors_for_oneway(range(data.n_plots), cmap=cm)
        self._caxes = []
        if overlay:
            ax = self._axes[0]

        for i, layers in enumerate(data.data):
            stat = layers[0]
            if not overlay:
                ax = self._axes[i]

            # ax clusters
            if clusters_:
                if 'effect' in clusters_:
                    cs = clusters_.sub('effect == %r' % stat.name)
                else:
                    cs = clusters_
            else:
                cs = None

            cax = _ax_uts_clusters(ax, stat, cs, colors[i], pmax, ptrend, xdim)
            self._caxes.append(cax)

        self._configure_yaxis(data, True)
        self._configure_xaxis_dim(data.y0.get_dim(xdim), True, xticklabels)
        self.clusters = clusters_
        self._show()

    def _fill_toolbar(self, tb):
        from .._wxgui import wx

        btn = wx.Button(tb, wx.ID_ABOUT, "Clusters")
        tb.AddControl(btn)
        btn.Bind(wx.EVT_BUTTON, self._OnShowClusterInfo)

    def _OnShowClusterInfo(self, event):
        from .._wxgui import show_text_dialog

        info = str(self.clusters)
        show_text_dialog(self._frame, info, "Clusters")

    def set_pmax(self, pmax=0.05, ptrend=0.1):
        "Set the threshold p-value for clusters to be displayed"
        for cax in self._caxes:
            cax.set_pmax(pmax, ptrend)
        self.draw()


class _ax_uts:

    def __init__(self, ax, layers, xdim, vlims, colors):
        vmin, vmax = _base.find_uts_ax_vlim(layers, vlims)

        self.legend_handles = {}
        for l, color in zip(layers, colors):
            color = l.info.get('color', color)
            p = _plt_uts(ax, l, xdim, color)
            self.legend_handles[longname(l)] = p.plot_handle
            contours = l.info.get('contours', None)
            if contours:
                for v, c in contours.items():
                    if v in contours:
                        continue
                    contours[v] = ax.axhline(v, color=c)

        self.ax = ax
        self.set_ylim(vmin, vmax)

    def set_ylim(self, vmin, vmax):
        self.ax.set_ylim(vmin, vmax)
        self.vmin, self.vmax = self.ax.get_ylim()


class _plt_uts:

    def __init__(self, ax, ndvar, xdim, color):
        y = ndvar.get_data((xdim,))
        x = ndvar.get_dim(xdim)._axis_data()
        self.plot_handle = ax.plot(x, y, color=color, label=longname(ndvar))[0]

        for y, kwa in _base.find_uts_hlines(ndvar):
            if color is not None:
                kwa['color'] = color
            ax.axhline(y, **kwa)


class _ax_uts_clusters:
    def __init__(self, ax, y, clusters, color=None, pmax=0.05, ptrend=0.1,
                 xdim='time'):
        self._bottom, self._top = _base.find_vlim_args(y)
        if color is None:
            color = y.info.get('color')

        _plt_uts(ax, y, xdim, color)

        if np.any(y.x < 0) and np.any(y.x > 0):
            ax.axhline(0, color='k')

        # pmap
        self.cluster_plt = _plt_uts_clusters(ax, clusters, pmax, ptrend, color)

        # save ax attr
        self.ax = ax
        x = y.get_dim(xdim)._axis_data()
        self.xlim = (x[0], x[-1])

        ax.set_xlim(*self.xlim)
        ax.set_ylim(bottom=self._bottom, top=self._top)

    def set_clusters(self, clusters):
        self.cluster_plt.set_clusters(clusters)

    def set_pmax(self, pmax=0.05, ptrend=0.1):
        self.cluster_plt.set_pmax(pmax, ptrend)


class _plt_uts_clusters:
    """UTS cluster plot

    Parameters
    ----------
    ax : Axes
        Axes.
    clusters : Dataset
        Dataset with entries for 'tstart', 'tstop' and 'p'.
    """
    def __init__(self, ax, clusters, pmax, ptrend, color=None, hatch='/'):
        self.pmax = pmax
        self.ptrend = ptrend
        self.h = []
        self.ax = ax
        self.clusters = clusters
        self.color = color
        self.hatch = hatch
        self.y = None
        self.dy = None
        self.update()

    def set_clusters(self, clusters, update=True):
        self.clusters = clusters
        if update:
            self.update()

    def set_color(self, color, update=True):
        self.color = color
        if update:
            self.update()

    def set_pmax(self, pmax, ptrend, update=True):
        self.pmax = pmax
        self.ptrend = ptrend
        if update:
            self.update()

    def set_y(self, y, dy, update=True):
        self.y = y
        self.dy = dy
        if update:
            self.update()

    def update(self):
        h = self.h
        while len(h):
            h.pop().remove()

        clusters = self.clusters
        if clusters is None:
            return

        if self.dy is None:
            bottom, top = self.ax.get_ylim()
            dy = (top - bottom) / 40.
        else:
            dy = self.dy

        p_include = self.ptrend or self.pmax
        for cluster in clusters.itercases():
            if 'p' in cluster:
                p = cluster['p']
                if p > p_include:
                    continue
                alpha = 0.5 if p < self.pmax else 0.2
            else:
                alpha = 0.5

            tstart = cluster['tstart']
            tstop = cluster['tstop']
            effect = cluster.get('effect')
            color = self.color[effect] if isinstance(self.color, dict) else self.color
            y = self.y[effect] if isinstance(self.y, dict) else self.y
            if y is None:
                h = self.ax.axvspan(
                    tstart, tstop, color=color, fill=True, alpha=alpha, zorder=-10)
            else:
                h = mpl.patches.Rectangle(
                    (tstart, y - dy / 2.), tstop - tstart, dy, facecolor=color,
                    linewidth=0, zorder=-10)
                self.ax.add_patch(h)
            self.h.append(h)


class _plt_uts_stat:

    def __init__(self, ax, x, y, main, error, dev_data, color, label, clip,
                 error_alpha):
        # plot main
        if hasattr(main, '__call__'):
            y_main = main(y, axis=0)
            lw = mpl.rcParams['lines.linewidth']
            if error == 'all':
                lw *= 2
            self.main = ax.plot(x, y_main, color=color, label=label, lw=lw,
                                zorder=5, clip_on=clip)
        elif error == 'all':
            self.main = None
        else:
            raise ValueError("Invalid argument: main=%r" % main)

        # plot error
        if error == 'all':
            self.error = ax.plot(x, y.T, color=color, alpha=error_alpha,
                                 clip_on=clip)
        elif error and len(y) > 1:
            if error == 'data':
                pass
            elif hasattr(error, '__call__'):
                dev_data = error(y, axis=0)
            else:
                dev_data = stats.variability(y, None, None, error, False)
            lower = y_main - dev_data
            upper = y_main + dev_data
            self.error = ax.fill_between(x, lower, upper, color=color,
                                         alpha=error_alpha,
                                         linewidth=0, zorder=0, clip_on=clip)
        else:
            self.error = None
