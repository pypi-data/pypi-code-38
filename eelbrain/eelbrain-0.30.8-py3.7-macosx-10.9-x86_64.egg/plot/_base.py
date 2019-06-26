# -*- coding: utf-8 -*-
# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""Framework for figures embedded in a GUI

Implementation
==============

Plotting is implemented hierarchically in 3 different types of
functions/classes:

top-level (public names)
    Top-level functions or classes have public names create an entire figure.
    Some classes also retain the figure and provide methods for manipulating
    it.

_ax_
    Functions beginning with _ax_ organize an axes object. They do not
    create their own axes object (this is provided by the top-level function),
    but change axes formatting such as labels and extent.

_plt_
    Functions beginning with _plt_ only plot data to a given axes object
    without explicitly changing aspects of the axes themselves.


Top-level plotters can be called with nested lists of data-objects (NDVar
instances). They create a separate axes for each list element. Axes
themselves can have multiple layers (e.g., a difference map visualized through
a colormap, and significance levels indicated by contours).


Example: t-test
---------------

For example, the default plot for testnd.ttest() results is the
following list (assuming the test compares A and B):

``[A, B, [diff(A,B), p(A, B)]]``

where ``diff(...)`` is a difference map and ``p(...)`` is a map of p-values.
The main plot function creates a separate axes object for each list element:

- ``A``
- ``B``
- ``[diff(A,B), p(A, B)]``

Each of these element is then plotted with the corresponding _ax_ function.
The _ax_ function calls _plt_ for each of its input elements. Thus, the
functions executed are:

#. plot([A, B, [diff(A,B), p(A, B)]])
#. ---> _ax_(A)
#. ------> _plt_(A)
#. ---> _ax_(B)
#. ------> _plt_(B)
#. ---> _ax_([diff(A,B), p(A, B)])
#. ------> _plt_(diff(A,B))
#. ------> _plt_(p(A, B))

