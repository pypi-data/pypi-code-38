# -*- coding: utf-8 -*-
# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""Plot multidimensional uniform time series."""
import matplotlib as mpl
import numpy as np

from .._data_obj import Datalist
from .._names import INTERPOLATE_CHANNELS
from . import _base
from ._base import (
    PlotType,
    EelFigure, PlotData, LayerData, Layout,
    ColorMapMixin, LegendMixin, TimeSlicerEF, TopoMapKey, YLimMixin, XAxisMixin,
    pop_if_dict, set_dict_arg)


class _plt_im:

    _aspect = 'auto'

    def __init__(
            self,
            ax: mpl.axes.Axes,
            layer: LayerData,
            cmaps: dict,
            vlims: dict,
            contours: dict,
            extent, interpolation, mask=None):
        self.ax = ax
        self._meas = layer.y.info.get('meas')
        self._contours = layer.contour_plot_args(contours)
        self._data = self._data_from_ndvar(layer.y)
        self._extent = extent
        self._mask = mask

        if layer.plot_type == PlotType.IMAGE:
            kwargs = layer.im_plot_args(vlims, cmaps)
            self.im = ax.imshow(self._data, origin='lower', aspect=self._aspect, extent=extent, interpolation=interpolation, **kwargs)
            if mask is not None:
                self.im.set_clip_path(mask)
            self._cmap = kwargs['cmap']
            self.vmin, self.vmax = self.im.get_clim()
        elif layer.plot_type == PlotType.CONTOUR:
            self.im = None
            self.vmin = self.vmax = None
        else:
            raise RuntimeError(f"layer of type {layer.plot_type}")

        # draw flexible parts
        self._contour_h = None
        self._draw_contours()

    def _data_from_ndvar(self, ndvar):
        raise NotImplementedError

    def _draw_contours(self):
        if self._contour_h:
            for c in self._contour_h.collections:
                c.remove()
            self._contour_h = None

        if not self._contours:
            return

        # check whether any contours are in data range
        vmin = self._data.min()
        vmax = self._data.max()
        if not any(vmax >= l >= vmin for l in self._contours['levels']):
            return

        self._contour_h = self.ax.contour(self._data, origin='lower', extent=self._extent, **self._contours)
        if self._mask is not None:
            for c in self._contour_h.collections:
                c.set_clip_path(self._mask)

    def add_contour(self, meas, level, color):
        if self._meas == meas:
            levels = tuple(self._contours['levels']) + (level,)
            colors = tuple(self._contours['colors']) + (color,)
            self._contours = {'levels': levels, 'colors': colors}
            self._draw_contours()

    def get_kwargs(self):
        "Get the arguments required for plotting the im"
        if self.im:
            vmin, vmax = self.im.get_clim()
            args = dict(cmap=self._cmap, vmin=vmin, vmax=vmax)
        else:
            args = {}
        return args

    def set_cmap(self, cmap, meas=None):
        if (self.im is not None) and (meas is None or meas == self._meas):
            self.im.set_cmap(cmap)
            self._cmap = cmap

    def set_data(self, ndvar, vlim=False):
        data = self._data_from_ndvar(ndvar)
        if self.im is not None:
            self.im.set_data(data)
            if vlim:
                vmin, vmax = _base.find_vlim_args(ndvar)
                self.set_vlim(vmin, vmax, None)

        self._data = data
        self._draw_contours()

    def set_vlim(self, v, vmax=None, meas=None):
        if self.im is None:
            return
        elif (meas is not None) and (self._meas != meas):
            return
        vmin, vmax = _base.fix_vlim_for_cmap(v, vmax, self._cmap)
        self.im.set_clim(vmin, vmax)
        self.vmin, self.vmax = self.im.get_clim()


class _plt_im_array(_plt_im):

    def __init__(self, ax, layer, dimnames, interpolation, vlims, cmaps, contours):
        self._dimnames = dimnames[::-1]
        xdim, ydim = layer.y.get_dims(dimnames)
        xlim = xdim._axis_im_extent()
        ylim = ydim._axis_im_extent()
        _plt_im.__init__(self, ax, layer, cmaps, vlims, contours, xlim + ylim, interpolation)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

    def _data_from_ndvar(self, ndvar):
        return ndvar.get_data(self._dimnames)


