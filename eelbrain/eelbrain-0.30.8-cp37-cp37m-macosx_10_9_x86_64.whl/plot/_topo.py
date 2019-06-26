# -*- coding: utf-8 -*-
# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""Plot topographic maps of sensor space data."""
from collections import Sequence
from itertools import repeat
from math import floor, sqrt
from typing import Union, Tuple

import matplotlib as mpl
import numpy as np
from scipy import interpolate, linalg
from scipy.spatial import ConvexHull

from ._base import (
    PlotType, EelFigure, PlotData, AxisData, LayerData,
    Layout, ImLayout, VariableAspectLayout,
    ColorMapMixin, TimeSlicerEF, TopoMapKey, XAxisMixin, YLimMixin)
from ._utsnd import _ax_butterfly, _ax_im_array, _plt_im
from ._sensors import SENSORMAP_FRAME, SensorMapMixin, _plt_map2d


class Topomap(SensorMapMixin, ColorMapMixin, TopoMapKey, EelFigure):
    """Plot individual topogeraphies

    Parameters
    ----------
    y : (list of) NDVar, dims = ([case,] sensor,)
        Data to plot.
    xax : None | categorial
        Create a separate plot for each cell in this model.
    ds : None | Dataset
        If a Dataset is provided, data can be specified as strings.
    sub : str | array
        Specify a subset of the data.
    vmax : scalar
        Upper limits for the colormap (default is determined from data).
    vmin : scalar
        Lower limit for the colormap (default ``-vmax``).
    cmap : str
        Colormap (default depends on the data).
    contours : int | sequence | dict
        Contours to draw on topomaps. Can be an int (number of contours,
        including ``vmin``/``vmax``), a sequence (values at which to draw
        contours), or a ``**kwargs`` dict (must contain at least the "levels"
        key). Default is no contours.
    proj : str | list of str
        The sensor projection to use for topomaps (or one projection per plot).
    res : int
        Resolution of the topomaps (width = height = ``res``).
    interpolation : 'nearest' | 'linear' | 'spline'
        Method for interpolating topo-map between sensors (default is based on
        mne-python).
    clip : bool | 'even' | 'circle'
        Outline for clipping topomaps: 'even' to clip at a constant distance
        (default), 'circle' to clip using a circle.
    clip_distance : scalar
        How far from sensor locations to clip (1 is the axes height/width).
    head_radius : scalar | tuple
        Radius of the head outline drawn over sensors (on sensor plots with
        normalized positions, 0.45 is the outline of the topomap); 0 to plot no
        outline; tuple for separate (right, anterior) radius.
        The default is determined automatically.
    head_pos : scalar
        Head outline position along the anterior axis (0 is the center, 0.5 is
        the top end of the plot).
    im_interpolation : str
        Topomap image interpolation (see Matplotlib's
        :meth:`~matplotlib.axes.Axes.imshow`). Matplotlib 1.5.3's SVG output
        can't handle uneven aspect with ``interpolation='none'``, use
        ``interpolation='nearest'`` instead.
    sensorlabels : 'none' | 'index' | 'name' | 'fullname'
        Show sensor labels. For 'name', any prefix common to all names
        is removed; with 'fullname', the full name is shown.
    mark : Sensor index
        Sensors which to mark.
    mcolor : matplotlib color
        Color for marked sensors.
    axtitle : bool | sequence of str
        Title for the individual axes. The default is to show the names of the
        epochs, but only if multiple axes are plotted.
    xlabel : str
        Label below the topomaps (default is no label).
    margins : dict
        Layout parameter.
    ...
        Also accepts :ref:`general-layout-parameters`.

    Notes
    -----
    Keys:
     - ``t``: open a ``Topomap`` plot for the region under the mouse pointer.
     - ``T``: open a larger ``Topomap`` plot with visible sensor names for the
       map under the mouse pointer.
    """
    def __init__(self, y, xax=None, ds=None, sub=None,
                 vmax=None, vmin=None, cmap=None, contours=None,
                 # topomap args
                 proj='default', res=None, interpolation=None, clip='even',
                 clip_distance=0.05, head_radius=None, head_pos=0,
                 im_interpolation=None,
                 # sensor-map args
                 sensorlabels=None, mark=None, mcolor=None,
                 # layout
                 axtitle=True, xlabel=None, margins=None,
                 *args, **kwargs):
        data = PlotData.from_args(y, ('sensor',), xax, ds, sub)
        self.plots = []
        ColorMapMixin.__init__(self, data.data, cmap, vmax, vmin, contours, self.plots)
        if isinstance(proj, str):
            proj = repeat(proj, data.n_plots)
        elif not isinstance(proj, Sequence):
            raise TypeError(f"proj={proj!r}")
        elif len(proj) != data.n_plots:
            raise ValueError(f"proj={proj!r}: need as many proj as axes ({data.n_plots})")

        layout = ImLayout(data.plot_used, 1, 5, margins, {}, *args, **kwargs)
        EelFigure.__init__(self, data.frame_title, layout)
        self._set_axtitle(axtitle, data, verticalalignment='top', pad=-1)

        # plots
        axes_data = data.for_plot(PlotType.IMAGE)
        for ax, layers, proj_ in zip(self._axes, axes_data, proj):
            h = _ax_topomap(ax, layers, clip, clip_distance, sensorlabels, mark,
                            mcolor, None, proj_, res, im_interpolation, xlabel,
                            self._vlims, self._cmaps, self._contours, interpolation,
                            head_radius, head_pos)
            self.plots.append(h)

        TopoMapKey.__init__(self, self._topo_data)
        SensorMapMixin.__init__(self, [h.sensors for h in self.plots])
        self._show()

    def _fill_toolbar(self, tb):
        ColorMapMixin._fill_toolbar(self, tb)
        SensorMapMixin._fill_toolbar(self, tb)

    def _topo_data(self, event):
        if event.inaxes:
            ax_i = self._axes.index(event.inaxes)
            p = self.plots[ax_i]
            return p.data, p.title, p.proj