"""
import __main__

from collections import Iterable, Iterator
from copy import copy
from enum import Enum, auto
from itertools import chain
from logging import getLogger
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from typing import List, Sequence, Union
from typing import Iterator as IteratorType
import weakref

import matplotlib as mpl
from matplotlib.figure import SubplotParams
from matplotlib.ticker import FuncFormatter
import numpy as np
import PIL

from .._colorspaces import symmetric_cmaps, zerobased_cmaps, ALPHA_CMAPS
from .._config import CONFIG
from .._data_obj import (
    NDVar, Case, UTS,
    ascategorial, asndvar, assub, isnumeric, isdataobject, cellname,
)
from .._stats import testnd
from .._utils import IS_WINDOWS, LazyProperty, intervals, ui
from .._utils.subp import command_exists
from ..fmtxt import Image
from ..mne_fixes import MNE_EPOCHS
from .._ndvar import erode, resample
from .._text import enumeration, ms
from ._utils import adjust_hsv
from functools import reduce


# constants
POINT = 0.013888888888898

# defaults
defaults = {'maxw': 16, 'maxh': 10}


class PlotType(Enum):
    GENERAL = auto()
    LEGACY = auto()
    LINE = auto()
    IMAGE = auto()
    CONTOUR = auto()


def do_autorun(run=None):
    # http://stackoverflow.com/a/2356420/166700
    if run is not None:
        return run
    elif CONFIG['autorun'] is None:
        return not hasattr(__main__, '__file__')
    else:
        return CONFIG['autorun']


DISPLAY_UNIT = {
    's': 'ms',
    'V': 'µV',
    'T': 'fT',
    'sensor': int,
}
UNIT_FORMAT = {
    'A': 1,
    'Am': 1,
    'V': 1,
    'ms': 1e3,
    'mV': 1e3,
    'µV': 1e6,
    'pT': 1e12,
    'fT': 1e15,
    'dSPM': 1,
    'p': 1,
    'T': 1,
    'n': int,  # %i format
    'normalized': 1,
    int: int,
}
SCALE_FORMATTERS = {
    1: FuncFormatter(lambda x, pos: '%g' % x),
    1e3: FuncFormatter(lambda x, pos: '%g' % (1e3 * x)),
    1e6: FuncFormatter(lambda x, pos: '%g' % (1e6 * x)),
    1e9: FuncFormatter(lambda x, pos: '%g' % (1e9 * x)),
    1e12: FuncFormatter(lambda x, pos: '%g' % (1e12 * x)),
    1e15: FuncFormatter(lambda x, pos: '%g' % (1e15 * x)),
    int: FuncFormatter(lambda x, pos: '%i' % round(x)),
}
DEFAULT_CMAPS = {
    'B': 'xpolar',
    'V': 'xpolar',
    'p': 'sig',
    'f': 'viridis',
    'r': 'xpolar',
    't': 'xpolar',
}

INITIAL_RC = mpl.rcParams.copy()
del INITIAL_RC['backend']


def reset_rc():
    "Reset matplotlib rc-parameters to state at Eelbrain initialization"
    mpl.rcParams.update(INITIAL_RC)


def find_axis_params_data(v, label):
    """Find matching number formatter and label for display unit != data unit

    Parameters
    ----------
    v : PlotData | NDVar | Var | str | scalar
        Unit or scale of the axis. See ``unit_format`` dict above for options.
    label : bool | str
        If ``label is True``, try to infer a label from ``v``.

    Returns
    -------
    tick_formatter : Formatter
        Matplotlib axis tick formatter.
    label : str | None
        Axis label.
    """
    if isinstance(v, str):
        meas = None
        unit = v
        scale = UNIT_FORMAT.get(v, 1)
    elif isinstance(v, float):
        meas = None
        scale = v
        unit = None
    else:
        if isnumeric(v):
            meas = v.info.get('meas')
            data_unit = v.info.get('unit')
        elif isinstance(v, PlotData):
            meas = v.meas
            data_unit = v.unit
        else:
            raise TypeError("unit=%s" % repr(v))

        if data_unit in DISPLAY_UNIT:
            unit = DISPLAY_UNIT[data_unit]
            scale = UNIT_FORMAT[unit]
            if data_unit in UNIT_FORMAT:
                scale /= UNIT_FORMAT[data_unit]
        else:
            scale = 1
            unit = data_unit

    if label is True:
        if meas and unit and meas != unit:
            label = f'{meas} [{unit}]'
        elif meas:
            label = meas
        elif unit:
            label = unit
        elif isinstance(v, PlotData):
            label = v.default_y_label
        elif isnumeric(v):
            label = v.name

    # ScalarFormatter: disabled because it always used e notation in status bar
    # (needs separate instance because it adapts to data)
    # fmt = ScalarFormatter() if scale == 1 else scale_formatters[scale]
    return SCALE_FORMATTERS[scale], label


def find_uts_hlines(ndvar):
    """Find horizontal lines for uts plots (based on contours)

    Parameters
    ----------
    ndvar : NDVar
        Data to be plotted.

    Returns
    -------
    h_lines : iterator
        Iterator over (y, kwa) tuples.
    """
    contours = ndvar.info.get('contours', None)
    if contours:
        for level in sorted(contours):
            args = contours[level]
            if isinstance(args, dict):
                yield level, args.copy()
            else:
                yield level, {'color': args}


def find_uts_ax_vlim(layers, vlims={}):
    """Find y axis limits for uts axes

    Parameters
    ----------
    layers : list of NDVar
        Data to be plotted.
    vlims : dict
        Vmax and vmin values by (meas, cmap).

    Returns
    -------
    bottom : None | scalar
        Lowest value on y axis.
    top : None | scalar
        Highest value on y axis.
    """
    bottom = None
    top = None
    for ndvar in layers:
        meas = ndvar.info.get('meas')
        if meas in vlims:
            bottom_, top_ = vlims[meas]
            if bottom is None:
                bottom = bottom_
            elif bottom_ != bottom:
                bottom = min(bottom, bottom_)
            if top is None:
                top = top_
            elif top_ != top:
                top = max(top, top_)

    return bottom, top


def find_fig_cmaps(epochs, cmap=None, alpha=False):
    """Find cmap for every meas

    Parameters
    ----------
    epochs : list of list of NDVar
        All NDVars in the plot.
    cmap : str
        Use this instead of the default for the first ``meas`` (for user
        argument).
    alpha : bool
        If possible, use cmaps with alpha.

    Returns
    -------
    cmaps : dict
        {meas: cmap} dict for all meas.
    """
    if isinstance(cmap, dict):
        out = cmap.copy()
        cmap = None
    else:
        out = {}

    for ndvar in chain(*epochs):
        meas = ndvar.info.get('meas')

        if meas in out and out[meas]:
            pass
        elif cmap is not None:
            out[meas] = cmap
            cmap = None
        elif 'cmap' in ndvar.info:
            out[meas] = ndvar.info['cmap']
        else:
            out[meas] = None

    for k in out.keys():
        if out[k] is None:
            out[k] = DEFAULT_CMAPS.get(meas, 'xpolar')
        # replace with cmap with alpha
        if alpha and out[k] in ALPHA_CMAPS:
            out[k] = ALPHA_CMAPS[out[k]]

    return out


def find_fig_contours(epochs, vlims, contours_arg):
    """Find contour arguments for every meas type

    Parameters
    ----------
    epochs : list of list of NDVar
        Data to be plotted.
    vlims : dist
        Vlims dict (used to interpret numerical arguments)
    contours_arg : int | sequence | dict
        User argument. Can be an int (number of contours), a sequence (values
        at which to draw contours), a kwargs dict (must contain the "levels"
        key), or a {meas: kwargs} dictionary.

    Returns
    -------
    contours : dict
        {meas: kwargs} mapping for contour plots.

    Notes
    -----
    The NDVar's info dict contains default arguments that determine how the
    NDVar is plotted as base and as overlay. In case of insufficient
    information, defaults apply. On the other hand, defaults can be overridden
    by providing specific arguments to plotting functions.
    """
    if isinstance(contours_arg, dict) and 'levels' not in contours_arg:
        out = contours_arg.copy()
        contours_arg = None
    else:
        out = {}

    for ndvars in epochs:
        for layer, ndvar in enumerate(ndvars):
            meas = ndvar.info.get('meas')
            if meas in out:
                continue

            if contours_arg is not None:
                param = contours_arg
                contours_arg = None
            else:
                if layer:  # overlay
                    kind = ndvar.info.get('overlay', ('contours',))
                else:
                    kind = ndvar.info.get('base', ())

                if 'contours' in kind:
                    param = ndvar.info.get('contours', None)
                    if layer:
                        param = ndvar.info.get('overlay_contours', param)
                    else:
                        param = ndvar.info.get('base_contours', param)

                    if isinstance(param, dict) and 'levels' not in param:
                        levels = sorted(param)
                        colors = [param[v] for v in levels]
                        param = {'levels': levels, 'colors': colors}
                else:
                    param = None

            if param is None:
                out[meas] = None
            elif isinstance(param, dict):
                out[meas] = param
            elif isinstance(param, int):
                vmin, vmax = vlims[meas]
                out[meas] = {'levels': np.linspace(vmin, vmax, param),
                             'colors': 'k'}
            else:
                out[meas] = {'levels': tuple(param), 'colors': 'k'}

    return out


def find_fig_vlims(plots, vmax=None, vmin=None, cmaps=None):
    """Find vmin and vmax parameters for every (meas, cmap) combination

    Parameters
    ----------
    plots : nested list of NDVar
        Unpacked plot data.
    vmax : None | dict | scalar
        Dict: predetermined vlims (take precedence). Scalar: user-specified
        vmax parameter (used for for the first meas kind).
    vmin : None | scalar
        User-specified vmin parameter. If vmax is user-specified but vmin is
        None, -vmax is used.
    cmaps : dict
        If provided, vlims will be fixed to match symmetric or 0-based cmaps.

    Returns
    -------
    vlims : dict
        Dictionary of im limits: {meas: (vmin, vmax)}.
    """
    if isinstance(vmax, dict):
        vlims = vmax
        ndvars = [v for v in chain.from_iterable(plots) if v.info.get('meas') not in vlims]
    else:
        ndvars = [*chain.from_iterable(plots)]

        vlims = {}
        if vmax is None:
            user_vlim = None
        elif vmin is None:
            if cmaps is None and any(v.min() < 0 for v in ndvars):
                user_vlim = (-vmax, vmax)
            else:
                user_vlim = (0, vmax)
        else:
            user_vlim = (vmin, vmax)

        # apply user specified vlim
        if user_vlim is not None:
            meas = ndvars[0].info.get('meas')
            vlims[meas] = user_vlim
            ndvars = [v for v in ndvars if v.info.get('meas') != meas]

    # for other meas, fill in data limits
    for ndvar in ndvars:
        meas = ndvar.info.get('meas')
        vmin, vmax = find_vlim_args(ndvar)
        if meas in vlims:
            vmin_, vmax_ = vlims[meas]
            vmin = min(vmin, vmin_)
            vmax = max(vmax, vmax_)

        if vmin == vmax:
            vmin -= 1
            vmax += 1
        vlims[meas] = (vmin, vmax)

    # fix vlims based on cmaps
    if cmaps is not None:
        for meas in vlims.keys():
            vmin, vmax = vlims[meas]
            vlims[meas] = fix_vlim_for_cmap(vmin, vmax, cmaps[meas])

    return vlims


def find_vlim_args(ndvar, vmin=None, vmax=None):
    if vmax is None:
        vmax = ndvar.info.get('vmax', None)
        if vmin is None:
            vmin = ndvar.info.get('vmin', None)

    if vmax is None or vmin is None:
        xmax = np.nanmax(ndvar.x)
        if np.ma.is_masked(xmax):
            xmax = xmax.data
        xmin = np.nanmin(ndvar.x)
        if np.ma.is_masked(xmin):
            xmin = xmin.data
        abs_max = max(abs(xmax), abs(xmin)) or 1e-14
        scale = math.floor(np.log10(abs_max))
        if vmax is None:
            vmax = math.ceil(xmax * 10 ** -scale) * 10 ** scale
        if vmin is None:
            vmin = math.floor(xmin * 10 ** -scale) * 10 ** scale

    return vmin, vmax


def fix_vlim_for_cmap(vmin, vmax, cmap):
    "Fix the vmin value to yield an appropriate range for the cmap"
    if cmap in symmetric_cmaps:
        if vmax is None and vmin is None:
            pass
        elif vmin is None:
            vmax = abs(vmax)
            vmin = -vmax
        elif vmax is None:
            vmax = abs(vmin)
            vmin = -vmax
        else:
            vmax = max(abs(vmax), abs(vmin))
            vmin = -vmax
    elif cmap in zerobased_cmaps:
        vmin = 0
    return vmin, vmax


def find_data_dims(ndvar, dims, extra_dim=None):
    """Find dimensions in data.

    Raise a ValueError if the dimensions don't match, except when the ``case``
    dimension is omitted in ``dims``.

    Parameters
    ----------
    ndvar : NDVar
        NDVar instance to query.
    dims : int | tuple of str
        The requested dimensions. ``None`` for a free dimensions.
    extra_dim : str
        Dimension that will be removed by other operation (e.g. ``xax``).

    Returns
    -------
    agg : None | str
        Dimension to aggregate over.
    dims : list | tuple of str
        Dimension names with all instances of ``None`` replaced by a string.
    """
    if isinstance(dims, int):
        if extra_dim:
            dims += 1

        dimnames = list(ndvar.dimnames)
        if ndvar.ndim == dims:
            agg = None
        elif ndvar.ndim == dims + 1:
            for agg in dimnames:
                if agg != extra_dim:
                    break
            dimnames.remove(agg)
        else:
            raise ValueError(f"y={ndvar} has wrong number of dimensions; {dims} or {dims + 1} required")
    else:
        required_dims = (extra_dim,) + dims if extra_dim else dims
        if ndvar.ndim == len(required_dims):
            agg = None
            dimnames = list(ndvar.get_dimnames(required_dims))
        elif ndvar.ndim  == len(required_dims) + 1:
            if any(d is None for d in required_dims):
                if ndvar.has_case and 'case' not in required_dims:
                    agg = 'case'
                else:
                    raise ValueError(f"y={ndvar} is ambiguous for required dimensions {required_dims}")
            else:
                agg = None
            dimnames = list(ndvar.get_dimnames((agg,) + required_dims))
            agg = dimnames.pop(0)
        else:
            raise ValueError(f"y={ndvar} has wrong dimensions; {required_dims} or one more required")

        if extra_dim:
            dimnames.remove(extra_dim)
    return agg, tuple(dimnames)


def brain_data(
        data: Union[NDVar, testnd.NDTest],
):
    # for GlassBrain and surfer brain
    if isinstance(data, testnd.NDDifferenceTest):
        return data.masked_difference()
    else:
        return asndvar(data)


def butterfly_data(
        data: Union[NDVar, testnd.NDTest],
        hemi: str,
        resample_: int = None,
        colors: bool = False,
        return_vector_data: bool = False,
):
    """Data for plotting butterfly plot with brain

    Returns
    -------
    hemis : list of str
        Hemispheres in the data.
    butterfly_daya :
        Data for Butterfly plot.
    brain_data :
        Data for brain plot.
    """
    # find input type
    if isinstance(data, NDVar):
        y = data
        kind = 'ndvar'
    elif isinstance(data, testnd.NDDifferenceTest):
        y = data.masked_difference()
        kind = 'ndvar'
    else:
        raise TypeError(f"ndvar={data!r}")
    source = y.get_dim('source')

    # find samplingrate
    if resample_ is not None:
        raise NotImplementedError(f"resample_={resample_}")

    # find hemispheres to include
    if hemi is None:
        hemis = []
        if source.lh_n:
            hemis.append('lh')
        if source.rh_n:
            hemis.append('rh')
    elif hemi in ('lh', 'rh'):
        hemis = [hemi]
    else:
        raise ValueError("hemi=%r" % (hemi,))

    if kind == 'ndvar':
        if y.has_case:
            y = y.mean('case')
        if resample_:
            y = resample(y, resample_, window='hamming')
        if y.has_dim('space'):
            if return_vector_data:
                brain_data = y
                y = y.norm('space')
            else:
                y = y.norm('space')
                brain_data = y
        else:
            brain_data = y
        bfly_data = [y.sub(source=hemi, name=hemi.capitalize()) for hemi in hemis]
    elif kind == 'test':
        sig = data.p <= 0.05
        y_magnitude = y.rms('time')
        # resample
        if resample_:
            y = resample(y, resample_, window='hamming')
            sig = resample(sig, resample_) > 0.5
        brain_data = y.mask(~sig)
        # mask
        non_sig = erode(~sig, 'time')
        y_sig = y.mask(non_sig)
        y_ns = y.mask(sig)
        # line-styles
        if colors:
            lh_color = '#046AAD'
            rh_color = '#A60628'
            line_color_sig = {'lh': lh_color, 'rh': rh_color}
            line_color_ns = {'lh': adjust_hsv(lh_color, 0, -0.5, -0.),
                             'rh': adjust_hsv(rh_color, 0, -0.7, -0.)}
        else:
            color_sig = (0,) * 3
            color_ns = (.7,) * 3
            line_color_sig = {'lh': color_sig, 'rh': color_sig}
            line_color_ns = {'lh': color_ns, 'rh': color_ns}
        linestyle_ns = {'linewidth': 0.2, 'color': line_color_ns, 'alpha': 0.2}
        linestyle_sig = {'linewidth': 0.2, 'color': line_color_sig, 'alpha': 1.0}
        # layer-data
        axes = []
        for hemi in hemis:
            # z-order
            y_mag = y_magnitude.sub(source=hemi)
            z_order = dict(zip(y_mag.source, -y_mag.x.argsort()))
            # data
            layers = []
            for y, linestyle in ((y_ns, linestyle_ns), (y_sig, linestyle_sig)):
                kwargs = {'zorder': z_order, **linestyle}
                layers.append(LayerData(y.sub(source=hemi), PlotType.LINE, kwargs))
            axes.append(AxisData(layers))
        bfly_data = PlotData(axes, ('time', 'source'), plot_names=hemis)
    else:
        raise RuntimeError(f"kind={kind}")
    return hemis, bfly_data, brain_data


def pop_if_dict(kwargs, key):
    "Helper for artist-sepcific matplotlib kwargs"
    if key in kwargs and isinstance(kwargs[key], dict):
        return kwargs.pop(key)


def set_dict_arg(key, arg, line_dim_obj, artists, legend_handles=None):
    "Helper for artist-sepcific matplotlib kwargs"
    set_attr_name = 'set_' + key
    for dim_index, value in arg.items():
        index = line_dim_obj._array_index(dim_index)
        if isinstance(index, int):
            key_artists = [artists[index]]
        else:
            key_artists = artists[index]

        if not key_artists:
            continue

        for artist in key_artists:
            getattr(artist, set_attr_name)(value)

        if legend_handles is not None:
            for artist in key_artists:
                artist.set_label(dim_index)
            legend_handles[dim_index] = artist


_remap_args = {'c': 'color'}


class LayerData:
    """Data for one subplot layer"""

    def __init__(
            self,
            y: NDVar,
            plot_type: PlotType = PlotType.GENERAL,
            plot_args: dict = None,
            plot_args_2: dict = None,  # for contour plot of IMAGE layer
            bin_func: callable = np.mean,
    ):
        self.y = y
        self.is_masked = isinstance(y.x, np.ma.masked_array)
        self.plot_type = plot_type
        self._plot_args = self._dict_arg(plot_args)
        self._bin_func = bin_func
        if plot_type == PlotType.IMAGE:
            self._plot_args_2 = self._dict_arg(plot_args_2)
        elif plot_args_2:
            raise TypeError(f"plot_args_2={plot_args_2!r} for {plot_type}")
        else:
            self._plot_args_2 = None

    @staticmethod
    def _dict_arg(arg: dict = None) -> dict:
        if arg is None:
            return {}
        elif any(k in arg for k in _remap_args):
            return {_remap_args.get(k, k): v for k, v in arg.items()}
        else:
            return arg

    def plot_args(self, kwargs: dict) -> dict:
        # needs to be a copy?
        return {**self._dict_arg(kwargs), **self._plot_args}

    def contour_plot_args(self, contours):
        out = {}
        # contours arg
        meas = self.y.info.get('meas')
        if meas in contours:
            if contours[meas] is not None:
                out.update(contours[meas])
        # layer
        if self.plot_type == PlotType.IMAGE:
            out.update(self._plot_args_2)
        elif self.plot_type == PlotType.CONTOUR:
            out.update(self._plot_args)
        else:
            raise RuntimeError(f"layer of type {self.plot_type}")
        return out

    def im_plot_args(self, vlims: dict, cmaps: dict) -> dict:
        assert self.plot_type == PlotType.IMAGE
        meas = self.y.info.get('meas')
        if meas in cmaps:
            cmap = cmaps[meas]
        elif 'cmap' in self.y.info:
            cmap = self.y.info['cmap']
        else:
            cmap = DEFAULT_CMAPS.get(meas, 'xpolar')

        if meas in vlims:
            vmin, vmax = vlims[meas]
        else:
            vmin, vmax = find_vlim_args(self.y)
            vmin, vmax = fix_vlim_for_cmap(vmin, vmax, cmap)
        return {'cmap': cmap, 'vmin': vmin, 'vmax': vmax, **self._plot_args}

    def for_plot(self, plot_type: PlotType) -> IteratorType['LayerData']:
        if self.plot_type == plot_type:
            yield self
        elif not self.is_masked:
            yield LayerData(self.y, plot_type, self._plot_args)
        elif plot_type == PlotType.LEGACY:
            yield LayerData(self.y.unmask(), plot_type, self._plot_args)
        elif self.plot_type != PlotType.GENERAL:
            raise RuntimeError(f"Invalid PlotData conversion: {self.plot_type} -> {plot_type}")
        elif plot_type == PlotType.LINE:
            un_mask = NDVar(~self.y.x.mask, self.y.dims)
            # kwargs = {}
            if self.y.has_dim('time'):
                un_mask = erode(un_mask, 'time')
                # if self.y.ndim == 2:
                #     mag = self.y.rms('time')
                #     z_dim = mag.dimnames[0]
                #     kwargs['zorder'] = dict(zip(mag.get_dim(z_dim), -mag.x.argsort()))
            y_masked = self.y.unmask().mask(un_mask)
            args_main = {'alpha': 1., 'zorder': 1}
            args_masked = {'alpha': 0.4, 'color': (.7, .7, .7), 'zorder': 0}
            for y, args in ((self.y, args_main), (y_masked, args_masked)):
                yield LayerData(y, plot_type, args)
        elif plot_type == PlotType.IMAGE:
            x = NDVar(self.y.x.data, self.y.dims, self.y.info, self.y.name)
            yield LayerData(x, PlotType.IMAGE)
            x = NDVar(1. - self.y.x.mask, self.y.dims, {'meas': 'mask'}, self.y.name)
            yield LayerData(x, PlotType.CONTOUR, {'levels': [0.5], 'colors': ['black']}, bin_func=np.max)
        else:
            raise RuntimeError(f"plot_type={plot_type!r}")

    def bin(self, bin_length, tstart, tstop):
        y = self.y.bin(bin_length, tstart, tstop, self._bin_func)
        return LayerData(y, self.plot_type, self._plot_args, self._plot_args_2, self._bin_func)

    def sub_time(self, time: float, data_only: bool = False):
        y = self.y.sub(time=time)
        if data_only:
            return y
        else:
            return LayerData(y, self.plot_type, self._plot_args, self._plot_args_2, self._bin_func)


class AxisData:
    """Represent one axis (multiple layers)"""
    def __init__(
            self,
            layers: List[LayerData],
    ):
        self.layers = layers

    def __iter__(self):
        return iter(self.layers)

    @property
    def y0(self):
        for layer in self.layers:
            return layer.y
        raise IndexError("No data")

    def for_plot(self, plot_type: PlotType) -> 'AxisData':
        return AxisData([l for layer in self.layers for l in layer.for_plot(plot_type)])

    def bin(self, bin_length, tstart, tstop):
        return AxisData([l.bin(bin_length, tstart, tstop) for l in self.layers])

    def sub_time(self, time: float, data_only: bool = False):
        axis = []
        for layer in self.layers:
            if time in layer.y.time:
                axis.append(layer.sub_time(time, data_only))
        if data_only:
            return axis
        else:
            return AxisData(axis)


class PlotData:
    """Organize nd-data for plotting

    Parameters
    ----------
    axes : list of {None | list of LayerData}
        Data to be plotted on each axes.
    dims : list of str
        Dimensions assigned to the axes.
    title : str
        Default window title.
    plot_names : list of str
        Titles for the plots (all non-None axes).

    Attributes
    ----------
    plot_used : list of bool
        List indicating which plot slots are used (as opposed to empty).
    plot_data : list of AxisData
        The processed data to plot.
    data : list of list of NDVar
        The processed data to plot (for backwards compatibility).
    dims : tuple of str
        Dimensions assigned to the axes.
    title : str
        Data description for the plot frame.
    plot_names : list of str
        Titles for the plots.

    Notes
    -----
    :class:`PlotData` is initially independent of plot type, and can be rendered
    into specific plot-types with :meth:`PlotData.for_plot` methods.
    """
    def __init__(
            self,
            axes: List[AxisData],
            dims: Sequence[str],
            title: str = "unnamed data",
            plot_names: List[str] = None,
            use_axes: List[bool] = None,
            plot_type: PlotType = PlotType.GENERAL,
    ):
        self.plot_data = axes
        self.n_plots = len(axes)
        if use_axes is None:
            self.plot_used = (True,) * self.n_plots
        else:
            assert sum(use_axes) == self.n_plots
            self.plot_used = use_axes
        self.has_masked_data = any(l.is_masked for ax in self.plot_data for l in ax)
        self.dims = dims
        self.frame_title = title
        if plot_names is not None:
            assert len(plot_names) == self.n_plots
        self._plot_names = plot_names
        self.plot_type = plot_type

    def __repr__(self):
        desc = [f'{self.n_plots} plots']
        if not all(self.plot_used):
            desc.append(f'{len(self.plot_used) - self.n_plots} empty')
        desc.append(' x '.join(self.dims))
        return f"<PlotData {self.frame_title!r}: {', '.join(desc)}>"

    def _cannot_skip_axes(self, parent):
        if not all(self.plot_used):
            raise NotImplementedError(f"y can not contain None for {parent.__class__.__name__} plot")

    def __iter__(self):
        return iter(self.plot_data)

    @classmethod
    def from_args(cls, y, dims, xax=None, ds=None, sub=None):
        """Unpack the first argument to top-level NDVar plotting functions

        Parameters
        ----------
        y : NDVar | list
            the first argument.
        dims : tuple of {str | None}
            The dimensions needed for the plotting function. ``None`` to indicate
            arbitrary dimensions.
        xax : None | categorial
            A model to divide ``y`` into different axes. ``xax`` is currently
            applied on the first level, i.e., it assumes that ``y``'s first
            dimension is cases.
        ds : None | Dataset
            Dataset containing data objects which are provided as :class:`str`.
        sub : None | str
            Index selecting a subset of cases.

        Notes
        -----
        Ndvar plotting functions above 1-d UTS level should support the following
        API:

         - simple NDVar: summary ``plot(meg)``
         - by dim: each case ``plot(meg, '.case')``
         - NDVar and xax argument: summary for each  ``plot(meg, subject)
         - nested list of layers (e.g., ttest results: [c1, c0, [c1-c0, p]])
        """
        if isinstance(y, cls):
            return y
        elif isinstance(y, AxisData):
            for layer in y.layers:
                dims = find_data_dims(layer.y, dims)
            return PlotData([y], dims)
        sub = assub(sub, ds)
        ys = y._default_plot_obj() if hasattr(y, '_default_plot_obj') else y

        if isinstance(ys, MNE_EPOCHS):
            # Epochs are Iterators over arrays
            ys = (asndvar(ys, sub, ds),)
        elif not isinstance(ys, (tuple, list, Iterator)):
            ys = (ys,)

        ax_names = None
        if xax is None:
            # y=[[y1], y2], xax=None
            axes = []
            for ax in ys:
                if ax is None:
                    axes.append(None)
                elif isinstance(ax, (tuple, list, Iterator)):
                    layers = []
                    for layer in ax:
                        layer = asndvar(layer, sub, ds)
                        agg, dims = find_data_dims(layer, dims)
                        layers.append(aggregate(layer, agg))
                    axes.append(layers)
                else:
                    ax = asndvar(ax, sub, ds)
                    agg, dims = find_data_dims(ax, dims)
                    layer = aggregate(ax, agg)
                    axes.append([layer])
            x_name = None
            # determine y names
            y_names = []
            for layers in axes:
                if layers is None:
                    continue
                for layer in layers:
                    if layer.name and layer.name not in y_names:
                        y_names.append(layer.name)
        elif any(isinstance(ax, (tuple, list, Iterator)) for ax in ys):
            raise TypeError(f"y={y!r}, xax={xax!r}: y can't be nested list if xax is specified, use single list")
        else:
            ys = [asndvar(layer, sub, ds) for layer in ys]
            y_names = [layer.name for layer in ys]
            layers = []
            if isinstance(xax, str) and xax.startswith('.'):
                # y=[y1, y2], xax='.dim'
                dimname = xax[1:]
                xax_dim = None
                for layer in ys:
                    dim = layer.get_dim(dimname)
                    if xax_dim is None:
                        xax_dim = dim
                    elif dim != xax_dim:
                        raise ValueError(f"y={y}, xax={xax!r}: dimension not equal on different y")
                    agg, dims = find_data_dims(layer, dims, dimname)
                    layers.append([aggregate(layer.sub(**{dimname: v}), agg) for v in dim])
                x_name = xax
                unit = f' {xax_dim._axis_unit}' if xax_dim._axis_unit else ''
                ax_names = [f'{v}{unit}' for v in xax_dim]
            else:
                # y=[y1, y2], xax=categorial
                xax = ascategorial(xax, sub, ds)
                xax_indexes = [xax == cell for cell in xax.cells]
                for layer in ys:
                    agg, dims = find_data_dims(layer, dims)
                    layers.append([aggregate(layer.sub(index), agg) for index in xax_indexes])
                x_name = xax.name
                ax_names = [cellname(cell) for cell in xax.cells]
            axes = list(zip(*layers))
        if len(y_names) == 0:
            y_name = None
        elif len(y_names) == 1:
            y_name = y_names[0]
        else:
            y_name = ', '.join(y_names)

        use_axes = [ax is not None for ax in axes]
        axes = [AxisData([LayerData(l) for l in ax]) for ax in axes if ax]
        title = frame_title(y_name, x_name)
        return cls(axes, dims, title, ax_names, use_axes)

    @classmethod
    def empty(cls, plots: Union[int, List[bool]], dims: Sequence[str], title: str):
        """Empty PlotData object that can be filled by appending to layers

        Parameters
        ----------
        plots : int | list of bool
            Number of plots, or list of booleans indicating for each plot
            whether its slot is used.
        dims : sequence of str
            Names of the dimensions.
        title : str
            Data description for the plot frame.
        """
        if isinstance(plots, int):
            plots = [AxisData([]) for _ in range(plots)]
        else:
            plots = [AxisData([]) if p else None for p in plots]
        return cls(plots, dims, title)

    @property
    def y0(self):
        for ax in self.plot_data:
            for layer in ax:
                return layer.y
        raise IndexError("No data")

    @property
    def default_y_label(self):
        "Y-label in case meas and unit are uninformative"
        names = {l.y.name for ax in self.plot_data for l in ax}
        names.discard(None)
        if len(names) == 1:
            return names.pop()
        return None

    @property
    def meas(self):
        meass = {l.y.info.get('meas') for ax in self.plot_data for l in ax}
        meass.discard(None)
        if len(meass) == 1:
            return meass.pop()
        return None

    @property
    def unit(self):
        units = {l.y.info.get('unit') for ax in self.plot_data for l in ax}
        units.discard(None)
        if len(units) == 1:
            return units.pop()
        return None

    @LazyProperty
    def data(self):
        "For backwards compatibility with nested list of NDVar"
        return [[l.y for l in self.axis_for_plot(i, PlotType.LEGACY)] for i in range(self.n_plots)]

    @LazyProperty
    def time_dim(self):
        "UTS dimension to expose for time slicer"
        time_dims = [l.y.get_dim('time') for ax in self.plot_data for l in ax.layers if l.y.has_dim('time')]
        if time_dims:
            return reduce(UTS._union, time_dims)

    def for_plot(self, plot_type: PlotType) -> 'PlotData':
        if self.plot_type == plot_type:
            return self
        axes = [ax.for_plot(plot_type) for ax in self.plot_data]
        return PlotData(axes, self.dims, self.frame_title, self._plot_names, self.plot_used, plot_type)

    @LazyProperty
    def plot_names(self):
        if self._plot_names:
            return self._plot_names
        names = []
        for layers in self.plot_data:
            for layer in layers:
                if layer.y.name:
                    names.append(layer.y.name)
                    break
            else:
                names.append(None)
        return names

    def axis_for_plot(self, ax: int, plot_type: PlotType) -> List[LayerData]:
        """Data for ``ax``

        Parameters
        ----------
        ax : int
            Index of the axes.
        plot_type : PlotType
            How to handle masked arrays and layers in plot data.
        """
        return self.plot_data[ax].for_plot(plot_type)

    def bin(self, bin_length, tstart, tstop):
        axes = [ax.bin(bin_length, tstart, tstop) for ax in self.plot_data]
        return PlotData(axes, self.dims, self.frame_title, self._plot_names, self.plot_used, self.plot_type)

    def sub_time(self, time: float, data_only: bool = False):
        axes = [ax.sub_time(time, data_only) for ax in self.plot_data]
        if data_only:
            return axes
        else:
            dims = [dim for dim in self.dims if dim != 'time']
            return PlotData(axes, dims, self.frame_title, self._plot_names, self.plot_used, self.plot_type)


def aggregate(y, agg):
    return y if agg is None else y.mean(agg)


class MatplotlibFrame:
    "Cf. _wxgui.mpl_canvas"
    def __init__(self, **fig_kwargs):
        "Create self.figure and self.canvas attributes and return the figure"
        from matplotlib import pyplot

        self._plt = pyplot
        self.figure = pyplot.figure(**fig_kwargs)
        self.canvas = self.figure.canvas
        self._background = None

    def Close(self):
        self._plt.close(self.figure)

    def SetStatusText(self, text):
        pass

    def Show(self):
        if mpl.get_backend() == 'WXAgg' and do_autorun():
            self._plt.show()

    def redraw(self, axes=[], artists=[]):
        "Adapted duplicate of mpl_canvas.FigureCanvasPanel"
        self.canvas.restore_region(self._background)
        for ax in axes:
            ax.draw_artist(ax)
            extent = ax.get_window_extent()
            self.canvas.blit(extent)
        for artist in artists:
            artist.axes.draw_artist(artist.axes)
            extent = artist.axes.get_window_extent()
            self.canvas.blit(extent)

    def store_canvas(self):
        self._background = self.canvas.copy_from_bbox(self.figure.bbox)


# MARK: figure composition

def _loc(name, size=(0, 0), title_space=0, frame=.01):
    """Convert loc argument to ``(x, y)`` of bottom left edge"""
    if isinstance(name, str):
        y, x = name.split()
    # interpret x
    elif len(name) == 2:
        x, y = name
    else:
        raise NotImplementedError("loc needs to be string or len=2 tuple/list")
    if isinstance(x, str):
        if x == 'left':
            x = frame
        elif x in ['middle', 'center', 'centre']:
            x = .5 - size[0] / 2
        elif x == 'right':
            x = 1 - frame - size[0]
        else:
            raise ValueError(x)
    # interpret y
    if isinstance(y, str):
        if y in ['top', 'upper']:
            y = 1 - frame - title_space - size[1]
        elif y in ['middle', 'center', 'centre']:
            y = .5 - title_space / 2. - size[1] / 2.
        elif y in ['lower', 'bottom']:
            y = frame
        else:
            raise ValueError(y)
    return x, y


def frame_title(y, x=None, xax=None):
    """Generate frame title from common data structure

    Parameters
    ----------
    y : data-obj | str
        Dependent variable.
    x : data-obj | str
        Predictor.
    xax : data-obj | str
        Grouping variable for axes.
    """
    if isdataobject(y):
        y = y.name
    if isdataobject(x):
        x = x.name
    if isdataobject(xax):
        xax = xax.name

    if xax is None:
        if x is None:
            return "%s" % (y,)
        else:
            return "%s ~ %s" % (y, x)
    elif x is None:
        return "%s | %s" % (y, xax)
    else:
        return "%s ~ %s | %s" % (y, x, xax)


class EelFigure:
    """Parent class for Eelbrain figures.

    In order to subclass:

     - find desired figure properties and then use them to initialize
       the _EelFigure superclass; then use the
       :py:attr:`_EelFigure.figure` and :py:attr:`_EelFigure.canvas` attributes.
     - end the initialization by calling `_EelFigure._show()`
     - add the :py:meth:`_fill_toolbar` method
    """
    _default_xlabel_ax = -1
    _default_ylabel_ax = 0
    _make_axes = True
    _can_set_time = False
    _can_set_vlim = False
    _can_set_ylim = False
    _can_set_xlim = False
    _use_frame = None
    _has_frame = False

    def __init__(self, data_desc, layout):
        """Parent class for Eelbrain figures.

        Parameters
        ----------
        data_desc : None | str
            Data description for frame title.
        layout : Layout
            Layout that determines figure dimensions.
        """
        name = self.__class__.__name__
        desc = layout.name or data_desc
        self._title = f'{name}: {desc}' if desc else name

        # Only the first time: respect previously set matplotlib backend
        if EelFigure._use_frame is None:
            if 'matplotlib.pyplot' in sys.modules:  # matplotlib backend has been set
                EelFigure._use_frame = not mpl.get_backend().endswith('inline')
            else:  # matplotlib backend has not been set
                EelFigure._use_frame = True

        # Use Eelbrain frame or pyplot
        if EelFigure._use_frame and CONFIG['eelbrain']:
            from .._wxgui import get_app
            from .._wxgui.mpl_canvas import CanvasFrame
            get_app()
            frame = CanvasFrame(title=self._title, eelfigure=self, **layout.fig_kwa())
            self._has_frame = True
        else:
            frame = MatplotlibFrame(**layout.fig_kwa())

        figure = frame.figure
        if layout.title:
            self._figtitle = figure.suptitle(layout.title)
        else:
            self._figtitle = None

        # make axes
        if self._make_axes:
            axes = layout.make_axes(figure)
        else:
            axes = []

        # store attributes
        self._frame = frame
        self.figure = figure
        self._axes = axes
        self.canvas = frame.canvas
        self._layout = layout
        self._last_draw_time = 1.
        self.__callback_key_press = {}
        self.__callback_key_release = {}

        # containers for hooks
        self._draw_hooks = []
        self._untight_draw_hooks = []

        # options
        self._draw_crosshairs = False
        self._crosshair_lines = None
        self._crosshair_axes = None

        # add callbacks
        self.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.canvas.mpl_connect('axes_leave_event', self._on_leave_axes)
        self.canvas.mpl_connect('resize_event', self._on_resize)
        self.canvas.mpl_connect('key_press_event', self._on_key_press)
        self.canvas.mpl_connect('key_release_event', self._on_key_release)

    def __repr__(self):
        title = self._frame.GetTitle() if self._has_frame else self._title
        return f'<{title}>'

    def _set_axtitle(self, axtitle, data=None, axes=None, names=None, **kwargs):
        """Set axes titles automatically

        Parameters
        ----------
        axtitle : bool | str | sequence of str
            Plot parameter.
        data : PlotData
            Plotted data (if available).
        axes : list of axes | int
            Axes for which to set title (default is self._axes). If an int,
            (n axes) the method does not set axes title but returns ``None``
            or a tuple of titles.
        names : sequence of str
            Instead of using ``epochs`` name attributes, use these names.
        ...
            Matplotlib ``Axes.set_title()`` parameters.
        """
        if axtitle is False or axtitle is None:
            return

        if axes is None:
            axes = self._axes

        naxes = axes if isinstance(axes, int) else len(axes)

        if axtitle is True and naxes == 1:
            return
        elif axtitle is True or isinstance(axtitle, str):
            if names is None:
                if data is None:
                    raise RuntimeError(f"data=None and names=None with axtitle={axtitle!r}")
                names = data.plot_names

            if axtitle is True:
                axtitle = names
            else:
                axtitle = (axtitle.format(name=n) if n else None for n in names)
        elif isinstance(axtitle, Iterable):
            if isinstance(axtitle, Iterator):
                axtitle = tuple(axtitle)
            if len(axtitle) != naxes:
                raise ValueError("axtitle needs to have one entry per axes. "
                                 "Got %r for %i axes" % (axtitle, naxes))
        else:
            raise TypeError("axtitle=%r" % (axtitle,))

        if isinstance(axes, int):
            return axtitle

        for title, ax in zip(axtitle, axes):
            ax.set_title(title, **kwargs)

    def _show(self, crosshair_axes=None):
        if self._layout.tight:
            self._tight()

        if crosshair_axes is None:
            self._crosshair_axes = self._axes
        else:
            self._crosshair_axes = crosshair_axes

        self.draw()

        # Allow hooks to modify figure after first draw
        need_redraw = any([func() for func in self._draw_hooks])
        if not self._layout.tight:
            need_redraw = any([func() for func in self._untight_draw_hooks]) or need_redraw
        if need_redraw:
            self.draw()

        if CONFIG['show'] and self._layout.show:
            self._frame.Show()
            if self._has_frame and do_autorun(self._layout.run):
                from .._wxgui import run
                run()

        if self._has_frame and not self.canvas._background:
            self._frame.store_canvas()

    def _tight(self):
        "Default implementation based on matplotlib"
        try:
            self.figure.tight_layout()
        except ValueError as exception:
            getLogger('eelbrain').debug('tight-layout: %s', exception)

        if self._figtitle:
            trans = self.figure.transFigure.inverted()
            extent = self._figtitle.get_window_extent(self.figure.canvas.renderer)
            bbox = trans.transform(extent)
            t_bottom = bbox[0, 1]
            self.figure.subplots_adjust(top=1 - 2 * (1 - t_bottom))

    def _on_key_press(self, event):
        if event.key in self.__callback_key_press:
            self.__callback_key_press[event.key](event)
            event.guiEvent.Skip(False)  # Matplotlib Skip()s all events

    def _on_key_release(self, event):
        if event.key in self.__callback_key_release:
            self.__callback_key_release[event.key](event)
            event.guiEvent.Skip(False)

    def _on_leave_axes(self, event):
        "Update the status bar when the cursor leaves axes"
        if self._frame is None:
            return
        self._frame.SetStatusText(self._on_leave_axes_status_text(event))
        if self._draw_crosshairs:
            self._remove_crosshairs(True)

    def _on_leave_axes_status_text(self, event):
        return '☺︎'

    def _on_motion(self, event):
        "Update the status bar for mouse movement"
        if self._frame is None:
            return
        redraw_axes = self._on_motion_sub(event)
        ax = event.inaxes
        # draw crosshairs
        if self._draw_crosshairs and ax in self._crosshair_axes:
            if self._crosshair_lines is None:
                self._crosshair_lines = tuple(
                    (ax.axhline(event.ydata, color='k'),
                     ax.axvline(event.xdata, color='k'))
                    for ax in self._crosshair_axes)
            else:
                for hline, vline in self._crosshair_lines:
                    hline.set_ydata([event.ydata, event.ydata])
                    vline.set_xdata([event.xdata, event.xdata])
            redraw_axes.update(self._crosshair_axes)
        # update status bar
        self._frame.SetStatusText(self._on_motion_status_text(event))
        # redraw
        self.canvas.redraw(redraw_axes)

    @staticmethod
    def _on_motion_status_text(event):
        ax = event.inaxes
        if ax:
            return ('x = %s, y = %s' % (
                ax.xaxis.get_major_formatter().format_data_short(event.xdata),
                ax.yaxis.get_major_formatter().format_data_short(event.ydata)))
        return ''

    def _on_motion_sub(self, event):
        "Subclass action on mouse motion, return set of axes to redraw"
        return set()

    def _on_resize(self, event):
        if self._layout.tight:
            self._tight()

    def _register_key(self, key, press=None, release=None):
        if press:
            if key in self.__callback_key_press:
                raise RuntimeError("Attempting to assign key press %r twice" %
                                   key)
            self.__callback_key_press[key] = press
        if release:
            if key in self.__callback_key_release:
                raise RuntimeError("Attempting to assign key release %r twice" %
                                   key)
            self.__callback_key_release[key] = release

    def _remove_crosshairs(self, draw=False):
        if self._crosshair_lines is not None:
            for hline, vline in self._crosshair_lines:
                hline.remove()
                vline.remove()
            self._crosshair_lines = None
            if draw:
                self.canvas.redraw(self._crosshair_axes)

    def _fill_toolbar(self, tb):
        """
        Add toolbar tools

        Subclasses should add their toolbar items in this function which
        is called by ``CanvasFrame.FillToolBar()``.
        """
        pass

    def close(self):
        "Close the figure."
        self._frame.Close()

    def _get_axes(self, axes):
        "Iterate over axes corresponding to ``axes`` parameter"
        if axes is None:
            return self._axes
        elif isinstance(axes, int):
            return self._axes[axes],
        else:
            return (self._axes[i] for i in axes)

    def _configure_xaxis_dim(self, dim, label, xticklabels, axes=None,
                             scalar=True):
        """Configure the x-axis based on a dimension

        Parameters
        ----------
        dim : Dimension
            The dimension assigned to the axis.
        label : bool | str
            Axis label.
        xticklabels : bool | int | list of int
            Specify which axes should be annotated with x-axis tick labels.
            Use ``int`` for a single axis (default ``-1``), a sequence of
            ``int`` for multiple specific axes, or ``bool`` for all/none.
        axes : list of Axes
            Axes which to format (default is EelFigure._axes)
        """
        if axes is None:
            axes = self._axes
        formatter, locator, label = dim._axis_format(scalar, label)

        n_axes = len(axes)
        if isinstance(xticklabels, bool):
            add_tick_labels = [xticklabels] * n_axes
        else:
            if isinstance(xticklabels, int):
                tick_label_i = (xticklabels,)
            else:
                try:
                    tick_label_i = map(int, xticklabels)
                except TypeError:
                    raise TypeError("xticklabels=%r" % (xticklabels,))
            add_tick_labels = [False] * n_axes
            for i in tick_label_i:
                if i >= n_axes or i < -n_axes:
                    raise ValueError("xticklabels=%r for a plot with %i axes"
                                     % (xticklabels, n_axes))
                add_tick_labels[i] = True

        for ax, add_tick_labels_ in zip(axes, add_tick_labels):
            if locator:
                ax.xaxis.set_major_locator(locator)

            if formatter:
                ax.xaxis.set_major_formatter(formatter)

            if not add_tick_labels_:
                ax.tick_params(labelbottom=False)

        if label:
            self.set_xlabel(label)

    def _configure_xaxis(self, v, label, axes=None):
        if axes is None:
            axes = self._axes
        formatter, label = find_axis_params_data(v, label)
        for ax in axes:
            ax.xaxis.set_major_formatter(formatter)

        if label:
            self.set_xlabel(label)

    def _configure_yaxis_dim(self, epochs, dim, label, axes=None, scalar=True):
        "Configure the y-axis based on a dimension (see ._configure_xaxis_dim)"
        if axes is None:
            axes = self._axes

        labels = []
        for ax, layers in zip(axes, epochs):
            formatter, locator, label_ = layers[0].get_dim(
                dim)._axis_format(scalar, label)
            if locator:
                ax.yaxis.set_major_locator(locator)
            if formatter:
                ax.yaxis.set_major_formatter(formatter)
            labels.append(label_)

        if any(labels):
            if len(set(labels)) == 1:
                self.set_ylabel(labels[0])
            else:
                for ax, label in zip(axes, labels):
                    if label:
                        self.set_ylabel(label, ax)

    def _configure_yaxis(self, data, label, axes=None):
        if axes is None:
            axes = self._axes
        formatter, label = find_axis_params_data(data, label)
        for ax in axes:
            ax.yaxis.set_major_formatter(formatter)

        if isinstance(label, str):
            self.set_ylabel(label)
        elif isinstance(label, Iterable):
            for i, l in enumerate(label):
                self.set_ylabel(l, i)

    def draw(self):
        "(Re-)draw the figure (after making manual changes)."
        if self._frame is None:
            return
        t0 = time.time()
        self._frame.canvas.draw()
        self._last_draw_time = time.time() - t0

    def draw_crosshairs(self, enable=True):
        """Draw crosshairs under the cursor

        Parameters
        ----------
        enable : bool
            Enable drawing crosshairs (default True, set to False to disable).
        """
        self._draw_crosshairs = enable
        if not enable:
            self._remove_crosshairs(True)

    def _asfmtext(self):
        return self.image()

    def image(self, name=None, format=None):
        """Create FMTXT Image from the figure

        Parameters
        ----------
        name : str
            Name for the file (without extension; default is 'image').
        format : str
            File format (default 'png').

        Returns
        -------
        image : fmtxt.Image
            Image FMTXT object.
        """
        if format is None:
            format = CONFIG['format']

        image = Image(name, format)
        self.figure.savefig(image, format=format)
        return image

    def save(self, *args, **kwargs):
        "Short-cut for Matplotlib's :meth:`~matplotlib.figure.Figure.savefig()`"
        self.figure.savefig(*args, **kwargs)

    def add_hline(self, y, axes=None, *args, **kwargs):
        """Draw a horizontal line on one or more axes

        Parameters
        ----------
        y : scalar
            Level at which to draw the line.
        axes : int | list of int
            Which axes to mark (default is all axes).
        ...
            :meth:`matplotlib.axes.Axes.axhline` parameters.


        Notes
        -----
        See Matplotlib's :meth:`matplotlib.axes.Axes.axhline` for more
        arguments.
        """
        for ax in self._get_axes(axes):
            ax.axhline(y, *args, **kwargs)
        self.draw()

    def add_hspan(self, bottom, top, axes=None, *args, **kwargs):
        """Draw a horizontal bar on one or more axes

        Parameters
        ----------
        bottom : scalar
            Bottom end of the horizontal bar.
        top : scalar
            Top end of the horizontal bar.
        axes : int | list of int
            Which axes to mark (default is all axes).
        ...
            :meth:`matplotlib.axes.Axes.axvspan` parameters.


        Notes
        -----
        See Matplotlib's :meth:`matplotlib.axes.Axes.axhspan` for more
        arguments.
        """
        for ax in self._get_axes(axes):
            ax.axhspan(bottom, top, *args, **kwargs)
        self.draw()

    def add_vline(self, x, axes=None, *args, **kwargs):
        """Draw a vertical line on one or more axes

        Parameters
        ----------
        x : scalar
            Value at which to place the vertical line.
        axes : int | list of int
            Which axes to mark (default is all axes).
        ...
            :meth:`matplotlib.axes.Axes.axvspan` parameters.


        Notes
        -----
        See Matplotlib's :meth:`matplotlib.axes.Axes.axvline` for more
        arguments.
        """
        for ax in self._get_axes(axes):
            ax.axvline(x, *args, **kwargs)
        self.draw()

    def add_vspan(self, xmin, xmax, axes=None, *args, **kwargs):
        """Draw a vertical bar on one or more axes

        Parameters
        ----------
        xmin : scalar
            Start value on the x-axis.
        xmax : scalar
            Last value on the x-axis.
        axes : int | list of int
            Which axes to mark (default is all axes).
        ...
            :meth:`matplotlib.axes.Axes.axvspan` parameters.


        Notes
        -----
        See Matplotlib's :meth:`matplotlib.axes.Axes.axvspan` for more
        arguments.
        """
        for ax in self._get_axes(axes):
            ax.axvspan(xmin, xmax, *args, **kwargs)
        self.draw()

    def set_name(self, name):
        """Set the figure window title"""
        plot_name = self.__class__.__name__
        self._frame.SetTitle(f'{plot_name}: {name}' if name else plot_name)

    def set_xtick_rotation(self, rotation):
        """Rotate every x-axis tick-label by an angle (counterclockwise, in degrees)

        Parameters
        ----------
        rotation : scalar
            Counterclockwise rotation angle, in degrees.
        """
        for ax in self._axes:
            for t in ax.get_xticklabels():
                t.set_rotation(rotation)
        self.draw()

    def set_xlabel(self, label, ax=None):
        """Set the label for the x-axis

        Parameters
        ----------
        label : str
            X-axis label.
        ax : int
            Axis on which to set the label (default is usually the last axis).
        """
        if ax is None:
            ax = self._default_xlabel_ax
        self._axes[ax].set_xlabel(label)

    def set_ylabel(self, label, ax=None):
        """Set the label for the y-axis

        Parameters
        ----------
        label : str
            Y-axis label.
        ax : int
            Axis on which to set the label (default is usually the first axis).
        """
        if ax is None:
            ax = self._axes[self._default_ylabel_ax]
        elif isinstance(ax, int):
            ax = self._axes[ax]
        ax.set_ylabel(label)


class BaseLayout:
    def __init__(self, h, w, dpi, tight, show, run, autoscale, title, name):
        self.h = h
        self.w = w
        self.dpi = dpi or mpl.rcParams['figure.dpi']
        self.tight = tight
        self.show = show
        self.run = run
        self.autoscale = autoscale
        self.title = title
        self.name = name or title

    def fig_kwa(self):
        out = {'figsize': (self.w, self.h), 'dpi': self.dpi}
        if CONFIG['figure_background'] is not False:
            out['facecolor'] = CONFIG['figure_background']
        return out

    def make_axes(self, figure):
        raise NotImplementedError

    @staticmethod
    def _format_axes(ax, frame, yaxis):
        if frame == 't':
            ax.tick_params(direction='inout', bottom=False, top=True,
                           left=False, right=True, labelbottom=True,
                           labeltop=False, labelleft=True,
                           labelright=False)
            ax.spines['right'].set_position('zero')
            ax.spines['left'].set_visible(False)
            ax.spines['top'].set_position('zero')
            ax.spines['bottom'].set_visible(False)
        elif frame == 'none':
            ax.axis('off')
        elif not frame:
            ax.yaxis.set_ticks_position('left')
            ax.spines['right'].set_visible(False)
            ax.xaxis.set_ticks_position('bottom')
            ax.spines['top'].set_visible(False)

        if not yaxis:
            ax.yaxis.set_ticks(())
            ax.spines['left'].set_visible(False)


def resolve_plot_rect(w, h, dpi):
    # infer figure dimensions from screen size
    w_applies = w is not None and w <= 0
    h_applies = h is not None and h <= 0
    if w_applies or h_applies:
        from .._wxgui import wx, get_app

        get_app()
        effective_dpi = dpi or mpl.rcParams['figure.dpi']
        display_w, display_h = wx.GetDisplaySize()
        if h_applies:
            effective_display_h = display_h - 50
            h = effective_display_h / effective_dpi + h
        if w_applies:
            w = display_w / effective_dpi + w
    return w, h


class LayoutDim:
    "Helper function to determine figure spacing"
    _properties = ('total', 'first', 'space', 'last', 'ax')
    _equations = dict(
        ax='(total - first - last - (n_ax - 1) * space) / n_ax',
        total='first + n_ax * ax + (n_ax - 1) * space + last',
        first='total - n_ax * ax  - (n_ax - 1) * space - last',
        last='total - first - n_ax * ax - (n_ax - 1) * space',
        space='(total - first - n_ax * ax - last) / (n_ax - 1)',
    )

    def __init__(self, n_ax, total, ax, first, space, last, ax_default, first_default, space_default, last_default):
        if space is None and n_ax == 1:
            space = 0.
        values = {'total': total, 'first': first, 'space': space, 'last': last,
                  'ax': ax, 'n_ax': n_ax}
        defaults = {'first': first_default, 'space': space_default,
                    'last': last_default, 'ax': ax_default}
        for i, p in enumerate(self._properties):
            if values[p] is None:
                for p2 in self._properties[i + 1:]:
                    if values[p2] is None:
                        values[p2] = defaults[p2]
                values[p] = eval(self._equations[p], values)
                break
        self.total = values['total']
        self.ax = values['ax']
        self.first = values['first']
        self.space = values['space']
        self.last = values['last']


class Layout(BaseLayout):
    """Layout for figures with several axes of the same size"""
    _default_margins = {'left': 0.4, 'bottom': 0.5, 'right': 0.05, 'top': 0.05,
                        'wspace': 0.1, 'hspace': 0.1}

    def __init__(self, nax, ax_aspect, axh_default, tight=True, title=None,
                 h=None, w=None, axh=None, axw=None, nrow=None, ncol=None,
                 dpi=None, margins=None, show=True, run=None,
                 frame=True, yaxis=True, share_axes=False, autoscale=False,
                 name=None):
        """Create a grid of axes based on variable parameters.

        Parameters
        ----------
        nax : int | list of bool
            Number of axes required. If provided as a list, axes are only added
            for items where ``item`` is True.
        ax_aspect : scalar
            Width / height aspect of the axes.
        axh_default : scalar
            The default axes height if it can not be determined from the other
            parameters.
        tight : bool
            Rescale axes so that the space in the figure is used optimally
            (default True).
        title : str
            Figure title.
        h : scalar
            Height of the figure.
        w : scalar
            Width of the figure.
        axh : scalar
            Height of the axes.
        axw : scalar
            Width of the axes.
        nrow : int
            Set a limit to the number of rows (default is no limit).
        ncol : int
            Set a limit to the number of columns (defaut is no limit). If
            neither nrow or ncol is specified, a square layout is preferred.
        dpi : int
            DPI for the figure (default is to use matplotlib rc parameters).
        margins : dict
            Absolute subplot parameters (in inches). Implies ``tight=False``. 
            If ``margins`` is specified, ``axw`` and ``axh`` are interpreted 
            exclusive of the margins, i.e., ``axh=2, margins={'top': .5}`` for
            a plot with one axes will result in a total height of 2.5.
        show : bool
            Show the figure in the GUI (default True). Use False for creating
            figures and saving them without displaying them on the screen.
        run : bool
            Run the Eelbrain GUI app (default is True for interactive plotting and
            False in scripts).
        frame : bool | 't' | 'none'
            Draw frame around axes: 
            - True: all four spines
            - False: only spines with ticks
            - 't': spines at x=0 and y=0
            - 'none': no spines at all
        """
        if h and axh:
            if h < axh:
                raise ValueError("h < axh")
        if w and axw:
            if w < axw:
                raise ValueError("w < axw")
        w, h = resolve_plot_rect(w, h, dpi)

        self.w_fixed = w if w is not None else axw
        self._margins_arg = margins

        if margins is True:
            use_margins = True
            tight = False
            margins = self._default_margins.copy()
        elif margins is not None:
            use_margins = True
            tight = False
            margins = dict(margins)
            invalid = set(margins).difference(self._default_margins)
            if invalid:
                keys = ', '.join(map(repr, invalid))
                raise ValueError(f"margins={margins!r}: Unknown keys {keys}")
        else:
            margins = {k: 0 for k in self._default_margins}
            use_margins = False

        h_is_implicit = h is None
        w_is_implicit = w is None

        if nax is None:
            axes = None
        elif isinstance(nax, int):
            axes = list(range(nax))
        elif isinstance(nax, (list, tuple)):
            axes = [i for i, ax in enumerate(nax) if ax]
            nax = len(nax)
        else:
            raise TypeError("nax=%r" % (nax,))

        if not nax:
            if w is None:
                if h is None:
                    h = axh_default
                w = ax_aspect * h
            elif h is None:
                h = w / ax_aspect
        elif nax == 1:
            ncol = nrow = 1
        elif nrow is None and ncol is None:
            if w and axw:
                ncol = math.floor(w / axw)
            elif h and axh:
                nrow = math.floor(h / axh)
            elif w:
                if axh:
                    ncol = round(w / (axh * ax_aspect))
                else:
                    ncol = round(w / (axh_default * ax_aspect))
                ncol = max(1, min(nax, ncol))
            elif h:
                if axw:
                    nrow = round(h / (axw / ax_aspect))
                else:
                    nrow = round(h / axh_default)
                nrow = max(1, min(nax, nrow))
            elif axh or axw:
                if not axh:
                    axh = axw / ax_aspect
                nrow = min(nax, math.floor(defaults['maxh'] / axh))
            else:
                # default: minimum number of columns (max number of rows)
                hspace = margins.get('hspace', 0)
                maxh = defaults['maxh'] - margins.get('top', 0) - margins.get('bottom', 0) + hspace
                axh_with_space = axh_default + hspace
                nrow = min(nax, math.floor(maxh / axh_with_space))
                # test width
                ncol = math.ceil(nax / nrow)
                wspace = margins.get('wspace', 0)
                maxw = defaults['maxw'] - margins.get('left', 0) - margins.get('right', 0) + wspace
                axw_with_space = axh_default * ax_aspect + wspace
                if ncol * axw_with_space > maxw:
                    # nrow/ncol proportional to (maxh / axh) / (maxw / axw)
                    ratio = (maxh / axh_with_space) / (maxw / axw_with_space)
                    # nax = ncol * (ncol * ratio)
                    # ncol = sqrt(nax / ratio)
                    ncol = math.floor(math.sqrt(nax / ratio))
                    nrow = math.ceil(nax / ncol)
                    axh = (maxh - nrow * hspace) / nrow
                    axw = axh * ax_aspect

        if nax:
            if nrow is None:
                ncol = min(nax, ncol)
                nrow = int(math.ceil(nax / ncol))
            elif ncol is None:
                nrow = min(nax, nrow)
                ncol = int(math.ceil(nax / nrow))

            if axw:
                axh_default = axw / ax_aspect
            elif w:
                axh_default = w / ncol / ax_aspect
            h_dim = LayoutDim(
                nrow, h, axh, margins.get('top'), margins.get('hspace'),
                margins.get('bottom'), axh_default, self._default_margins['top'],
                self._default_margins['hspace'], self._default_margins['bottom']
            )
            w_dim = LayoutDim(
                ncol, w, axw, margins.get('left'), margins.get('wspace'),
                margins.get('right'), h_dim.ax * ax_aspect, self._default_margins['left'],
                self._default_margins['wspace'], self._default_margins['right']
            )
            h = h_dim.total
            w = w_dim.total
            axh = h_dim.ax
            axw = w_dim.ax
            margins = {
                'top': h_dim.first, 'bottom': h_dim.last, 'hspace': h_dim.space,
                'left': w_dim.first, 'right': w_dim.last, 'wspace': w_dim.space}
            h_is_implicit = w_is_implicit = False

        if nax:
            nrow = int(nrow)
            ncol = int(ncol)
            if w is None:
                w = axw * ncol
            if h is None:
                h = axh * nrow

        if h_is_implicit:
            hspace = 0 if nrow is None else margins['hspace'] * (nrow - 1)
            h += margins['bottom'] + hspace + margins['top']
        if w_is_implicit:
            wspace = 0 if ncol is None else margins['wspace'] * (ncol - 1)
            w += margins['left'] + wspace + margins['right']

        BaseLayout.__init__(self, h, w, dpi, tight, show, run, autoscale,
                            title, name)
        self.nax = nax
        self.axes = axes
        self.axh = axh
        self.axw = axw
        self.nrow = nrow
        self.ncol = ncol
        self.frame = frame
        self.yaxis = yaxis
        self.share_axes = share_axes
        self.margins = margins if use_margins else None

    def fig_kwa(self):
        out = BaseLayout.fig_kwa(self)

        if self.margins:  # absolute subplot parameters
            out['subplotpars'] = SubplotParams(
                self.margins['left'] / self.w,
                self.margins['bottom'] / self.h,
                1 - self.margins['right'] / self.w,
                1 - self.margins['top'] / self.h,
                # space expressed as a fraction of the average axis height/width
                self.margins['wspace'] / self.axw,
                self.margins['hspace'] / self.axh)

        return out

    def make_axes(self, figure):
        if not self.nax:
            return []
        axes = []
        kwargs = {}
        for i in self.axes:
            ax = figure.add_subplot(self.nrow, self.ncol, i + 1, autoscale_on=self.autoscale, **kwargs)
            axes.append(ax)
            if self.share_axes:
                kwargs.update(sharex=ax, sharey=ax)
            self._format_axes(ax, self.frame, self.yaxis)
        return axes


class ImLayout(Layout):
    """Layout subclass for axes without space

    Make sure to specify the ``margins`` parameter for absolute spacing
    """
    _default_margins = {'left': 0, 'bottom': 0, 'right': 0, 'top': 0,
                        'wspace': 0, 'hspace': 0}

    def __init__(self, nax, ax_aspect, axh_default, margins, default_margins,
                 title=None, *args, **kwargs):
        if margins is None:
            margins = default_margins
        elif isinstance(margins, dict):
            for k in default_margins:
                if k not in margins:
                    margins[k] = default_margins[k]
        else:
            raise TypeError("margins=%r; needs to be a dict" % (margins,))
        Layout.__init__(self, nax, ax_aspect, axh_default, False, title, *args,
                        margins=margins, **kwargs)

    def make_axes(self, figure):
        axes = []
        for i in self.axes:
            ax = figure.add_subplot(self.nrow, self.ncol, i + 1,
                                    autoscale_on=self.autoscale)
            ax.axis('off')
            axes.append(ax)
        return axes


class VariableAspectLayout(BaseLayout):
    """Layout with a fixed number of columns that differ in spacing

    Axes are originally created to fill the whole rectangle allotted to them.
    Developed for TopoButterfly plot: one variable aspect butterfly plot, and
    one square topomap plot.

    Parameters
    ----------
    nrow : int
        Number of rows.
    axh_default : scalar
        Default row height.
    w_default : scalar
        Default figure width.
    aspect : tuple of {scalar | None}
        Axes aspect ratio (w/h) for each column; None for axes with flexible
        width.
    ax_kwargs : tuple of dict
        Parameters for :meth:`figure.add_axes` for each column.
    ax_frames : tuple of str
        ``frame`` parameter for :meth:`._format_axes` for each column.
    row_titles : sequence of {str | None}
        One title per row.
    """
    def __init__(self, nrow, axh_default, w_default, aspect=(None, 1),
                 ax_kwargs=None, ax_frames=None, row_titles=None,
                 title=None, h=None, w=None, axh=None,
                 dpi=None, show=True, run=None, frame=True, yaxis=True,
                 autoscale=False, name=None):
        w, h = resolve_plot_rect(w, h, dpi)
        self.w_fixed = w

        if axh and h:
            raise ValueError("h and axh can not be specified both at the same time")
        elif h:
            axh = h / nrow
        elif axh:
            h = nrow * axh
        else:
            axh = axh_default
            h = nrow * axh

        if w is None:
            w = w_default

        if ax_kwargs is None:
            ax_kwargs = [{}] * len(aspect)
        if ax_frames is None:
            ax_frames = [True] * len(aspect)

        BaseLayout.__init__(self, h, w, dpi, False, show, run, autoscale,
                            title, name)
        self.nax = nrow * len(aspect)
        self.axh = axh
        self.nrow = nrow
        self.ncol = len(aspect)
        self.frame = frame
        self.yaxis = yaxis
        self.share_axes = False
        self.row_titles = row_titles
        self.aspect = aspect
        self.n_flexible = self.aspect.count(None)
        self.ax_kwargs = ax_kwargs
        self.ax_frames = ax_frames

        # Compute axes outlines for given height and width
        h = self.h
        w = self.w
        text_buffer = 20 * POINT

        # buffers for legends
        left_buffer = text_buffer * (3 + (self.row_titles is not None))
        bottom_buffer = text_buffer * 2
        top_buffer = text_buffer * (1 + 2 * bool(self.title))

        # rectangle base in inches
        axh = (h - bottom_buffer - top_buffer) / self.nrow
        axws = [None if a is None else a * axh for a in self.aspect]
        fixed = sum(axw for axw in axws if axw is not None)
        w_free = (w - fixed - left_buffer) / self.n_flexible
        widths = [w_free if axw is None else axw for axw in axws]
        lefts = (sum(widths[:i]) + left_buffer for i in range(len(widths)))
        bottoms = (i * axh + bottom_buffer for i in range(self.nrow - 1, -1, -1))

        # convert to figure coords
        height = axh / h
        lefts_ = [l / w for l in lefts]
        widths_ = [w_ / w for w_ in widths]
        bottoms_ = [b / h for b in bottoms]

        # rectangles:  (left, bottom, width, height)
        self._ax_rects = [[(l, bottom, w, height) for l, w in zip(lefts_, widths_)] for bottom in bottoms_]

    def make_axes(self, figure):
        axes = []
        for row, row_rects in enumerate(self._ax_rects):
            for rect, kwa, frame in zip(row_rects, self.ax_kwargs, self.ax_frames):
                ax = figure.add_axes(rect, autoscale_on=self.autoscale, **kwa)
                self._format_axes(ax, frame, True)
                axes.append(ax)

            if self.row_titles and self.row_titles[row]:
                bottom, height = rect[1], rect[3]
                figure.text(0, bottom + height / 2, self.row_titles[row],
                            ha='left', va='center', rotation='vertical')

        # id axes for callbacks
        for i, ax in enumerate(axes):
            ax.id = i
        return axes


class ColorBarMixin:
    """Colorbar toolbar button mixin

    Parameters
    ----------
    param_func : func
        Function that returns color-bar parameters.
    """
    def __init__(self, param_func, data):
        self.__get_params = param_func
        if data is None:
            self.__unit = None
            self.__label = 'colormap'
        else:
            self.__unit = data.info.get('unit', None)
            _, self.__label = find_axis_params_data(data, True)

    def _fill_toolbar(self, tb):
        from .._wxgui import wx, ID, Icon

        tb.AddTool(ID.PLOT_COLORBAR, "Plot Colorbar", Icon("plot/colorbar"))
        tb.Bind(wx.EVT_TOOL, self.__OnPlotColorBar, id=ID.PLOT_COLORBAR)

    def __OnPlotColorBar(self, event):
        return self.plot_colorbar()

    def plot_colorbar(self, label=True, label_position=None,
                      label_rotation=None, clipmin=None, clipmax=None,
                      orientation='horizontal', *args, **kwargs):
        """Plot a colorbar corresponding to the displayed data

        Parameters
        ----------
        label : str | bool
            Label for the x-axis (default is based on the data).
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

        Returns
        -------
        colorbar : plot.ColorBar
            ColorBar plot object.
        """
        from . import ColorBar
        if label is True:
            label = self.__label
        cmap, vmin, vmax = self.__get_params()
        return ColorBar(cmap, vmin, vmax, label, label_position, label_rotation,
                        clipmin, clipmax, orientation, self.__unit, (), *args,
                        **kwargs)


class ColorMapMixin(ColorBarMixin):
    """takes care of color-map and includes color-bar"""
    _can_set_vlim = True

    def __init__(self, epochs, cmap, vmax, vmin, contours, plots):
        ColorBarMixin.__init__(self, self.__get_cmap_params, epochs[0][0])
        self.__plots = plots  # can be empty list at __init__
        self._cmaps = find_fig_cmaps(epochs, cmap)
        self._vlims = find_fig_vlims(epochs, vmax, vmin, self._cmaps)
        self._contours = find_fig_contours(epochs, self._vlims, contours)
        self._first_meas = epochs[0][0].info.get('meas')

    def __get_cmap_params(self):
        return (self._cmaps[self._first_meas],) + self._vlims[self._first_meas]

    def add_contour(self, level, color='k', meas=None):
        """Add a contour line

        Parameters
        ----------
        level : scalar
            The value at which to draw the contour.
        color : matplotlib color
            The color of the contour line.
        meas : str
            The measurement for which to add a contour line (default is the
            measurement plotted first).
        """
        if meas is None:
            meas = self._first_meas

        for p in self.__plots:
            p.add_contour(meas, level, color)
        self.draw()

    def set_cmap(self, cmap, meas=None):
        """Change the colormap in the array plots

        Parameters
        ----------
        cmap : str | colormap
            New colormap.
        meas : None | str
            Measurement to which to apply the colormap. With None, it is
            applied to all.
        """
        if meas is None:
            meas = self._first_meas

        for p in self.__plots:
            p.set_cmap(cmap, meas)
        self._cmaps[meas] = cmap
        self.draw()

    def set_vlim(self, v=None, vmax=None, meas=None):
        """Change the colormap limits

        If the limit is symmetric, use ``set_vlim(vlim)``; if it is not, use
        ``set_vlim(vmin, vmax)``.

        Parameters
        ----------
        v : scalar
            If this is the only value specified it is interpreted as the upper
            end of the scale, and the lower end is determined based on
            the colormap to be ``-v`` or ``0``. If ``vmax`` is also specified,
            ``v`` specifies the lower end of the scale.
        vmax : scalar (optional)
            Upper end of the color scale.
        meas : str (optional)
            Measurement type to apply (default is the first one found).
        """
        if meas is None:
            meas = self._first_meas
        elif meas not in self._cmaps:
            raise ValueError("meas=%r" % (meas,))

        if vmax is None:
            vmin, vmax = fix_vlim_for_cmap(None, abs(v), self._cmaps[meas])
        else:
            vmin = v

        for p in self.__plots:
            p.set_vlim(vmin, vmax, meas)
        self._vlims[meas] = vmin, vmax

        if self._can_set_ylim:
            self.set_ylim(vmin, vmax)
        else:
            self.draw()

    def get_vlim(self, meas=None):
        "Retrieve colormap value limits as ``(vmin, vmax)`` tuple"
        if meas is None:
            meas = self._first_meas
        return self._vlims[meas]


class LegendMixin:
    __choices = ('invisible', 'separate window', 'draggable', 'upper right',
                 'upper left', 'lower left', 'lower right', 'right',
                 'center left', 'center right', 'lower center', 'upper center',
                 'center')
    __args = (False, 'fig', 'draggable', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    _has_frame = None

    def __init__(self, loc, handles, labels=None):
        """Legend toolbar menu mixin

        Parameters
        ----------
        loc : str | int | 'fig' | None
            Matplotlib figure legend location argument or 'fig' to plot the
            legend in a separate figure.
        handles : dict
            {cell: handle} dictionary.
        labels : dict
            Dictionary with labels for cells.
        """
        self.__handles = handles
        self.legend = None
        self.__labels = copy(labels)
        if self.__handles:
            self.plot_legend(loc, labels)

    def _fill_toolbar(self, tb):
        from .._wxgui import wx

        choices = [name.title() for name in self.__choices]
        self.__ctrl = wx.Choice(tb, choices=choices, name='Legend')
        tb.AddControl(self.__ctrl, "Legend")
        self.__ctrl.Bind(wx.EVT_CHOICE, self.__OnChoice, source=self.__ctrl)

    def __OnChoice(self, event):
        self.__plot(self.__args[event.GetSelection()])

    def plot_legend(self, loc='fig', labels=None, *args, **kwargs):
        """Plot the legend (or remove it from the figure).

        Parameters
        ----------
        loc : False | 'fig' | 'draggable' | str | int
            Where to plot the legend (see Notes; default 'fig').
        labels : dict
            Dictionary with alternate labels for all cells.
        ... :
            Parameters for :class:`eelbrain.plot.Legend`.

        Returns
        -------
        legend_figure : None | legend
            If loc=='fig' the Figure, otherwise None.

        Notes
        -----
        legend content can be modified through the figure's
        ``legend_handles`` and ``legend_labels`` attributes.

        Possible values for the ``loc`` argument:

        ``False``:
            Make the current legend invisible
        'fig':
            Plot the legend in a new figure
        'draggable':
            The legend can be dragged to the desired position with the mouse
            pointer.
        str | int:
            Matplotlib position argument: plot the legend on the figure


        Matplotlib Position Arguments:

         - 'upper right'  : 1,
         - 'upper left'   : 2,
         - 'lower left'   : 3,
         - 'lower right'  : 4,
         - 'right'        : 5,
         - 'center left'  : 6,
         - 'center right' : 7,
         - 'lower center' : 8,
         - 'upper center' : 9,
         - 'center'       : 10,
        """
        if loc in self.__choices:
            choice = self.__choices.index(loc)
            arg = self.__args[choice]
        elif loc is None:
            choice = 0
            arg = False
        elif loc not in self.__args:
            raise ValueError(f"Invalid legend location: {loc!r}; use one of: {enumeration(map(repr, self.__choices), 'or')}")
        else:
            choice = self.__args.index(loc)
            arg = loc

        if self._has_frame:
            self.__ctrl.SetSelection(choice)

        if arg is not False:
            return self.__plot(loc, labels, *args, **kwargs)

    def save_legend(self, *args, **kwargs):
        """Save the legend as image file

        Parameters
        ----------
        ... :
            Parameters for Matplotlib's figure.savefig()
        """
        p = self.plot_legend(show=False)
        p.save(*args, **kwargs)
        p.close()

    def __plot(self, loc, labels=None, *args, **kwargs):
        if loc and self.__handles:
            if labels is None:
                labels = self.__labels
            else:
                self.__labels = copy(labels)

            if labels is None:
                cells = list(self.__handles)
                labels = [cellname(cell) for cell in cells]
            elif isinstance(labels, dict):
                cells = list(labels.keys())
                labels = list(labels.values())
            else:
                raise TypeError(f"labels={labels!r}; needs to be dict")
            handles = [self.__handles[cell] for cell in cells]
            if loc == 'fig':
                return Legend(handles, labels, *args, **kwargs)
            else:
                # take care of old legend
                if self.legend is not None and loc == 'draggable':
                    self.legend.set_draggable(True)
                elif self.legend is not None:
                    self.legend.remove()
                elif loc == 'draggable':
                    self.legend = self.figure.legend(handles, labels, loc=1)
                    self.legend.set_draggable(True)

                if loc != 'draggable':
                    self.legend = self.figure.legend(handles, labels, loc=loc)
                self.draw()
        elif self.legend is not None:
            self.legend.remove()
            self.legend = None
            self.draw()
        elif not self.__handles:
            raise RuntimeError("No handles to produce legend.")


class Legend(EelFigure):

    def __init__(self, handles, labels, *args, **kwargs):
        layout = Layout(0, 1, 2, False, *args, **kwargs)
        EelFigure.__init__(self, None, layout)

        self.legend = self.figure.legend(handles, labels, loc=2)

        # resize figure to match legend
        if not self._layout.w_fixed:
            self.draw()
            bb = self.legend.get_window_extent()
            w0, h0 = self._frame.GetSize()
            h = int(h0 + bb.x0 - bb.y0)
            w = int(bb.x0 + bb.x1)
            self._frame.SetSize((w, h))

        self._show()


class TimeController:
    # Link plots that have the TimeSlicer mixin
    def __init__(self, t=0, fixate=False):
        self._plots = []  # list of weakref to plots
        self.current_time = t
        self.fixate = fixate

    def add_plot(self, plot: 'TimeSlicer'):
        if plot._time_controller is None:
            t = plot._validate_time(self.current_time)
            plot._set_time(t, self.fixate)
            self._plots.append(weakref.ref(plot))
            plot._time_controller = self
        elif plot._time_controller is not self:
            self.merge(plot._time_controller)

    def iter_plots(self):
        needs_cleaning = False
        for ref in self._plots:
            plot = ref()
            if plot is None:
                needs_cleaning = True
            else:
                yield plot
        if needs_cleaning:
            self._plots = [ref for ref in self._plots if ref() is not None]

    def merge(self, time_controller):
        "Merge another TimeController into self"
        for plot in time_controller.iter_plots():
            plot._time_controller = None
            self.add_plot(plot)

    def set_time(self, t, fixate):
        if t == self.current_time and fixate == self.fixate:
            return
        for p in self.iter_plots():
            t = p._validate_time(t)
        for p in self.iter_plots():
            p._update_time_wrapper(t, fixate)
        self.current_time = t
        self.fixate = fixate

    def set_xlim(self, xmin, xmax):
        for p in self.iter_plots():
            if isinstance(p, XAxisMixin):
                p._set_xlim(xmin, xmax, draw=True)


class TimeSlicer:
    # Interface to link time axes of multiple plots.
    # update data in a child plot of time-slices
    _time_dim = None
    _current_time = None
    _display_time_in_frame_title = False

    def __init__(self, time_dim=None, time_fixed=False):
        if time_dim is not None:
            self._set_time_dim(time_dim)
        self._time_controller = None
        self._time_fixed = time_fixed

    def _init_controller(self):
        tc = TimeController(self._current_time, self._time_fixed)
        tc.add_plot(self)

    def _set_time_dim(self, time_dim):
        if self._time_dim is not None:
            raise NotImplementedError("Time dim already set")
        self._time_dim = time_dim
        if isinstance(time_dim, UTS):
            self._current_time = time_dim.tmin
        elif isinstance(time_dim, Case):
            self._current_time = 0

    def link_time_axis(self, other):
        """Link the time axis of this figure with another figure"""
        if self._time_dim is None:
            raise NotImplementedError("Slice plot for dimension other than time")
        elif not isinstance(other, TimeSlicer):
            raise TypeError(f"{other.__class__.__name__} plot does not support linked time axes")
        elif other._time_dim is None:
            raise NotImplementedError("Slice plot for dimension other than time")
        elif other._time_controller:
            other._time_controller.add_plot(self)
        else:
            if not self._time_controller:
                self._init_controller()
            self._time_controller.add_plot(other)

    def _nudge_time(self, offset):
        if self._time_dim is None:
            return
        current_i = self._time_dim._array_index(self._current_time)
        if offset > 0:
            new_i = min(self._time_dim.nsamples - 1, current_i + offset)
        else:
            new_i = max(0, current_i + offset)
        self._set_time(self._time_dim[new_i], True)

    def get_time(self):
        "Retrieve the current time"
        return self._current_time

    def set_time(self, time):
        """Set the time point to display

        Parameters
        ----------
        time : scalar
            Time to display.
        """
        self._set_time(time, True)

    def _set_time(self, t, fixate=False):
        "Called by the plot"
        if self._time_controller is None:
            self._update_time_wrapper(t, fixate)
        else:
            self._time_controller.set_time(t, fixate)

    def _update_time_wrapper(self, t, fixate):
        "Called by the TimeController"
        if (t == self._current_time and fixate == self._time_fixed) or self._frame is None:
            return
        self._update_time(t, fixate)
        self._current_time = t
        self._time_fixed = fixate
        if self._display_time_in_frame_title:
            self._frame.SetTitleSuffix(f' [{ms(t)} ms]')

    def _update_time(self, t, fixate):
        raise NotImplementedError

    def _validate_time(self, t):
        if self._time_dim is not None:
            if t < self._time_dim.tmin:
                return self._time_dim.tmin
            elif t > self._time_dim.tmax:
                return self._time_dim.tmax
        return t


class TimeSlicerEF(TimeSlicer):
    # TimeSlicer for Eelfigure
    _can_set_time = True

    def __init__(self, x_dimname, x_dim, axes=None, redraw=True):
        if x_dimname != 'time':
            TimeSlicer.__init__(self, time_fixed=True)
            return
        TimeSlicer.__init__(self, x_dim)
        self.__axes = self._axes if axes is None else axes
        self.__time_lines = []
        self.__redraw = redraw
        self.canvas.mpl_connect('button_press_event', self._on_click)
        self._register_key('.', self._on_nudge_time)
        self._register_key(',', self._on_nudge_time)

    def _on_click(self, event):
        if self._time_controller and event.inaxes in self.__axes:
            self._set_time(event.xdata, fixate=event.button == 1)

    def _on_motion_sub(self, event):
        if not self._time_fixed and event.inaxes in self.__axes:
            self._set_time(event.xdata)
        return set()

    def _on_nudge_time(self, event):
        self._nudge_time(1 if event.key == '.' else -1)

    def _update_time(self, t, fixate):
        if fixate:
            redraw = True
            if self.__time_lines:
                xdata = (t, t)
                for line in self.__time_lines:
                    line.set_xdata(xdata)
            else:
                for ax in self.__axes:
                    self.__time_lines.append(ax.axvline(t, color='k'))
        else:
            redraw = bool(self.__time_lines)
            while self.__time_lines:
                self.__time_lines.pop().remove()

        if self.__redraw and redraw and self._frame is not None:
            self.canvas.redraw(self.__axes)

    def save_movie(self, filename=None, time_dilation=4., **kwargs):
        """Save the figure with moving time axis as movie

        Parameters
        ----------
        filename : str
            Filename for the movie (omit to use a GUI).
        time_dilation : float
            Factor by which to stretch time (default 4). Time dilation is
            controlled through the frame-rate; if the ``fps`` keyword argument
            is specified, ``time_dilation`` is ignored.
        ...
            :func:`imageio.mimwrite` parmeters.
        """
        import imageio

        if filename is None:
            filename = ui.ask_saveas("Save movie...", None, [('Movie (*.mov)', '*.mov')])
            if not filename:
                return
        else:
            filename = os.path.expanduser(filename)

        if 'fps' not in kwargs:
            kwargs['fps'] = 1. / self._time_dim.tstep / time_dilation

        ims = []
        for t in self._time_dim:
            self._set_time(t, True)
            # private attr usage is official: https://matplotlib.org/gallery/misc/agg_buffer_to_array.html
            im = np.array(self.figure.canvas.renderer._renderer)
            ims.append(im)
        imageio.mimwrite(filename, ims, **kwargs)


class TopoMapKey:

    def __init__(self, data_func):
        self.__topo_data = data_func
        self._register_key('t', self.__on_topo)
        self._register_key('T', self.__on_topo)

    def __on_topo(self, event):
        topo_data = self.__topo_data(event)
        if topo_data is None:
            return

        from ._topo import Topomap

        data, title, proj = topo_data
        if event.key == 't':
            Topomap(data, proj=proj, cmap=self._cmaps, vmax=self._vlims,
                    contours=self._contours, title=title)
        else:
            Topomap(data, proj=proj, cmap=self._cmaps, vmax=self._vlims,
                    contours=self._contours, title=title, axw=9,
                    sensorlabels='name')


class XAxisMixin:
    """Manage x-axis

    Parameters
    ----------
    xmin : scalar
        Lower bound of the x axis.
    xmin : scalar
        Upper bound of the x axis.
    axes : list of Axes
        Axes that should be managed by the mixin.
    xlim : scalar | (scalar, scalar)
        Initial x-axis view limits as ``(left, right)`` tuple or as ``length``
        scalar (default is the full x-axis in the data).

    Notes
    -----
    Navigation:
     - ``←``: scroll left
     - ``→``: scroll right
     - ``home``: scroll to beginning
     - ``end``: scroll to end
     - ``f``: x-axis zoom in (reduce x axis range)
     - ``d``: x-axis zoom out (increase x axis range)
    """
    _can_set_xlim = True

    def __init__(self, xmin, xmax, xlim=None, axes=None):
        self.__xmin = xmin
        self.__xmax = xmax
        self.__axes = axes or self._axes
        self.__vspans = []
        self._register_key('f', self.__on_zoom_plus)
        self._register_key('d', self.__on_zoom_minus)
        self._register_key('j' if IS_WINDOWS else 'left', self.__on_left)
        self._register_key('l' if IS_WINDOWS else 'right', self.__on_right)
        self._register_key('home', self.__on_beginning)
        self._register_key('end', self.__on_end)
        if xlim is None:
            xlim = (self.__xmin, self.__xmax)
        elif np.isscalar(xlim):
            xlim = (self.__xmin, self.__xmin + xlim)
        self._set_xlim(*xlim)

    def _init_with_data(self, epochs, xdim, xlim=None, axes=None, im=False):
        """Compute axis bounds from data

        Parameters
        ----------
        epochs : list of list of NDVar
            The data that is plotted (to determine axis range).
        xdim : str
            Dimension that is plotted on the x-axis.
        axes : list of Axes
            Axes that should be managed by the mixin.
        xlim : scalar | (scalar, scalar)
            Initial x-axis view limits as ``(left, right)`` tuple or as ``length``
            scalar (default is the full x-axis in the data).
        im : bool
            Plot displays an im, i.e. the axes limits need to extend beyond the
            dimension endpoints by half a step (default False).
        """
        dims = tuple(e.get_dim(xdim) for e in chain(*epochs))
        if im:
            dim_extent = tuple(dim._axis_im_extent() for dim in dims)
            xmin = min(e[0] for e in dim_extent)
            xmax = max(e[1] for e in dim_extent)
        else:
            xmin = min(dim[0] for dim in dims)
            xmax = max(dim[-1] for dim in dims)
        XAxisMixin.__init__(self, xmin, xmax, xlim, axes)

    def get_xlim(self):
        return self.__axes[0].get_xlim()

    def __animate(self, vmin, vmin_dst, vmax, vmax_dst):
        n_steps = int(0.1 // self._last_draw_time)
        if n_steps > 1:
            vmin_d = vmin_dst - vmin
            vmax_d = vmax_dst - vmax
            for i in range(1, n_steps):
                x = i / n_steps
                self.set_xlim(vmin + x * vmin_d, vmax + x * vmax_d)
        self.set_xlim(vmin_dst, vmax_dst)

    def __on_beginning(self, event):
        left, right = self.get_xlim()
        d = right - left
        self.set_xlim(self.__xmin, min(self.__xmax, self.__xmin + d))

    def __on_end(self, event):
        left, right = self.get_xlim()
        d = right - left
        self.set_xlim(max(self.__xmin, self.__xmax - d), self.__xmax)

    def __on_zoom_plus(self, event):
        left, right = self.get_xlim()
        d = (right - left) / 4.
        self.__animate(left, left + d, right, right - d)

    def __on_zoom_minus(self, event):
        left, right = self.get_xlim()
        d = right - left
        new_left = max(self.__xmin, left - (d / 2.))
        new_right = min(self.__xmax, new_left + 2 * d)
        self.__animate(left, new_left, right, new_right)

    def __on_left(self, event):
        left, right = self.get_xlim()
        d = right - left
        new_left = max(self.__xmin, left - d)
        self.__animate(left, new_left, right, new_left + d)

    def __on_right(self, event):
        left, right = self.get_xlim()
        d = right - left
        new_right = min(self.__xmax, right + d)
        self.__animate(left, new_right - d, right, new_right)

    def _set_xlim(self, left, right, draw=False):
        for ax in self.__axes:
            ax.set_xlim(left, right)
        if draw:
            self.draw()

    def add_vspans(self, intervals, axes=None, *args, **kwargs):
        """Draw vertical bars over axes

        Parameters
        ----------
        intervals : sequence of (start, stop) tuples
            Start and stop positions on the x-axis.
        axes : int | list of int
            Which axes to mark (default is all axes).
        additonal arguments :
            Additional arguments for :func:`matplotlib.axvspan`.
        """
        if axes is None:
            axes = self.__axes
        elif isinstance(axes, int):
            axes = (self.__axes[axes],)
        else:
            axes = [self.__axes[i] for i in axes]

        for ax in axes:
            for xmin, xmax in intervals:
                self.__vspans.append(ax.axvspan(xmin, xmax, *args, **kwargs))
        self.draw()

    def set_xlim(self, left=None, right=None):
        """Set the x-axis limits for all axes"""
        if isinstance(self, TimeSlicer) and self._time_controller is not None:
            if left is None or right is None:
                ax_left, ax_right = self.__axes[0].get_xlim()
                if left is None:
                    left = ax_left
                if right is None:
                    right = ax_right
            self._time_controller.set_xlim(left, right)
        else:
            self._set_xlim(left, right, draw=True)


class YLimMixin:
    """Manage y-axis

    Parameters
    ----------
    plots : Sequence
        Plots to manage. Plots must have ``.ax`` attribute.

    Notes
    -----
    Navigation:
     - ``↑``: scroll up
     - ``↓``: scroll down
     - ``r``: y-axis zoom in (reduce y-axis range)
     - ``c``: y-axis zoom out (increase y-axis range)
    """
    # Keep Y-lim and V-lim separate. For EEG, one might want to invert the
    # y-axis without inverting the colormap

    # What should be the organizing principle for different vlims within
    # one figure? Use cases:
    # - 2 axes with different data
    # - (not implemented) one axis with two y-axes
    _can_set_ylim = True

    def __init__(self, plots):
        self.__plots = plots
        self._register_key('r', self.__on_zoom_in)
        self._register_key('c', self.__on_zoom_out)
        self._register_key('i' if IS_WINDOWS else 'up', self.__on_move_up)
        self._register_key('k' if IS_WINDOWS else 'down', self.__on_move_down)
        self._draw_hooks.append(self.__draw_hook)
        # disable because it changes y-limits
        # self._untight_draw_hooks.append(self.__untight_draw_hook)

    def __draw_hook(self):
        need_draw = False
        for p in self.__plots:
            # decimate overlapping ticklabels
            locs = p.ax.yaxis.get_ticklocs()
            we = tuple(l.get_window_extent(self.canvas.renderer) for l in p.ax.yaxis.get_ticklabels())
            start = 0
            step = 1
            locs_list = list(locs) if 0 in locs else None
            while any(e1.ymin < e0.ymax for e0, e1 in intervals(we[start::step])):
                step += 1
                if locs_list:
                    start = locs_list.index(0) % step
            if step > 1:
                p.ax.yaxis.set_ticks(locs[start::step])
                need_draw = True
        return need_draw

    def __untight_draw_hook(self):
        for p in self.__plots:
            # remove the top-most y tick-label if it is outside the figure
            extent = p.ax.yaxis.get_ticklabels()[-1].get_window_extent()
            if extent.height and extent.y1 > self.figure.get_window_extent().y1:
                p.ax.set_yticks(p.ax.get_yticks()[:-1])

    def get_ylim(self):
        vmin = min(p.vmin for p in self.__plots)
        vmax = max(p.vmax for p in self.__plots)
        return vmin, vmax

    def set_ylim(self, bottom=None, top=None):
        """Set the y-axis limits

        Parameters
        ----------
        bottom : scalar
            Lower y-axis limit.
        top : scalar
            Upper y-axis limit.
        """
        if bottom is None and top is None:
            return

        for p in self.__plots:
            p.set_ylim(bottom, top)
        self.draw()

    def __animate(self, vmin, vmin_d, vmax, vmax_d):
        n_steps = int(0.1 // self._last_draw_time)
        if n_steps <= 1:
            self.set_ylim(vmin + vmin_d, vmax + vmax_d)
        else:
            for i in range(1, n_steps + 1):
                x = i / n_steps
                self.set_ylim(vmin + x * vmin_d, vmax + x * vmax_d)

    def __on_move_down(self, event):
        vmin, vmax = self.get_ylim()
        d = (vmax - vmin) * 0.1
        self.__animate(vmin, -d, vmax, -d)

    def __on_move_up(self, event):
        vmin, vmax = self.get_ylim()
        d = (vmax - vmin) * 0.1
        self.__animate(vmin, d, vmax, d)

    def __on_zoom_in(self, event):
        vmin, vmax = self.get_ylim()
        d = (vmax - vmin) * 0.05
        self.__animate(vmin, d, vmax, -d)

    def __on_zoom_out(self, event):
        vmin, vmax = self.get_ylim()
        d = (vmax - vmin) * (1 / 22)
        self.__animate(vmin, -d, vmax, d)


class ImageTiler:
    """
    Create tiled images and animations from individual image files.

    Parameters
    ----------
    ext : str
        Extension to append to generated file names.
    nrow : int
        Number of rows of tiles in a frame.
    ncol : int
        Number of columns of tiles in a frame.
    nt : int
        Number of time points in the animation.
    dest : str(directory)
        Directory in which to place files. If None, a temporary directory
        is created and removed upon deletion of the ImageTiler instance.
    """
    def __init__(self, ext='.png', nrow=1, ncol=1, nt=1, dest=None):
        if dest is None:
            self.dir = tempfile.mkdtemp()
        else:
            if not os.path.exists(dest):
                os.makedirs(dest)
            self.dir = dest

        # find number of digits necessary to name images
        row_fmt = '%%0%id' % (np.floor(np.log10(nrow)) + 1)
        col_fmt = '%%0%id' % (np.floor(np.log10(ncol)) + 1)
        t_fmt = '%%0%id' % (np.floor(np.log10(nt)) + 1)
        self._tile_fmt = 'tile_%s_%s_%s%s' % (row_fmt, col_fmt, t_fmt, ext)
        self._frame_fmt = 'frame_%s%s' % (t_fmt, ext)

        self.dest = dest
        self.ncol = ncol
        self.nrow = nrow
        self.nt = nt

    def __del__(self):
        if self.dest is None:
            shutil.rmtree(self.dir)

    def get_tile_fname(self, col=0, row=0, t=0):
        if col >= self.ncol:
            raise ValueError("col: %i >= ncol" % col)
        if row >= self.nrow:
            raise ValueError("row: %i >= nrow" % row)
        if t >= self.nt:
            raise ValueError("t: %i >= nt" % t)

        if self.ncol == 1 and self.nrow == 1:
            return self.get_frame_fname(t)

        fname = self._tile_fmt % (col, row, t)
        return os.path.join(self.dir, fname)

    def get_frame_fname(self, t=0, dirname=None):
        if t >= self.nt:
            raise ValueError("t: %i >= nt" % t)

        if dirname is None:
            dirname = self.dir

        fname = self._frame_fmt % (t,)
        return os.path.join(dirname, fname)

    def make_frame(self, t=0, redo=False):
        """Produce a single frame."""
        dest = self.get_frame_fname(t)

        if os.path.exists(dest):
            if redo:
                os.remove(dest)
            else:
                return

        # collect tiles
        images = []
        colw = [0] * self.ncol
        rowh = [0] * self.nrow
        for r in range(self.nrow):
            row = []
            for c in range(self.ncol):
                fname = self.get_tile_fname(c, r, t)
                if os.path.exists(fname):
                    im = PIL.Image.open(fname)
                    colw[c] = max(colw[c], im.size[0])
                    rowh[r] = max(rowh[r], im.size[1])
                else:
                    im = None
                row.append(im)
            images.append(row)

        cpos = np.cumsum([0] + colw)
        rpos = np.cumsum([0] + rowh)
        out = PIL.Image.new('RGB', (cpos[-1], rpos[-1]))
        for r, row in enumerate(images):
            for c, im in enumerate(row):
                if im is None:
                    pass
                else:
                    out.paste(im, (cpos[c], rpos[r]))
        out.save(dest)

    def make_frames(self):
        for t in range(self.nt):
            self.make_frame(t=t)

    def make_movie(self, dest, framerate=10, codec='mpeg4'):
        """Make all frames and export a movie"""
        dest = os.path.expanduser(dest)
        dest = os.path.abspath(dest)
        root, ext = os.path.splitext(dest)
        dirname = os.path.dirname(dest)
        if ext not in ['.mov', '.avi']:
            if len(ext) == 4:
                dest = root + '.mov'
            else:
                dest = dest + '.mov'

        if not command_exists('ffmpeg'):
            err = ("Need ffmpeg for saving movies. Download from "
                   "http://ffmpeg.org/download.html")
            raise RuntimeError(err)
        elif os.path.exists(dest):
            os.remove(dest)
        elif not os.path.exists(dirname):
            os.mkdir(dirname)

        self.make_frames()

        # make the movie
        frame_name = self._frame_fmt
        cmd = ['ffmpeg',  # ?!? order of options matters
               '-f', 'image2',  # force format
               '-r', str(framerate),  # framerate
               '-i', frame_name,
               '-c', codec,
               '-sameq', dest,
               '-pass', '2'  #
               ]
        sp = subprocess.Popen(cmd, cwd=self.dir, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        stdout, stderr = sp.communicate()
        if not os.path.exists(dest):
            raise RuntimeError("ffmpeg failed:\n" + stderr)

    def save_frame(self, dest, t=0, overwrite=False):
        if not overwrite and os.path.exists(dest):
            raise IOError("File already exists: %r" % dest)
        self.make_frame(t=t)
        fname = self.get_frame_fname(t)
        im = PIL.Image.open(fname)
        im.save(dest)