class _ax_im_array:

    def __init__(self, ax, layers, x='time', interpolation=None, vlims={}, cmaps={}, contours={}):
        self.ax = ax
        self.data = layers
        dimnames = layers.y0.get_dimnames((x, None))
        self.plots = [_plt_im_array(ax, l, dimnames, interpolation, vlims, cmaps, contours) for l in layers]

    @property
    def title(self):
        return self.ax.get_title()

    def add_contour(self, meas, level, color):
        for l in self.plots:
            l.add_contour(meas, level, color)

    def set_cmap(self, cmap, meas=None):
        """Change the colormap in the array plot

        Parameters
        ----------
        cmap : str | colormap
            New colormap.
        meas : None | str
            Measurement to which to apply the colormap. With None, it is
            applied to all.
        """
        for l in self.plots:
            l.set_cmap(cmap, meas)

    def set_data(self, layers, vlim=False):
        """Update the plotted data

        Parameters
        ----------
        layers : list of NDVar
            Data to plot
        vlim : bool
            Update vlims for the new data.
        """
        for l, p in zip(layers, self.plots):
            p.set_data(l, vlim)

    def set_vlim(self, v, vmax=None, meas=None):
        for l in self.plots:
            l.set_vlim(v, vmax, meas)


class Array(TimeSlicerEF, ColorMapMixin, XAxisMixin, EelFigure):
    """Plot UTS data to a rectangular grid.

    Parameters
    ----------
    y : (list of) NDVar
        Data to plot.
    xax : None | categorial
        Create a separate plot for each cell in this model.
    xlabel, ylabel : bool | str
        Labels for x- and y-axis; the default is determined from the data.
    xticklabels : bool | int | list of int
        Specify which axes should be annotated with x-axis tick labels.
        Use ``int`` for a single axis (default ``-1``), a sequence of
        ``int`` for multiple specific axes, or ``bool`` for all/none.
    ds : None | Dataset
        If a Dataset is provided, ``epochs`` and ``xax`` can be specified
        as strings.
    sub : str | array
        Specify a subset of the data.
    x : str
        Dimension to plot on the x axis (default 'time').
    vmax : scalar
        Upper limits for the colormap.
    vmin : scalar
        Lower limit for the colormap.
    cmap : str
        Colormap (default depends on the data).
    axtitle : bool | sequence of str
        Title for the individual axes. The default is to show the names of the
        epochs, but only if multiple axes are plotted.
    interpolation : str
        Array image interpolation (see Matplotlib's
        :meth:`~matplotlib.axes.Axes.imshow`). Matplotlib 1.5.3's SVG output
        can't handle uneven aspect with ``interpolation='none'``, use
        ``interpolation='nearest'`` instead.
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
     - ``←``: scroll left
     - ``→``: scroll right
     - ``home``: scroll to beginning
     - ``end``: scroll to end
     - ``f``: zoom in (reduce x axis range)
     - ``d``: zoom out (increase x axis range)
    """
    def __init__(self, y, xax=None, xlabel=True, ylabel=True,
                 xticklabels=-1, ds=None, sub=None, x='time', vmax=None,
                 vmin=None, cmap=None, axtitle=True, interpolation=None,
                 xlim=None, *args, **kwargs):
        data = PlotData.from_args(y, (x, None), xax, ds, sub).for_plot(PlotType.IMAGE)
        xdim, ydim = data.dims
        self.plots = []
        ColorMapMixin.__init__(self, data.data, cmap, vmax, vmin, None, self.plots)

        layout = Layout(data.plot_used, 2, 4, *args, **kwargs)
        EelFigure.__init__(self, data.frame_title, layout)
        self._set_axtitle(axtitle, data)

        for ax, layers in zip(self._axes, data):
            p = _ax_im_array(ax, layers, x, interpolation, self._vlims, self._cmaps, self._contours)
            self.plots.append(p)

        self._configure_xaxis_dim(data.data[0][0].get_dim(xdim), xlabel, xticklabels)
        self._configure_yaxis_dim(data.data, ydim, ylabel, scalar=False)
        XAxisMixin._init_with_data(self, data.data, xdim, xlim, im=True)
        TimeSlicerEF.__init__(self, xdim, data.time_dim)
        self._show()

    def _fill_toolbar(self, tb):
        ColorMapMixin._fill_toolbar(self, tb)