class TopomapBins(SensorMapMixin, ColorMapMixin, TopoMapKey, EelFigure):
    """Topomaps in time-bins

    Parameters
    ----------
    y : (list of) NDVar, dims = ([case,] sensor, time)
        Data to plot.
    xax : None | categorial
        Create a separate plot for each cell in this model.
    ds : None | Dataset
        If a Dataset is provided, data can be specified as strings.
    sub : str | array
        Specify a subset of the data.
    vmax : scalar
        Upper limits for the colormap (default is determined from data).
    vmin : scalar
        Lower limit for the colormap (default ``-vmax``).
    cmap : str
        Colormap (default depends on the data).
    contours : int | sequence | dict
        Contours to draw on topomaps. Can be an int (number of contours,
        including ``vmin``/``vmax``), a sequence (values at which to draw
        contours), or a ``**kwargs`` dict (must contain at least the "levels"
        key). Default is no contours.
    proj : str
        The sensor projection to use for topomaps.
    res : int
        Resolution of the topomaps (width = height = ``res``).
    interpolation : 'nearest' | 'linear' | 'spline'
        Method for interpolating topo-map between sensors (default is based on
        mne-python).
    clip : bool | 'even' | 'circle'
        Outline for clipping topomaps: 'even' to clip at a constant distance
        (default), 'circle' to clip using a circle.
    clip_distance : scalar
        How far from sensor locations to clip (1 is the axes height/width).
    head_radius : scalar | tuple
        Radius of the head outline drawn over sensors (on sensor plots with
        normalized positions, 0.45 is the outline of the topomap); 0 to plot no
        outline; tuple for separate (right, anterior) radius.
        The default is determined automatically.
    head_pos : scalar
        Head outline position along the anterior axis (0 is the center, 0.5 is
        the top end of the plot).
    im_interpolation : str
        Topomap image interpolation (see Matplotlib's
        :meth:`~matplotlib.axes.Axes.imshow`). Matplotlib 1.5.3's SVG output
        can't handle uneven aspect with ``interpolation='none'``, use
        ``interpolation='nearest'`` instead.
    sensorlabels : 'none' | 'index' | 'name' | 'fullname'
        Show sensor labels. For 'name', any prefix common to all names
        is removed; with 'fullname', the full name is shown.
    mark : Sensor index
        Sensors which to mark.
    mcolor : matplotlib color
        Color for marked sensors.
    ...
        Also accepts :ref:`general-layout-parameters`.

    Notes
    -----
    Keys:
     - ``t``: open a ``Topomap`` plot for the map under the mouse pointer.
     - ``T``: open a larger ``Topomap`` plot with visible sensor names for the
       map under the mouse pointer.
    """
    def __init__(self, y, xax=None, ds=None, sub=None,
                 bin_length=0.05, tstart=None, tstop=None,
                 vmax=None, vmin=None, cmap=None, contours=None,
                 # topomap args
                 proj='default', res=None, interpolation=None, clip='even',
                 clip_distance=0.05, head_radius=None, head_pos=0,
                 im_interpolation=None,
                 # sensor-map args
                 sensorlabels=None, mark=None, mcolor=None,
                 *args, **kwargs):
        data = PlotData.from_args(y, ('sensor', 'time'), xax, ds, sub)
        self._plots = []
        data._cannot_skip_axes(self)
        bin_data = data.for_plot(PlotType.IMAGE).bin(bin_length, tstart, tstop)
        ColorMapMixin.__init__(self, data.data, cmap, vmax, vmin, contours, self._plots)

        # create figure
        time = bin_data.y0.get_dim('time')
        n_bins = len(time)
        n_rows = bin_data.n_plots
        layout = Layout(n_bins * n_rows, 1, 1.5, False, *args, nrow=n_rows, ncol=n_bins, **kwargs)
        EelFigure.__init__(self, data.frame_title, layout)
        self._plots.extend(repeat(None, n_bins * n_rows))

        for column, t in enumerate(time):
            t_data = bin_data.sub_time(t)
            for row, layers in enumerate(t_data):
                i = row * n_bins + column
                ax = self._axes[i]
                self._plots[i] = _ax_topomap(ax, layers, clip, clip_distance, sensorlabels, mark, mcolor, None, proj, res, im_interpolation, None, self._vlims, self._cmaps, self._contours, interpolation, head_radius, head_pos)

        self._set_axtitle((str(t) for t in time), axes=self._axes[:len(time)])
        TopoMapKey.__init__(self, self._topo_data)
        SensorMapMixin.__init__(self, [h.sensors for h in self._plots])
        self._show()

    def _fill_toolbar(self, tb):
        ColorMapMixin._fill_toolbar(self, tb)
        SensorMapMixin._fill_toolbar(self, tb)

    def _topo_data(self, event):
        if event.inaxes:
            ax_i = self._axes.index(event.inaxes)
            p = self._plots[ax_i]
            return p.data, p.title, p.proj