class _plt_utsnd:
    """
    UTS-plot for a single epoch

    Parameters
    ----------
    ax : matplotlib axes
        Target axes.
    layer : LayerData
        Epoch to plot.
    sensors : None | True | numpy index
        The sensors to plot (None or True -> all sensors).
    """
    def __init__(self, ax, layer, xdim, line_dim, sensors=None, **kwargs):
        epoch = layer.y
        if sensors is not None and sensors is not True:
            epoch = epoch.sub(sensor=sensors)

        kwargs = layer.plot_args(kwargs)
        color = pop_if_dict(kwargs, 'color')
        z_order = pop_if_dict(kwargs, 'zorder')
        self._dims = (line_dim, xdim)
        x = epoch.get_dim(xdim)._axis_data()
        line_dim_obj = epoch.get_dim(line_dim)
        self.legend_handles = {}
        self.lines = ax.plot(x, epoch.get_data((xdim, line_dim)),
                             label=epoch.name, **kwargs)

        # apply line-specific formatting
        lines = Datalist(self.lines)
        if z_order:
            set_dict_arg('zorder', z_order, line_dim_obj, lines)

        if color:
            self.legend_handles = {}
            set_dict_arg('color', color, line_dim_obj, lines, self.legend_handles)
        else:
            self.legend_handles = {epoch.name: self.lines[0]}

        for y, kwa in _base.find_uts_hlines(epoch):
            ax.axhline(y, **kwa)

        self.epoch = epoch
        self._sensors = sensors

    def remove(self):
        while self.lines:
            self.lines.pop().remove()

    def set_visible(self, visible=True):
        for line in self.lines:
            line.set_visible(visible)

    def set_ydata(self, epoch):
        if self._sensors:
            epoch = epoch.sub(sensor=self._sensors)
        for line, y in zip(self.lines, epoch.get_data(self._dims)):
            line.set_ydata(y)


class _ax_butterfly:
    """Axis with butterfly plot

    Parameters
    ----------
    vmin, vmax: None | scalar
        Y axis limits.
    layers : list of LayerData
        Data layers to plot.
    """
    def __init__(self, ax, layers, xdim, linedim, sensors, color, linewidth, vlims, clip=True):
        self.ax = ax
        self.data = [l.y for l in layers]
        self.layers = []
        self.legend_handles = {}
        self._meas = None

        vmin, vmax = _base.find_uts_ax_vlim(self.data, vlims)

        name = ''
        for l in layers:
            h = _plt_utsnd(ax, l, xdim, linedim, sensors, clip_on=clip, color=color, linewidth=linewidth)
            self.layers.append(h)
            if not name and l.y.name:
                name = l.y.name

            self.legend_handles.update(h.legend_handles)

        ax.yaxis.offsetText.set_va('top')

        self.set_ylim(vmin, vmax)

    @property
    def title(self):
        return self.ax.get_title()

    def set_ylim(self, vmin, vmax):
        self.ax.set_ylim(vmin, vmax)
        self.vmin, self.vmax = self.ax.get_ylim()


class Butterfly(TimeSlicerEF, LegendMixin, TopoMapKey, YLimMixin, XAxisMixin, EelFigure):
    """Butterfly plot for NDVars

    Parameters
    ----------
    y : (list of) NDVar
        Data to plot.
    xax : None | categorial
        Create a separate plot for each cell in this model.
    sensors: None or list of sensor IDs
        sensors to plot (``None`` = all)
    axtitle : bool | sequence of str
        Title for the individual axes. The default is to show the names of the
        epochs, but only if multiple axes are plotted.
    xlabel : str | bool
        X-axis labels. By default the label is inferred from the data.
    ylabel : str | bool
        Y-axis labels. By default the label is inferred from the data.
    xticklabels : bool | int | list of int
        Specify which axes should be annotated with x-axis tick labels.
        Use ``int`` for a single axis (default ``-1``), a sequence of
        ``int`` for multiple specific axes, or ``bool`` for all/none.
    color : matplotlib color | dict
        Either a color for all lines, or a dictionary mapping levels of the 
        line dimension to colors. The default is to use ``NDVar.info['color']``
        if available, otherwise the matplotlib default color alternation. Use 
        ``color=True`` to use the matplotlib default.
    linewidth : scalar
        Linewidth for plots (defult is to use ``matplotlib.rcParams``).
    ds : None | Dataset
        If a Dataset is provided, ``epochs`` and ``xax`` can be specified
        as strings.
    sub : str | array
        Specify a subset of the data.
    x : str
        Dimension to plot on the x-axis (default 'time').
    vmax : scalar
        Top of the y axis (default depends on data).
    vmin : scalar
        Bottom of the y axis (default depends on data).
    xlim : scalar | (scalar, scalar)
        Initial x-axis view limits as ``(left, right)`` tuple or as ``length``
        scalar (default is the full x-axis in the data).
    clip : bool
        Clip lines outside of axes (the default depends on whether ``frame`` is
        closed or open).
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

    Keys available for sensor data:
     - ``t``: open a ``Topomap`` plot for the time point under the mouse pointer.
     - ``T``: open a larger ``Topomap`` plot with visible sensor names for the
       time point under the mouse pointer.
    """
    _cmaps = None  # for TopoMapKey mixin
    _contours = None
    # keep track of open butterfly combo plots to optimally position new plots on screen
    _OPEN_PLOTS = []

    def __init__(self, y, xax=None, sensors=None, axtitle=True,
                 xlabel=True, ylabel=True, xticklabels=-1, color=None,
                 linewidth=None,
                 ds=None, sub=None, x='time', vmax=None, vmin=None, xlim=None,
                 clip=None, *args, **kwargs):
        data = PlotData.from_args(y, (x, None), xax, ds, sub)
        xdim, linedim = data.dims
        layout = Layout(data.plot_used, 2, 4, *args, **kwargs)
        EelFigure.__init__(self, data.frame_title, layout)
        self._set_axtitle(axtitle, data)
        self._configure_xaxis_dim(data.y0.get_dim(xdim), xlabel, xticklabels)
        self._configure_yaxis(data.y0, ylabel)

        if clip is None:
            clip = layout.frame is True

        self.plots = []
        self._vlims = _base.find_fig_vlims(data.data, vmax, vmin)
        legend_handles = {}
        for i, ax in enumerate(self._axes):
            layers = data.axis_for_plot(i, PlotType.LINE)
            h = _ax_butterfly(ax, layers, xdim, linedim, sensors, color, linewidth, self._vlims, clip)
            self.plots.append(h)
            legend_handles.update(h.legend_handles)

        XAxisMixin._init_with_data(self, data.data, xdim, xlim)
        YLimMixin.__init__(self, self.plots)
        if linedim == 'sensor':
            TopoMapKey.__init__(self, self._topo_data)
        LegendMixin.__init__(self, 'invisible', legend_handles)
        TimeSlicerEF.__init__(self, xdim, data.time_dim)
        self._show()

    def _auto_position(self, p2=None):
        """Position Butterfly plot and corresponding time-slice plot"""
        from .._wxgui import wx
        from .._wxgui.mpl_canvas import CanvasFrame

        if not isinstance(self._frame, CanvasFrame):
            return
        px, py = wx.ClientDisplayRect()[:2]
        display_w, display_h = wx.DisplaySize()
        pw, ph = self._frame.GetSize()
        old_ys = []
        self.__class__._OPEN_PLOTS = [p for p in self._OPEN_PLOTS if p._frame is not None]
        if self._OPEN_PLOTS:
            for p in self._OPEN_PLOTS:
                old_x, old_y = p._frame.GetPosition()
                if old_x < px + 10:
                    _, old_h = p._frame.GetSize()
                    old_ys.append((old_y, old_y + old_h))
            if old_ys:
                old_ys.sort()
                # find vertical space without overlap
                for y_start, y_stop in old_ys:
                    overlap = max(0, min(py + ph, y_stop) - max(py, y_start))
                    # print(f"overlap: [{y_start}, {y_stop}], [{py}, {py + ph}] -> {overlap}")
                    if overlap:
                        py = y_stop
                    else:
                        break
                py = min(y_stop, display_h - ph)

        self._frame.SetPosition((px, py))
        self._OPEN_PLOTS.append(self)

        if p2:  # secondary plot
            p2w, _ = p2._frame.GetSize()
            p2x = min(px + pw, display_w - p2w)
            p2._frame.SetPosition((p2x, py))

    def _fill_toolbar(self, tb):
        LegendMixin._fill_toolbar(self, tb)

    def _topo_data(self, event):
        if not event.inaxes:
            return
        p = self.plots[self._axes.index(event.inaxes)]
        t = event.xdata
        data = [l.sub(time=t) for l in p.data]
        return data, p.title + ' %i ms' % round(t), 'default'