class TopoButterfly(ColorMapMixin, TimeSlicerEF, TopoMapKey, YLimMixin,
                    XAxisMixin, EelFigure):
    """Butterfly plot with corresponding topomaps

    Parameters
    ----------
    y : (list of) NDVar
        Data to plot.
    xax : None | categorial
        Create a separate plot for each cell in this model.
    ds : None | Dataset
        If a Dataset is provided, data can be specified as strings.
    sub : str | array
        Specify a subset of the data.
    vmax : scalar
        Upper limits for the colormap (default is determined from data).
    vmin : scalar
        Lower limit for the colormap (default ``-vmax``).
    cmap : str
        Colormap (default depends on the data).
    contours : int | sequence | dict
        Contours to draw on topomaps. Can be an int (number of contours,
        including ``vmin``/``vmax``), a sequence (values at which to draw
        contours), or a ``**kwargs`` dict (must contain at least the "levels"
        key). Default is no contours.
    color : matplotlib color
        Color of the butterfly plots.
    linewidth : scalar
        Linewidth for plots (defult is to use ``matplotlib.rcParams``).
    proj : str
        The sensor projection to use for topomaps.
    res : int
        Resolution of the topomaps (width = height = ``res``).
    interpolation : 'nearest' | 'linear' | 'spline'
        Method for interpolating topo-map between sensors (default is based on
        mne-python).
    clip : bool | 'even' | 'circle'
        Outline for clipping topomaps: 'even' to clip at a constant distance
        (default), 'circle' to clip using a circle.
    clip_distance : scalar
        How far from sensor locations to clip (1 is the axes height/width).
    head_radius : scalar | tuple
        Radius of the head outline drawn over sensors (on sensor plots with
        normalized positions, 0.45 is the outline of the topomap); 0 to plot no
        outline; tuple for separate (right, anterior) radius.
        The default is determined automatically.
    head_pos : scalar
        Head outline position along the anterior axis (0 is the center, 0.5 is
        the top end of the plot).
    im_interpolation : str
        Topomap image interpolation (see Matplotlib's
        :meth:`~matplotlib.axes.Axes.imshow`). Matplotlib 1.5.3's SVG output
        can't handle uneven aspect with ``interpolation='none'``, use
        ``interpolation='nearest'`` instead.
    sensorlabels : 'none' | 'index' | 'name' | 'fullname'
        Show sensor labels. For 'name', any prefix common to all names
        is removed; with 'fullname', the full name is shown.
    mark : Sensor index
        Sensors which to mark.
    mcolor : matplotlib color
        Color for marked sensors.
    xlabel, ylabel : bool | string
        Labels for x and y axes. If True, labels are automatically chosen.
    xticklabels : bool | int | list of int
        Specify which axes should be annotated with x-axis tick labels.
        Use ``int`` for a single axis (default ``-1``), a sequence of
        ``int`` for multiple specific axes, or ``bool`` for all/none.
    axtitle : bool | sequence of str
        Title for the individual axes. The default is to show the names of the
        epochs, but only if multiple axes are plotted.
    frame : 't'
        Use T-frame for the Butterfly plots (default is rectangular frame).
    xlim : scalar | (scalar, scalar)
        Initial x-axis view limits as ``(left, right)`` tuple or as ``length``
        scalar (default is the full x-axis in the data).
    ...
        Also accepts :ref:`general-layout-parameters`.

    Notes
    -----
    Topomap control:
     - LMB click in a butterfly plot fixates the topomap time
     - RMB click in a butterfly plot removes the time point, the topomaps
       follow the mouse pointer
     - ``.``: Increment the current topomap time (got right)
     - ``,``: Decrement the current topomap time (go left)
     - ``t``: open a ``Topomap`` plot for the time point under the mouse
       pointer
     - ``T``: open a larger ``Topomap`` plot with visible sensor names for the
       time point under the mouse pointer

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
    _default_xlabel_ax = -2

    def __init__(self, y, xax=None, ds=None, sub=None,
                 vmax=None, vmin=None, cmap=None, contours=None,
                 color=None, linewidth=None,
                 # topomap args
                 proj='default', res=None, interpolation=None, clip='even',
                 clip_distance=0.05, head_radius=None, head_pos=0,
                 im_interpolation=None,
                 # sensor-map args
                 sensorlabels=None, mark=None, mcolor=None,
                 # layout
                 xlabel=True, ylabel=True, xticklabels=-1,
                 axtitle=True, frame=True, xlim=None,
                 *args, **kwargs):
        data = PlotData.from_args(y, ('sensor', None), xax, ds, sub)
        data._cannot_skip_axes(self)
        xdim = data.dims[1]
        self._topomap_data = data.for_plot(PlotType.IMAGE)

        # create figure
        layout = VariableAspectLayout(data.n_plots, 3, 10, (None, 1), None, (frame, False), self._set_axtitle(axtitle, data, data.n_plots), *args, **kwargs)
        EelFigure.__init__(self, data.frame_title, layout)

        self.bfly_axes = self._axes[0::2]
        self.topo_axes = self._axes[1::2]
        self.bfly_plots = []
        self.topo_plots = []
        self.t_markers = []  # vertical lines on butterfly plots

        ColorMapMixin.__init__(self, data.data, cmap, vmax, vmin, contours,
                               self.topo_plots)

        self._topo_kwargs = {
            'clip': clip,
            'clip_distance': clip_distance,
            'head_radius': head_radius,
            'head_pos': head_pos,
            'proj': proj,
            'contours': self._contours,
            'res': res,
            'interpolation': interpolation,
            'im_interpolation': im_interpolation,
            'sensorlabels': sensorlabels,
            'mark': mark,
            'mcolor': mcolor,
        }

        # plot epochs (x/y are in figure coordinates)
        for i, ax in enumerate(self.bfly_axes):
            layers = data.axis_for_plot(i, PlotType.LINE)
            h = _ax_butterfly(ax, layers, 'time', 'sensor', mark, color, linewidth, self._vlims, clip)
            self.bfly_plots.append(h)

        # decorate axes
        self._configure_xaxis_dim(data.time_dim, xlabel, xticklabels, self.bfly_axes)
        self._configure_yaxis(data, ylabel, self.bfly_axes)

        # setup callback
        XAxisMixin._init_with_data(self, data.data, xdim, xlim, self.bfly_axes)
        YLimMixin.__init__(self, self.bfly_plots + self.topo_plots)
        TimeSlicerEF.__init__(self, xdim, data.time_dim, self.bfly_axes, False)
        TopoMapKey.__init__(self, self._topo_data)
        self._realtime_topo = True
        self._t_label = None  # time label under lowest topo-map
        self._frame .store_canvas()
        self._update_topo(data.time_dim[0])

        self._show(crosshair_axes=self.bfly_axes)
        self._init_controller()

    def _fill_toolbar(self, tb):
        ColorMapMixin._fill_toolbar(self, tb)

    def _update_topo(self, t):
        if not self.topo_plots:
            data = self._topomap_data.sub_time(t)
            for ax, layers in zip(self.topo_axes, data):
                p = _ax_topomap(ax, layers, cmaps=self._cmaps, vlims=self._vlims, **self._topo_kwargs)
                self.topo_plots.append(p)
        else:
            data = self._topomap_data.sub_time(t, data_only=True)
            for p, layers in zip(self.topo_plots, data):
                p.set_data(layers)

    def _topo_data(self, event):
        ax = event.inaxes
        p = self.bfly_plots[ax.id // 2]
        if ax in self.bfly_axes:
            t = event.xdata
        elif ax in self.topo_axes:
            t = self._current_time
        else:
            return
        seg = [l.sub(time=t) for l in p.data]
        return seg, "%i ms" % round(t * 1e3), self._topo_kwargs['proj']

    def _on_leave_axes_status_text(self, event):
        return "Topomap: t = %.3f" % self._current_time

    def _update_time(self, t, fixate):
        TimeSlicerEF._update_time(self, t, fixate)
        self._update_topo(t)
        if fixate:
            # add time label
            text = "t = %i ms" % round(t * 1e3)
            if self._t_label:
                self._t_label.set_text(text)
            else:
                ax = self.topo_axes[-1]
                self._t_label = ax.text(.5, -0.1, text, ha='center', va='top')
            self.canvas.draw()  # otherwise time label does not get redrawn
        elif self._time_fixed:
            self._t_label.remove()
            self._t_label = None
            self.canvas.draw()  # otherwise time label does not get redrawn
        else:
            self.canvas.redraw(self.topo_axes)


class _plt_topomap(_plt_im):
    """Topomap plot

    Parameters
    ----------
    ...
    im_frame : scalar
        Empty space beyond outmost sensors in the im plot.
    vmax : scalar
        Override the colorspace vmax.
    interpolation : 'nearest' | 'linear' | 'spline'
        Method for interpolating topo-map between sensors.
    """
    _aspect = 'equal'

    def __init__(
            self,
            ax: mpl.axes.Axes,
            layer: LayerData,
            proj: str,
            res: int,
            im_interpolation: str,
            vlims,
            cmaps,
            contours,
            interpolation: str,
            clip: str,
            clip_distance: float,
    ):
        # store attributes
        self._proj = proj
        self._visible_data = layer.y.sensor._visible_sensors(proj)
        self._grid = np.linspace(0, 1, res)
        self._mgrid = tuple(np.meshgrid(self._grid, self._grid))
        self._method = interpolation

        # clip mask
        if interpolation is None and clip:
            locs = layer.y.sensor.get_locs_2d(self._proj, frame=SENSORMAP_FRAME)
            if clip == 'even':
                hull = ConvexHull(locs)
                points = locs[hull.vertices]
                default_head_radius = sqrt(np.min(np.sum((points - [0.5, 0.5]) ** 2, 1)))
                # find offset due to clip_distance
                tangents = np.roll(points, -1, axis=0) - np.roll(points, 1, axis=0)
                verticals = np.dot(tangents, [[0, -1], [1, 0]])
                verticals /= np.sqrt(np.sum(verticals ** 2, 1)[:, None])
                verticals *= clip_distance
                # apply offset
                points += verticals
                mask = mpl.patches.Polygon(points, transform=ax.transData)
            elif clip == 'circle':
                clip_radius = sqrt(np.max(np.sum((locs - [0.5, 0.5]) ** 2, 1)))
                mask = mpl.patches.Circle((0.5, 0.5), clip_radius, transform=ax.transData)
                default_head_radius = clip_radius
            else:
                raise ValueError('clip=%r' % (clip,))
        else:
            mask = None
            default_head_radius = None

        self._default_head_radius = default_head_radius
        _plt_im.__init__(self, ax, layer, cmaps, vlims, contours, (0, 1, 0, 1), im_interpolation, mask)

    def _data_from_ndvar(self, ndvar):
        v = ndvar.get_data(('sensor',))
        locs = ndvar.sensor.get_locs_2d(self._proj, frame=SENSORMAP_FRAME)
        if self._visible_data is not None:
            v = v[self._visible_data]
            locs = locs[self._visible_data]

        # axis parameter in numpy >= 0.13
        # unique_locs = np.unique(locs, axis=0)

        if self._method is None:
            # interpolate data
            xi, yi = self._mgrid

            # code adapted from mne-python topmap _griddata()
            xy = locs[:, 0] + locs[:, 1] * -1j
            d = np.abs(xy - xy[:, None])
            diagonal_step = len(locs) + 1
            d.flat[::diagonal_step] = 1.

            g = (d * d) * (np.log(d) - 1.)
            g.flat[::diagonal_step] = 0.
            try:
                weights = linalg.solve(g, v.ravel())
            except ValueError:
                raise NotImplementedError(
                    "Error determining sensor map projection, possibly due to "
                    "more than one sensor in a single location; try using a "
                    "different projection.")

            m, n = xi.shape
            out = np.empty_like(xi)

            g = np.empty(xy.shape)
            for i in range(m):
                for j in range(n):
                    d = np.abs(xi[i, j] + -1j * yi[i, j] - xy)
                    mask = np.where(d == 0)[0]
                    if len(mask):
                        d[mask] = 1.
                    np.log(d, out=g)
                    g -= 1.
                    g *= d * d
                    if len(mask):
                        g[mask] = 0.
                    out[i, j] = g.dot(weights)
            return out
        elif self._method == 'spline':
            k = int(floor(sqrt(len(locs)))) - 1
            tck = interpolate.bisplrep(locs[:, 1], locs[:, 0], v, kx=k, ky=k)
            return interpolate.bisplev(self._grid, self._grid, tck)
        else:
            isnan = np.isnan(v)
            if np.any(isnan):
                nanmap = interpolate.griddata(locs, isnan, self._mgrid, self._method)
                mask = nanmap > 0.5
                v = np.where(isnan, 0, v)
                vmap = interpolate.griddata(locs, v, self._mgrid, self._method)
                np.place(vmap, mask, np.NaN)
                return vmap
            return interpolate.griddata(locs, v, self._mgrid, self._method)


class _ax_topomap(_ax_im_array):
    """Axes with a topomap

    Parameters
    ----------
    mark : list of IDs
        highlight a subset of the sensors
    """
    def __init__(
            self,
            ax,
            layers: AxisData,
            clip: str = 'even',  # even or circle (only applies if interpolation is None)
            clip_distance: float=0.05,  # distance from outermost sensor for clip=='even'
            sensorlabels: str = None,  # index | name | fullname
            mark=None,
            mcolor=None,
            mmarker=None,
            proj: str = 'default',  # topomap projection method
            res: int = None,  # topomap image resolution
            im_interpolation: str = None,  # matplotlib imshow interpolation method
            xlabel: Union[bool, str] = None,
            vlims: dict = {},
            cmaps: dict = {},
            contours: dict = {},
            interpolation: str = None,  # topomap interpolation method
            head_radius: float = None,
            head_pos: Union[float, Tuple[float, float]] = 0.,  # y if centered on x, or (x, y)
            head_linewidth: float = None):
        self.ax = ax
        self.data = layers  # will not update from .set_data()
        self.proj = proj
        sensor_dim = layers.y0.sensor

        if xlabel is True:
            xlabel = layers.y0.name
        if im_interpolation is None:
            im_interpolation = 'bilinear'
        if res is None:
            res = 64 if interpolation is None else 100

        ax.set_axis_off()
        self.plots = [_plt_topomap(ax, layer, proj, res, im_interpolation, vlims, cmaps, contours, interpolation, clip, clip_distance) for layer in layers]

        # head outline
        if head_radius is None and clip == 'circle' and interpolation is None and sensor_dim._topomap_outlines(proj) == 'top':
            head_radius = self.plots[0]._default_head_radius

        # plot sensors
        self.sensors = _plt_map2d(ax, sensor_dim, proj, 1, '.', 1, 'k', mark,
                                  mcolor, mmarker, sensorlabels, False,
                                  head_radius, head_pos, head_linewidth)

        ax.set_aspect('equal')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        if isinstance(xlabel, str):
            x, y = ax.transData.inverted().transform(ax.transAxes.transform((0.5, 0)))
            ax.text(x, y, xlabel, ha='center', va='top')

    def set_ylim(self, bottom, top):  # Alias for YLimMixin
        self.set_vlim(bottom, top)


class _TopoWindow:
    """Helper class for TopoArray.

    Maintains a topomap corresponding to one segment with flexible time point.
    """
    def __init__(self, ax, parent, *plot_args):
        self.ax = ax
        self.parent = parent
        self.plot_args = plot_args
        # initial plot state
        self.t_line = None
        self.pointer = None
        self.plot = None

    def update(self, t):
        if t is not None:
            if self.t_line:
                self.t_line.remove()
            self.t_line = self.parent.ax.axvline(t, c='r')

            t_str = "%i ms" % round(t * 1e3)
            if self.pointer:
                self.pointer.axes = self.parent.ax
                self.pointer.xy = (t, 1)
                self.pointer.set_text(t_str)
                self.pointer.set_visible(True)
            else:
                xytext = self.ax.transAxes.transform((.5, 1))
                # These coordinates are in 'figure pixels'. They do not scale
                # when the figure is rescaled, so we need to transform them
                # into 'figure fraction' coordinates
                inv = self.ax.figure.transFigure.inverted()
                xytext = inv.transform(xytext)
                self.pointer = self.parent.ax.annotate(
                    t_str, (t, 0),
                    xycoords='data',
                    xytext=xytext,
                    textcoords='figure fraction',
                    horizontalalignment='center',
                    verticalalignment='center',
                    arrowprops={'arrowstyle': '-',
                                'shrinkB': 0,
                                'connectionstyle': "angle3,angleA=90,angleB=0",
                                'color': 'r'},
                    zorder=99)

            if self.plot is None:
                layers = self.parent.data.sub_time(t)
                self.plot = _ax_topomap(self.ax, layers, *self.plot_args)
            else:
                layers = self.parent.data.sub_time(t, data_only=True)
                self.plot.set_data(layers)

    def clear(self):
        self.ax.cla()
        self.ax.set_axis_off()
        self.plot = None
        if self.t_line:
            self.t_line.remove()
            self.t_line = None
        if self.pointer:
            self.pointer.remove()
            self.pointer = None

    def add_contour(self, meas, level, color):
        if self.plot:
            self.plot.add_contour(meas, level, color)

    def set_cmap(self, cmap, meas):
        if self.plot:
            self.plot.set_cmap(cmap, meas)

    def set_vlim(self, v, vmax=None, meas=None):
        if self.plot:
            self.plot.set_vlim(v, vmax, meas)


class TopoArray(ColorMapMixin, EelFigure):
    """Channel by sample plots with topomaps for individual time points

    Parameters
    ----------
    y : (list of) NDVar
        Data to plot.
    xax : None | categorial
        Create a separate plot for each cell in this model.
    ds : None | Dataset
        If a Dataset is provided, data can be specified as strings.
    sub : str | array
        Specify a subset of the data.
    vmax : scalar
        Upper limits for the colormap (default is determined from data).
    vmin : scalar
        Lower limit for the colormap (default ``-vmax``).
    cmap : str
        Colormap (default depends on the data).
    contours : int | sequence | dict
        Contours to draw on topomaps. Can be an int (number of contours,
        including ``vmin``/``vmax``), a sequence (values at which to draw
        contours), or a ``**kwargs`` dict (must contain at least the "levels"
        key). Default is no contours.
    ntopo | int
        number of topomaps per array-plot.
    t : list of scalar (len <= ntopo)
        Time points for topomaps.
    proj : str
        The sensor projection to use for topomaps.
    res : int
        Resolution of the topomaps (width = height = ``res``).
    interpolation : 'nearest' | 'linear' | 'spline'
        Method for interpolating topo-map between sensors (default is based on
        mne-python).
    clip : bool | 'even' | 'circle'
        Outline for clipping topomaps: 'even' to clip at a constant distance
        (default), 'circle' to clip using a circle.
    clip_distance : scalar
        How far from sensor locations to clip (1 is the axes height/width).
    head_radius : scalar | tuple
        Radius of the head outline drawn over sensors (on sensor plots with
        normalized positions, 0.45 is the outline of the topomap); 0 to plot no
        outline; tuple for separate (right, anterior) radius.
        The default is determined automatically.
    head_pos : scalar
        Head outline position along the anterior axis (0 is the center, 0.5 is
        the top end of the plot).
    im_interpolation : str
        Topomap image interpolation (see Matplotlib's
        :meth:`~matplotlib.axes.Axes.imshow`). Matplotlib 1.5.3's SVG output
        can't handle uneven aspect with ``interpolation='none'``, use
        ``interpolation='nearest'`` instead.
    sensorlabels : 'none' | 'index' | 'name' | 'fullname'
        Show sensor labels. For 'name', any prefix common to all names
        is removed; with 'fullname', the full name is shown.
    mark : Sensor index
        Sensors which to mark.
    mcolor : matplotlib color
        Color for marked sensors.
    xticklabels : bool | int | list of int
        Specify which axes should be annotated with x-axis tick labels.
        Use ``int`` for a single axis (default ``-1``), a sequence of
        ``int`` for multiple specific axes, or ``bool`` for all/none.
    axtitle : bool | sequence of str
        Title for the individual axes. The default is to show the names of the
        epochs, but only if multiple axes are plotted.
    ...
        Also accepts :ref:`general-layout-parameters`.

    Notes
    -----
     - LMB click on a topomap selects it for tracking the mouse pointer
         - LMB on the array plot fixates the topomap time point
     - RMB on a topomap removes the topomap

    """
    _make_axes = False

    def __init__(self, y, xax=None, ds=None, sub=None,
                 vmax=None, vmin=None, cmap=None, contours=None,
                 ntopo=3, t=(),
                 # topomap args
                 proj='default', res=None, interpolation=None, clip='even',
                 clip_distance=0.05, head_radius=None, head_pos=0,
                 im_interpolation=None,
                 # sensor-map args
                 sensorlabels=None, mark=None, mcolor=None,
                 # layout
                 xticklabels=-1, axtitle=True,
                 title=None, *args, **kwargs):
        data = PlotData.from_args(y, ('time', 'sensor'), xax, ds, sub).for_plot(PlotType.IMAGE)
        n_topo_total = ntopo * data.n_plots

        # create figure
        layout = Layout(data.plot_used, 1.5, 4, False, title, *args, **kwargs)
        EelFigure.__init__(self, data.frame_title, layout)
        all_plots = []
        ColorMapMixin.__init__(self, data.data, cmap, vmax, vmin, contours, all_plots)

        # fig coordinates
        x_frame_l = .6 / self._layout.axw / data.n_plots
        x_frame_r = .025 / data.n_plots
        x_sep = .01 / data.n_plots
        x_per_ax = (1 - x_frame_l - x_frame_r) / data.n_plots

        self.figure.subplots_adjust(left=x_frame_l, right=1 - x_frame_r,
                                    bottom=.05, top=.9, wspace=.1, hspace=.3)
        self.title = title

        # save important properties
        self._data = data
        self._ntopo = ntopo
        self._default_xlabel_ax = -1 - ntopo

        # im_array plots
        self._array_axes = []
        self._array_plots = []
        self._topo_windows = []
        ax_height = .4 + .07 * (not title)
        ax_bottom = .45  # + .05*(not title)
        for i, layers in enumerate(data):
            ax_left = x_frame_l + i * (x_per_ax + x_sep)
            ax_right = 1 - x_frame_r - (data.n_plots - i - 1) * (x_per_ax + x_sep)
            ax_width = ax_right - ax_left
            ax = self.figure.add_axes((ax_left, ax_bottom, ax_width, ax_height),
                                      picker=True)
            ax.ID = i
            ax.type = 'main'
            im_plot = _ax_im_array(ax, layers, 'time', im_interpolation, self._vlims, self._cmaps, self._contours)
            self._axes.append(ax)
            self._array_axes.append(ax)
            self._array_plots.append(im_plot)
            if i > 0:
                ax.yaxis.set_visible(False)

            # topo plots
            for j in range(ntopo):
                ID = i * ntopo + j
                ax = self.figure.add_subplot(3, n_topo_total,
                                             2 * n_topo_total + 1 + ID,
                                             picker=True, xticks=[], yticks=[])
                ax.ID = ID
                ax.type = 'window'
                win = _TopoWindow(
                    ax, im_plot, clip, clip_distance, sensorlabels, mark,
                    mcolor, None, proj, res, im_interpolation, None,
                    self._vlims, self._cmaps, self._contours, interpolation,
                    head_radius, head_pos)
                self._axes.append(ax)
                self._topo_windows.append(win)
        all_plots.extend(self._array_plots)
        all_plots.extend(self._topo_windows)

        # if t argument is provided, set topo-map time points
        if t:
            if np.isscalar(t):
                t = [t]
            self.set_topo_ts(*t)

        self._set_axtitle(axtitle, data, self._array_axes)
        self._configure_xaxis_dim(data.y0.time, True, xticklabels, self._array_axes)
        self._configure_yaxis_dim(data.data, 'sensor', True, self._array_axes, False)

        # setup callback
        self._selected_window = None
        self.canvas.mpl_connect('pick_event', self._pick_handler)
        self._frame .store_canvas()
        self._show(crosshair_axes=self._array_axes)

    def _fill_toolbar(self, tb):
        ColorMapMixin._fill_toolbar(self, tb)

    def add_contour(self, meas, level, color='k'):
        """Add a contour line

        Parameters
        ----------
        meas : str
            The measurement for which to add a contour line.
        level : scalar
            The value at which to draw the contour.
        color : matplotlib color
            The color of the contour line.
        """
        for p in self._iter_plots():
            p.add_contour(meas, level, color)
        self.draw()

    def _iter_plots(self):
        "Iterate through non-empty plots"
        for p in self._array_plots:
            yield p
        for w in self._topo_windows:
            if w.plot is not None:
                yield w.plot

    def set_cmap(self, cmap, meas=None):
        """Change the colormap

        Parameters
        ----------
        cmap : str | colormap
            New colormap.
        meas : None | str
            Measurement to which to apply the colormap. With None, it is
            applied to all.
        """
        self._cmaps[meas] = cmap
        for p in self._iter_plots():
            p.set_cmap(cmap, meas)
        self.draw()

    def set_topo_t_single(self, topo_id, t):
        """
        Set the time for a single topomap.

        Parameters
        ----------
        topo_id : int
            Index of the topomap (numbered throughout the figure).
        t : scalar or ``None``
            time point; ``None`` clears the topomap
        """
        # get window ax
        w = self._topo_windows[topo_id]
        w.clear()

        if t is not None:
            w.update(t)

        self.canvas.draw()

    def set_topo_t(self, topo_id, t):
        """
        Set the time point for a topo-map (same for all array plots)

        Parameters
        ----------
        topo_id : int
            Index of the topomap (numberd for each array-plot).
        t : scalar or ``None``
            time point; ``None`` clears the topomap

        See Also
        --------
        .set_topo_ts : set several topomap time points at once
        .set_topo_t_single : set the time point of a single topomap
        """
        for i in range(len(self._array_plots)):
            _topo = self._ntopo * i + topo_id
            self.set_topo_t_single(_topo, t)

    def set_topo_ts(self, *t_list):
        """Set the time points displayed in topo-maps across all array-plots"""
        for i, t in enumerate(t_list):
            self.set_topo_t(i, t)

    def _pick_handler(self, pickevent):
        mouseevent = pickevent.mouseevent
        ax = pickevent.artist
        if ax.type == 'window':
            button = mouseevent.button  # 1: Left
            window = self._topo_windows[ax.ID]
            if button == 1:
                self._selected_window = window
            elif button in (2, 3):
                Id = window.ax.ID % self._ntopo
                self.set_topo_t(Id, None)
            else:
                pass
        elif (ax.type == 'main') and (self._selected_window is not None):
            self._selected_window.clear()  # to side track pdf export transparency issue
            # update corresponding topo_windows
            t = mouseevent.xdata
            Id = self._selected_window.ax.ID % self._ntopo
            self.set_topo_t(Id, t)

            self._selected_window = None
            self.canvas.draw()

    def _on_motion_sub(self, event):
        if (self._selected_window is not None and event.inaxes and
                event.inaxes.type == 'main' and
                event.xdata in self._data.plot_data[event.inaxes.ID].y0.time):
            self._selected_window.update(event.xdata)
            return {self._selected_window.ax}
        return set()