class _ax_bfly_epoch:

    def __init__(self, ax, epoch, mark=None, state=True, label=None, color='k',
                 lw=0.2, mcolor='r', mlw=0.8, antialiased=True, vlims={}):
        """Specific plot for showing a single sensor by time epoch

        Parameters
        ----------
        ax : mpl Axes
            Plot target axes.
        epoch : NDVar
            Sensor by time epoch.
        mark : dict {int: mpl color}
            Channel: color dict of channels with custom color.
        color : mpl color
            Color for unmarked traces.
        lw : scalar
            Sensor trace plot Line width (default 0.5).
        mlw : scalar
            Marked sensor plot line width (default 1).
        """
        self.lines = _plt_utsnd(ax, LayerData(epoch, PlotType.LINE), 'time', 'sensor',
                                color=color, lw=lw, antialiased=antialiased)
        ax.set_xlim(epoch.time[0], epoch.time[-1])

        self.ax = ax
        self.epoch = epoch
        self._state_h = []
        self._visible = True
        self.set_ylim(_base.find_uts_ax_vlim([epoch], vlims))
        self._styles = {None: {'color': color, 'lw': lw, 'ls': '-',
                               'zorder': 2},
                        'mark': {'color': mcolor, 'lw': mlw, 'ls': '-',
                                 'zorder': 10},
                        INTERPOLATE_CHANNELS: {'color': 'b', 'lw': 1.2,
                                               'ls': ':', 'zorder': 6}}
        self._marked = {'mark': set(), INTERPOLATE_CHANNELS: set()}
        if mark:
            self.set_marked('mark', mark)

        if label is None:
            label = ''
        self._label = ax.text(0, 1.01, label, va='bottom', ha='left', transform=ax.transAxes)

        # create initial plots
        self.set_state(state)

    def set_data(self, epoch, label=None):
        self.epoch = epoch
        self.lines.set_ydata(epoch)
        if label is not None:
            self._label.set_text(label)

    def set_marked(self, kind, sensors):
        """Set the channels which should be marked for a specific style

        Parameters
        ----------
        kind : str
            The style.
        sensors : collection of int
            Channel index for the channels to mark as ``kind``.
        """
        old = self._marked[kind]
        new = self._marked[kind] = set(sensors)
        if not old and not new:
            return
        # mark new channels
        for i in new.difference(old):
            self.lines.lines[i].update(self._styles[kind])
        # find channels to unmark
        old.difference_update(new)
        if not old:
            return
        # possible alternate style
        if kind == 'mark':
            other_kind = INTERPOLATE_CHANNELS
        else:
            other_kind = 'mark'
        # reset old channels
        for i in old:
            if i in self._marked[other_kind]:
                self.lines.lines[i].update(self._styles[other_kind])
            else:
                self.lines.lines[i].update(self._styles[None])

    def set_state(self, state):
        "Set the state (True=accept / False=reject)"
        if state:
            while self._state_h:
                h = self._state_h.pop()
                h.remove()
        else:
            if not self._state_h:
                h1 = self.ax.plot([0, 1], [0, 1], color='r', linewidth=1,
                                  transform=self.ax.transAxes)
                h2 = self.ax.plot([0, 1], [1, 0], color='r', linewidth=1,
                                  transform=self.ax.transAxes)
                self._state_h.extend(h1 + h2)

    def set_visible(self, visible=True):
        if self._visible != visible:
            self.lines.set_visible(visible)
            self._label.set_visible(visible)
            for line in self._state_h:
                line.set_visible(visible)
            self._visible = visible

    def set_ylim(self, ylim):
        if ylim:
            if np.isscalar(ylim):
                self.ax.set_ylim(-ylim, ylim)
            else:
                self.ax.set_ylim(ylim)
