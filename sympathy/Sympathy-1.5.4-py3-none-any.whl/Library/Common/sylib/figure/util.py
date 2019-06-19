# Copyright (c) 2016, Combine Control Systems AB
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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import copy
import numbers
import itertools
from collections import defaultdict, OrderedDict, Iterable
from datetime import datetime

import numpy as np
import six
import matplotlib
import matplotlib.cm as cm
from matplotlib import collections as mpl_collections
from matplotlib import container as mpl_container
from matplotlib import dates as mpl_dates
from matplotlib import gridspec
from matplotlib import image as mpl_image
from matplotlib import lines as mpl_lines
from matplotlib import patches as mpl_patches
from matplotlib.text import Text
from matplotlib.ticker import FixedLocator
from matplotlib.transforms import IdentityTransform

from sylib.figure import colors, models, mpl_utils, common
from sympathy.platform.exceptions import sywarn
from sympathy.platform.exceptions import SyConfigurationError
from sympathy.platform.exceptions import SyDataError
from sympathy.typeutils import figure
from sympathy.typeutils.figure import SyAxes


def make_iterable(X, N):
    """If object X is not an array or list, then create a list containing
    N copies of X. If object X is not an array or list, then create a
    list containing N copies of X"""

    if X is None:
        return [None]*N
    if not (isinstance(X, np.ndarray) or isinstance(X, list)):
        return [X]*N
    else:
        return X


def make_iterable_or_none(X, N):
    """If X is None then return None, otherwise if object X is not an
    array or list, then create a list containing N copies of X. If X
    is already iterable then keep it."""

    if X is None:
        return None
    if not (isinstance(X, np.ndarray) or isinstance(X, list)):
        return [X]*N
    else:
        return X


def gen_config_by_prefix(config, prefix):
    """
    Return a generator returning (key, value) where the key
    starts with the given prefix + '.'.
    """
    prefix += '.'
    return ((k.lower(), v) for k, v in config
            if k.lower().startswith(prefix.lower()))


def fill_in_global_parameters(global_params, local_params):
    """
    Update the local parameters with existing global parameters
    without overriding existing ones.
    """
    for key, value in six.iteritems(global_params):
        for local in local_params.values():
            if key not in local:
                local[key] = value


def add_layer_to_axes(config, layer_cls, axes, default_axes_id,
                      container_dict):
    """
    Parse the parameters of a plot type (line/scatter/bar etc.).

    The parsed configurations get added to the appropriate axes.

    Parameters
    ----------
    config : list of tuples
        A list of (parameter, value) pairs, where each parameter is defined as
        <layer_type>.<type_id>.<type_parameter>.
    layer_cls : class
        The model class of the given layer type, either
        `models.BasePlot` or `models.BasePlotContainer`.
    axes : dict
        A dictionary with all parsed axes.
    default_axes_id : str
        The axes_id in `axes` of the default 'x1,y1' axis.
    container_dict : OrderedDict
    """
    # global_layer_params = {}
    layers = OrderedDict()

    item_leafs = layer_cls.NODE_LEAFS

    for key, value in config:
        key_splitted = key.lower().split('.')
        sub_param = []
        num_keys = len(key_splitted)

        if num_keys == 3 and key_splitted[1] not in item_leafs.keys():
            identifier, param = key_splitted[1:]
        elif num_keys == 3 and key_splitted[1] in item_leafs.keys():
            identifier = None
            param = key_splitted[1]
            sub_param = key_splitted[2:]
        elif num_keys == 2:
            identifier, param = None, key_splitted[1]
        else:
            identifier = key_splitted[1]
            param = key_splitted[2]
            sub_param = key_splitted[3:]

        if identifier is not None:
            if identifier not in layers:
                layers[identifier] = copy.deepcopy(layer_cls.default_data)
                layers[identifier]['type'] = layer_cls.node_type
            working_d = layers[identifier]
        else:
            continue
            # currently disabled, since not used
            # working_d = global_layer_params

        if models.NodeTags.is_container in layer_cls.cls_tags:
            container_dict[identifier] = working_d
        child_nodes = {c.node_type: c for c in layer_cls.valid_children() if
                       not c.is_leaf}
        if param in child_nodes:
            param_cls = child_nodes[param]
            sub_props = param_cls.NODE_LEAFS

            if param not in working_d:
                if param_cls.default_data is not None:
                    working_d[param] = copy.deepcopy(param_cls.default_data)
                else:
                    working_d[param] = OrderedDict()
            if len(sub_param) == 1 and sub_param[0] in sub_props:
                prop = sub_param[0]
                if prop is not None and value is not None:
                    working_d[param][prop] = value
        else:
            if param == 'axes' and identifier is not None:
                if value == '_default_':
                    value = default_axes_id
                working_d['axes'] = value
            elif param == 'container' and identifier is not None:
                working_d['container'] = value
            elif param not in item_leafs:
                continue
            else:
                working_d[param] = value

    # add the layers to the appropriate axes
    for id_, layer in six.iteritems(layers):
        container_id = layer.pop('container', None)
        # if axes_id does not exist, take default one
        if container_id is None or container_id not in container_dict:
            axes_id = layer.pop('axes', default_axes_id)
            if axes_id not in axes:
                axes_id = default_axes_id
            axes[axes_id]['plots'].append(layer)
        else:
            # remove link to axes from plot, its already given by the container
            axes_id = layer.pop('axes', None)
            container_dict[container_id]['plots'].append(layer)
    return axes


def parse_config_axes(config):
    """Parse the axes parameters."""
    # global_axes = {}
    axes = OrderedDict()

    item_properties = models.Axes.STORED_LEAFS

    for key, value in config:
        key_splitted = key.lower().split('.')
        sub_param = []
        num_keys = len(key_splitted)

        if num_keys == 3 and key_splitted[1] not in item_properties.keys():
            identifier, param = key_splitted[1:]
        elif num_keys == 3 and key_splitted[1] in item_properties.keys():
            identifier = None
            param = key_splitted[1]
            sub_param = key_splitted[2:]
        elif num_keys == 2:
            identifier, param = None, key_splitted[1]
        else:
            identifier = key_splitted[1]
            param = key_splitted[2]
            sub_param = key_splitted[3:]

        # special case handling to convert old style axis positions
        if param == 'xaxis':
            param = 'xaxis_position'
            if value in common.REPLACE_AXIS_TYPE:
                value = common.REPLACE_AXIS_TYPE[value]
        if param == 'yaxis':
            param = 'yaxis_position'
            if value in common.REPLACE_AXIS_TYPE:
                value = common.REPLACE_AXIS_TYPE[value]

        # set default data for identifier and
        # assign dict to add parameters to as 'working_d'
        if identifier is not None:
            if identifier not in axes:
                axes[identifier] = copy.deepcopy(models.Axes.default_data)
            working_d = axes[identifier]
        else:
            continue
            # currently not used
            # working_d = global_axes

        mapping = item_properties.get(param, None)
        if mapping is None:
            continue

        child_nodes = {c.node_type: c for c in models.Axes.valid_children() if
                       not issubclass(c, models.FigureProperty)}
        if param in child_nodes:
            sub_cls = child_nodes[param]
            sub_props = sub_cls.NODE_LEAFS

            if param not in working_d:
                if sub_cls.default_data is not None:
                    working_d[param] = copy.deepcopy(sub_cls.default_data)
                else:
                    working_d[param] = OrderedDict()
            if len(sub_param) == 1 and sub_param[0] in sub_props:
                prop = sub_param[0]
                if prop is not None and value is not None:
                    working_d[param][prop] = value
        else:
            # parsed_value = common.parse_type(value, t, o)
            # a[param] = value  # parsed_value

            subdirs = mapping.split('.')
            for subdir in subdirs[:-1]:
                if subdir not in working_d:
                    working_d[subdir] = OrderedDict()
                working_d = working_d[subdir]
            working_d[subdirs[-1]] = value  # parsed_value

    # get all defined x and y axes
    # defined_yaxis = set(
    #     [a['yaxis'] for a in axes.values() if 'yaxis' in a])

    # get required parameters
    # required_parameters = [k for k, v in six.iteritems(AXES) if
    #                        not isinstance(v, dict) and v[3]]

    # TODO(Bene): update line parameters from global parameters if missing and
    # defined in global line parameter
    # for axis_id, params in six.iteritems(axes):
    #     for required_param in required_parameters:
    #         if required_param in params.keys():
    #             continue
    #         if required_param in global_axes.keys():
    #             value = global_axes[required_param]
    #         else:
    #             value = AXES[required_param][1]
    #             if required_param == 'yaxis':
    #                 if value in defined_yaxis:
    #                     value = 'right'
    #         axes[axis_id][required_param] = value
    # fill_in_global_parameters(global_axes, axes)
    return axes


def parse_config_figure(config):
    """Parse the figure parameters."""
    figure = OrderedDict()

    item_leafs = models.Figure.NODE_LEAFS

    for key, value in config:
        key_splitted = key.lower().split('.')
        num_keys = len(key_splitted)

        if num_keys == 2 and key_splitted[1] in item_leafs:
            param = key_splitted[1]
            type_ = item_leafs[param]['eval']
            options = item_leafs[param]['options']
            parsed_value = common.parse_type(value, type_, options)
            figure[param] = parsed_value
        elif num_keys == 3 and key_splitted[1] in [models.Legend.node_type]:
            param = key_splitted[1]
            sub_param = key_splitted[2]
            if param not in figure:
                figure[param] = OrderedDict()
            figure[param][sub_param] = value
    # TODO: reordering of items
    return figure


def get_default_axes_id(axes):
    """Get the default axes_id."""
    for axes_id, ax in six.iteritems(axes):
        if (ax['xaxis']['position'] == 'bottom' and
                ax['yaxis']['position'] == 'left'):
            return axes_id
    return None


def parse_configuration(config):
    """
    Parse a configuration table with a parameter and value column.
    """
    figure = parse_config_figure(gen_config_by_prefix(config, 'figure'))
    axes = parse_config_axes(gen_config_by_prefix(config, 'axes'))

    # get a default axes_id to use
    # if layer parameters define axes as "_default_"
    default_axes_id = get_default_axes_id(axes)

    # handle containers first, so plots can be added appropriately
    valid_layer_types = OrderedDict(
        [(i.node_type, i) for i in [
            models.BarContainer,
            models.HistogramContainer,
            models.Iterator,
            models.LinePlot,
            models.ScatterPlot,
            models.BarPlot,
            models.HistogramPlot,
            models.HeatmapPlot,
            models.BoxPlot,
            models.PieChart,
            models.Annotation,
            models.TimelinePlot,
            models.ImagePlot,
            models.Lines,
            models.Rectangles,
            models.Ellipses,
        ]])

    container_dict = OrderedDict()
    for layer_type, layer_cls in six.iteritems(valid_layer_types):
        layer_cfg = gen_config_by_prefix(config, layer_type)
        axes = add_layer_to_axes(
            layer_cfg, layer_cls, axes, default_axes_id, container_dict)

    figure['axes'] = list(axes.values())  # remove the axes ids
    return OrderedDict([('figure', figure)])


def export_config(model):
    """
    Export the models node and properties to list of (parameter, value) pairs.

    Parameters
    ----------
    model : models.DataModel

    Returns
    -------
    list
        A list of (parameter, value) tuples.
    """
    return model.root.export_config()


def reconstruct_twin_axes(start_axes, axes):
    """Reconstruct the relationship between overlaying twin axes."""
    sibling_axes = {start_axes: (1, 1)}
    shared_ax = {ax: (ax._sharex, ax._sharey) for ax in axes}

    for ax in axes:
        if ax in sibling_axes.keys():
            continue
        has_shared = shared_ax.get(ax)
        if has_shared is not None and has_shared != (None, None):
            sharex, sharey = has_shared
            if sharex is not None and sharey is None:
                x_parent_pos = sibling_axes.get(sharex)
                pos = x_parent_pos[0], x_parent_pos[1] + 1
            elif sharex is None and sharey is not None:
                y_parent_pos = sibling_axes.get(sharey)
                pos = y_parent_pos[0] + 1, y_parent_pos[1]
            else:
                raise ValueError('Unknown axes configuration')
            sibling_axes[ax] = pos
    return sibling_axes


def get_twin_axes(axes_dict, xaxis, yaxis):
    """
    Return the twin axes given by `xaxis`, `yaxis`.

    Parameters
    ----------
    axes_dict : dict
        A dictionary containing at least the default axes
        with xaxis='bottom' and yaxis='left'.
    xaxis : unicode
        The name of the xaxis. Supported values are 'bottom' and 'top'.
    yaxis : unicode
        The name of the yaxis. Supported values are 'left' and 'right'.

    Returns
    -------
    ax : matplotlib.axes._subplots.AxesSubplot
    """
    ax = axes_dict.get((xaxis, yaxis), None)
    default_axes = axes_dict[('bottom', 'left')]
    if isinstance(default_axes, figure.SyAxes):
        default_axes = default_axes.get_mpl_axes()
    if ax is None:
        if xaxis == 'bottom' and yaxis == 'right':
            ax = default_axes.twinx()
        elif xaxis == 'top' and yaxis == 'left':
            ax = default_axes.twiny()
        elif xaxis == 'top' and yaxis == 'right':
            x1y2axes = get_twin_axes(axes_dict, 'bottom', 'right')
            ax = x1y2axes.twiny()
        else:
            raise ValueError('The axes type "{}, {}" is not '
                             'supported.'.format(xaxis, yaxis))
        axes_dict[(xaxis, yaxis)] = ax
    return ax


def classify_axes(axes):
    """
    Classify the axes in the scheme ('bottom', 'left').

    The axes get stored with a (x,y) key in a dictionary
    depending on their shared x or y axes. The first axes
    will always be set as ('bottom', 'left').
    """
    if len(axes):
        classed_axes = reconstruct_twin_axes(axes[0], axes)
        xaxis_options = ['bottom', 'top']
        yaxis_options = ['left', 'right']
        return {(xaxis_options[v[0]-1], yaxis_options[v[1]-1]): k
                for k, v in six.iteritems(classed_axes)}
    return {}


def get_sorted_axes(axes_dict):
    """Sort axes dictionary."""
    order = [('bottom', 'left'),
             ('bottom', 'right'),
             ('top', 'left'),
             ('top', 'right')]
    return OrderedDict([(ax_id, axes_dict.get(ax_id))
                        for ax_id in order
                        if axes_dict.get(ax_id) is not None])


def _get_mpl_axes(source, target):
    if isinstance(target, figure.SyAxes):
        target = target.get_mpl_axes()
    if isinstance(source, figure.SyAxes):
        source = source.get_mpl_axes()
    return source, target


def _get_colorbar_axes(axes):
    """
    Helper function which returns all axes of colorbars linked to artists.

    Parameters
    ----------
    axes : list
        A list of matplotlib Axes.

    Returns
    -------
    cb_axes : set
    """
    cb_axes = []
    for ax in axes:
        for artist_type in ['images', 'collections']:
            for artist in getattr(ax, artist_type):
                if artist.colorbar is not None:
                    cb_axes.append(artist.colorbar.ax)
    return cb_axes


def _copy_axis_visibility(source, target):
    """
    Copies visibility and color properties from each X/Y axis in the source
    axes object to the target axes object.
    """
    if not source.get_xaxis().get_visible():
        target.get_xaxis().set_visible(False)
    if not source.get_yaxis().get_visible():
        target.get_yaxis().set_visible(False)
    target.set_facecolor(source.get_facecolor())


def _move_artists(source, target, existing_colors, auto_recolor=True):
    """
    Move all supported artists from a source to a target axes.
    """
    colorbars = {}
    handles_labels = []

    handles_labels.extend(_move_lines_to(source, target, existing_colors,
                                         auto_recolor=auto_recolor))
    handles_labels.extend(_copy_patches_to(source, target))
    handles_labels.extend(_copy_wedges_to(source, target))
    _copy_spines_to(source, target)
    cbs, collection_handles_labels = _move_collections_to(
        source, target, existing_colors, auto_recolor=auto_recolor)
    if cbs:
        colorbars['collections'] = cbs
    handles_labels.extend(collection_handles_labels)
    handles_labels.extend(_move_containers_to(source, target))
    _move_text_to(source, target)
    cbs, image_handles_labels = _move_images_to(source, target)
    if cbs:
        colorbars['images'] = cbs
    handles_labels.extend(image_handles_labels)

    total_handles = []
    total_labels = []
    for handle, label in handles_labels:
        if not label or label.startswith('_'):
            continue
        total_labels.append(label)
        total_handles.append(handle)
    return colorbars, total_handles, total_labels


def _move_lines_to(source, target, existing_colors, auto_recolor=True):
    """
    Move a line artist from a source to a target axes.

    Remove the line artist from the source mpl.axes and
    add it to the target axes.
    """
    source, target = _get_mpl_axes(source, target)
    handles_labels = []
    for i, line in enumerate(source.lines):
        # create new Line2D object
        x, y = line.get_data()
        new_line = mpl_lines.Line2D(x, y)
        new_line.update_from(line)
        # extend the label if same already exists
        label = line.get_label()
        used_labels = [l.get_label() for l in target.lines]
        if label in used_labels:
            i = 2
            while '{}_{}'.format(label, i) in used_labels:
                i += 1
            new_line.set_label('{}_{}'.format(label, i))
        # this is a bit of a hack to remove axes specific properties
        new_line.set_transform(IdentityTransform())
        new_line._transformed_path = None
        new_line._transformSet = False
        new_line._xy = None
        new_line._x = None
        new_line._y = None
        handles_labels.append((new_line, new_line.get_label()))

        # auto assign new color from mpl color_cycle
        if auto_recolor:
            count_cols, unique_cols, unused_cols = _get_unique_n_unused_colors(
                existing_colors)
            current_color = colors.color2hex(new_line.get_color())
            if current_color in unique_cols:
                # assign a new color
                if len(unused_cols):
                    new_color = unused_cols[0]
                else:
                    least_occuring_color = unique_cols[
                        np.argsort(count_cols)[0]]
                    if len(least_occuring_color):
                        new_color = least_occuring_color
                    else:
                        new_color = mpl_utils.color_cycle[0]()
            else:
                new_color = current_color
            new_line.set_color(new_color)
        target.add_line(new_line)
        existing_colors.append(new_line.get_color())
    return handles_labels


def _move_images_to(source, target):
    """
    Move image artists from a source to a target axes.

    Parameters
    ----------
    source : SyAxes or matplotlib.axes.Axes
        The source axes from which artists are copied.
    target : SyAxes or matplotlib.axes.Axes
        The target axes into which artists are pasted.

    Returns
    -------
    cbs : list
        A list of tuples (artist, colorbar properties dict).
    """
    source, target = _get_mpl_axes(source, target)
    cbs = []
    handles_labels = []
    for i, image in enumerate(source.images):
        target.set_aspect(source.get_aspect())

        im = mpl_image.AxesImage(target,
                                 image.get_cmap(),
                                 image.norm,
                                 image.get_interpolation(),
                                 image.origin,
                                 image.get_extent(),
                                 filternorm=image.get_filternorm(),
                                 filterrad=image.get_filterrad(),
                                 resample=image.get_resample())
        im.set_data(image.get_array())
        im.set_alpha(image.get_alpha())
        handles_labels.append((im, im.get_label()))

        if im.get_clip_path() is None:
            im.set_clip_path(target.patch)
        vmin, vmax = image.get_clim()
        if vmin is not None or vmax is not None:
            im.set_clim(vmin, vmax)
        else:
            im.autoscale_None()
        im.set_url(image.get_url())

        extent = im.get_extent()
        im.set_extent(extent)
        target.add_image(im)
        colorbar_params = _get_colorbar_properties(image)
        cbs.append((im, colorbar_params))
    return cbs, handles_labels


def _move_collections_to(source, target, existing_colors, auto_recolor=True):
    """
    Move collection artists from a source to a target axes.

    Currently PathCollections and PolyCollections are supported.

    Parameters
    ----------
    source : SyAxes or matplotlib.axes.Axes
        The source axes from which artists are copied.
    target : SyAxes or matplotlib.axes.Axes
        The target axes into which artists are pasted.
    existing_colors : list
        A list of colors used by artists of the target axes. New used colors
        get appended to the list to be available to other '_move__to' helper
        functions.
    auto_recolor : bool, optional
        Set True if artists should be automatically recolored.

    Returns
    -------
    cbs : list
        A list of tuples (artist, colorbar properties dict).
    """
    source, target = _get_mpl_axes(source, target)
    cbs = []
    handles_labels = []
    for i, collection in enumerate(source.collections):
        if isinstance(collection, mpl_collections.PathCollection):
            new_collection, kwargs = _move_path_collection(collection, target)
        elif isinstance(collection, mpl_collections.PolyCollection):
            new_collection, kwargs = _move_poly_collection(collection, target)
        else:
            # Unsupported collection type. Skipping!
            continue
        handles_labels.append((new_collection, new_collection.get_label()))

        # auto assign new color from mpl color_cycle
        if auto_recolor:
            _set_unique_collection_color(new_collection, existing_colors)
        target.add_collection(new_collection, **kwargs)
        colorbar_params = _get_colorbar_properties(collection)
        cbs.append((new_collection, colorbar_params))
        target.autoscale_view()
    return cbs, handles_labels


def _move_poly_collection(collection, target):
    """Move a single PolyCollection to target axes."""

    verts = [p.vertices for p in collection.get_paths()]
    # TODO: remove if else when matplotlib version > 1.4.0
    if hasattr(collection, 'get_sizes'):
        sizes = collection.get_sizes()
    else:
        sizes = collection._sizes

    new_collection = mpl_collections.PolyCollection(verts, sizes)
    new_collection.update_from(collection)
    new_collection._transformSet = False

    label = collection.get_label()
    used_labels = [l.get_label() for l in target.collections]
    if label in used_labels:
        i = 2
        while '{}_{}'.format(label, i) in used_labels:
            i += 1
        new_collection.set_label('{}_{}'.format(label, i))

    # now update the datalim and autoscale
    for path in collection.get_paths():
        target.dataLim.update_from_path(
            path, ignore=target.ignore_existing_data_limits,
            updatex=True, updatey=True)

    return new_collection, {'autolim': False}


def _move_path_collection(collection, target):
    """Move a single PathCollection to target axes."""
    x, y = collection.get_offsets().T
    # create a new Collection object
    new_collection = mpl_collections.PathCollection(
        collection.get_paths(),
        collection.get_sizes(),
        offsets=collection.get_offsets(),
        transOffset=target.transData,
        alpha=collection.get_alpha())
    # extend the label if same already exists
    label = collection.get_label()
    used_labels = [l.get_label() for l in target.collections]
    if label in used_labels:
        i = 2
        while '{}_{}'.format(label, i) in used_labels:
            i += 1
        new_collection.set_label('{}_{}'.format(label, i))
    new_collection.update_from(collection)
    new_collection.set_cmap(collection.get_cmap())
    if target._xmargin < 0.05 and x.size > 0:
        target.set_xmargin(0.05)
    if target._ymargin < 0.05 and y.size > 0:
        target.set_ymargin(0.05)
    return new_collection, {}


def _set_unique_collection_color(collection, existing_colors):
    count_cols, unique_cols, unused_cols = _get_unique_n_unused_colors(
        existing_colors)
    current_color = colors.color2hex(collection.get_facecolor()[0])
    if current_color in unique_cols:
        # assign a new color
        if len(unused_cols):
            new_color = unused_cols[0]
        else:
            least_occuring_color = unique_cols[
                np.argsort(count_cols)[0]]
            if len(least_occuring_color):
                new_color = least_occuring_color
            else:
                new_color = mpl_utils.color_cycle[0]()
    else:
        new_color = current_color
    if isinstance(collection, mpl_collections.PolyCollection):
        collection.set_facecolor(new_color)
    else:
        collection.set_color(new_color)
    existing_colors.append(new_color)


def _move_containers_to(source, target):
    """
    Move a bar containers artist from a source to a target axes.
    """
    source, target = _get_mpl_axes(source, target)
    handles_labels = []
    for container in source.containers:
        # currently only BarContainers are supported
        if not isinstance(container, mpl_container.BarContainer):
            continue

        patches = []
        for patch in container.patches:
            r = mpl_patches.Rectangle(
                xy=patch.get_xy(),
                width=patch.get_width(),
                height=patch.get_height(),
                facecolor=patch.get_facecolor(),
                edgecolor=patch.get_edgecolor(),
                linewidth=patch.get_linewidth(),
                linestyle=patch.get_linestyle(),
                fill=patch.get_fill(),
                hatch=patch.get_hatch(),
                alpha=patch.get_alpha())
            target.add_patch(r)
            patches.append(r)

        label = container.get_label()
        used_labels = [l.get_label() for l in target.containers]
        if label in used_labels:
            i = 2
            while '{}_{}'.format(label, i) in used_labels:
                i += 1
            new_label = '{}_{}'.format(label, i)
        else:
            new_label = label

        bar_container = mpl_container.BarContainer(patches, None,
                                                   label=new_label)
        target.add_container(bar_container)
        handles_labels.append((bar_container, bar_container.get_label()))

    # Label the bins on the x axis.
    if isinstance(source.xaxis.get_major_locator(), FixedLocator):
        labels = source.get_xticklabels()
        target.set_xticks(range(len(labels)))
        target.set_xticklabels([l.get_text() for l in labels])
    return handles_labels


def _move_text_to(source, target):
    """
    Move text artist from a source to a target axes.
    """
    source, target = _get_mpl_axes(source, target)
    for text in source.texts:
        # get the text properties

        args = {}
        fancy_bbox = text.get_bbox_patch()
        if fancy_bbox:
            fbargs = {}
            fbargs['facecolor'] = fancy_bbox.get_facecolor()
            fbargs['edgecolor'] = fancy_bbox.get_edgecolor()
            fbargs['boxstyle'] = fancy_bbox.get_boxstyle()
            args['bbox'] = fbargs
        args['rotation'] = text.get_rotation()

        if isinstance(text, matplotlib.text.Annotation):
            new_text = matplotlib.text.Annotation(
                text.get_text(), text.xy, xytext=text.xyann,
                arrowprops=text.arrowprops, **args)
            target.add_artist(new_text)
            pass
        else:
            x, y = text.get_unitless_position()
            t = text.get_text()
            c = text.get_color()
            va = text.get_verticalalignment()
            ha = text.get_horizontalalignment()
            rot = text.get_rotation()
            rot_mode = text.get_rotation_mode()
            new_text = target.text(x, y, t, color=c, va=va, ha=ha, **args)

            # copy font properties
            new_text.set_fontproperties(text.get_font_properties())
            # apply rotation
            new_text.set_rotation_mode(rot_mode)
            new_text.set_rotation(rot)


def _copy_patches_to(source, target):
    """
    Copy patch artist from a soruce to a target axes.
    """
    source, target = _get_mpl_axes(source, target)
    handles_labels = []

    for child in source.get_children():
        if isinstance(child, matplotlib.patches.PathPatch):
            kwargs = {}
            kwargs['facecolor'] = child.get_facecolor()
            kwargs['edgecolor'] = child.get_edgecolor()
            target.add_patch(
                matplotlib.patches.PathPatch(child.get_path(), **kwargs))
            handles_labels.append((child, child.get_label()))
    return handles_labels


def _copy_wedges_to(source, target):
    """
    Copy wedges from a soruce to a target axes.
    """
    source, target = _get_mpl_axes(source, target)
    handles_labels = []

    for child in source.get_children():
        if isinstance(child, matplotlib.patches.Wedge):
            kwargs = {}
            kwargs['facecolor'] = child.get_facecolor()
            kwargs['edgecolor'] = child.get_edgecolor()
            target.add_patch(matplotlib.patches.Wedge(
                child.center, child.r, child.theta1, child.theta2,
                **kwargs))
            handles_labels.append((child, child.get_label()))
    return handles_labels


def _copy_spines_to(source, target):
    """
    Positions the left/bottom spines in the target axes the same as in
    the source object. Also hides the top/right spines if they are
    hidden in the source axes.
    """
    source, target = _get_mpl_axes(source, target)

    left_pos = source.spines['left'].get_position()
    bottom_pos = source.spines['bottom'].get_position()
    if isinstance(left_pos, tuple) and left_pos[0] == 'outward':
        # Default spines (not manually set) always have "outward" as their pos
        pass
    else:
        target.spines['left'].set_position(
            source.spines['left'].get_position())
        target.spines['right'].set_color('none')
    if isinstance(bottom_pos, tuple) and bottom_pos[0] == 'outward':
        pass
    else:
        target.spines['bottom'].set_position(
            source.spines['bottom'].get_position())
        target.spines['top'].set_color('none')


def _get_unique_n_unused_colors(existing_colors):
    unique_colors = np.unique(existing_colors)
    # workaround for numpy version < 1.9
    # we could use return_count in np.unique in the future
    color_count = [(np.array(existing_colors) == item).sum()
                   for item in unique_colors]
    unique_colors = list(unique_colors)  # otherwise FutureWarning
    hex_color_cycle = [colors.color2hex(c) for c in mpl_utils.color_cycle()]
    unused_colors = [c for c in hex_color_cycle if
                     c not in unique_colors]
    return color_count, unique_colors, unused_colors


parameter_list_to_copy = [
    # 'title',  # doesn't work for whichever reason
    'xscale',
    'yscale',
    'xlabel',
    'ylabel',
    'xlim',
    'ylim',
    'aspect',
]


def copy_axes_parameter(source, target):
    """
    Copy axes parameters from a source to a target axes.

    Copy the parameters defined in the ``parameter_list_to_copy``
    from the ``source`` mpl axes to the ``target`` mpl axes.
    """
    source, target = _get_mpl_axes(source, target)
    for attr in parameter_list_to_copy:
        # special case handling for FixedLocator on xaxis
        # required to keep Fixed Bar Plot lables
        if (attr == 'xscale' and
                isinstance(source.xaxis.get_major_locator(), FixedLocator)):
            continue
        value = getattr(source, 'get_{}'.format(attr))()
        setter = getattr(target, 'set_{}'.format(attr))
        setter(value)

    # Copy x-axis tick labels including rotations
    if isinstance(source.xaxis.get_major_locator(), FixedLocator):
        x_ticklabels = source.xaxis.get_ticklabels()
        try:
            tick_label_kwargs = {
                'ha': x_ticklabels[0].get_ha(),
                'rotation': x_ticklabels[0].get_rotation()}
        except IndexError:
            tick_label_kwargs = {}
        target.set_xticklabels(
            [text.get_text() for text in x_ticklabels],
            **tick_label_kwargs)

    for saxis, taxis in zip([source.xaxis, source.yaxis],
                            [target.xaxis, target.yaxis]):
        grid_params = {}
        major_grid_on = saxis._major_tick_kw.get('gridOn', False)
        minor_grid_on = saxis._minor_tick_kw.get('gridOn', False)

        if major_grid_on and minor_grid_on:
            grid_params['which'] = 'both'
        elif major_grid_on:
            grid_params['which'] = 'major'
        elif minor_grid_on:
            grid_params['which'] = 'minor'

        grid_lines = saxis.get_gridlines()
        if grid_lines:
            line_properties = grid_lines[0].properties()
            for prop in ['color', 'linewidth', 'linestyle']:
                value = line_properties.get(prop, None)
                grid_params[prop] = value

        grid_params['zorder'] = 1
        if saxis._gridOnMajor or saxis._gridOnMinor:
            taxis.grid(**grid_params)


def compress_axes(axes_of_figures, default_output_axes,
                  legends_join=False, legend_location='best',
                  copy_properties_from=0, auto_recolor=True,
                  auto_rescale=True, add_colorbars=True, add_legends=True,
                  remove_ticklabels=None):
    """
    Compress the lines and parameters from different axes into one.

    Parameters
    ----------
    axes_of_figures : array-like
        List of mpl axes
    default_output_axes : axes
        Mpl axes
    legends_join : bool, optional
        Set True if legends for different twin axes should be joined
        into one. Default False.
    legend_location : unicode or str or int, optional
        Location of the joined legend in mpl strings or int.
        Default 'best'., optional
    copy_properties_from : int, optional
        The set of twinaxes from which the axes properties should be
        copied to the resulting axes. Default 0.
    auto_recolor : bool, optional
        Set True if artists should be automatically recolored [Default: True].
    auto_rescale : bool, optional
        Automatically rescale all axes to fit the visible data.
    add_colorbars : bool, optional
        If True colorbars are added to the output axes.
        Default True
    add_legends : bool, optional
        If True legends are added to the output axes.
        Default True
    remove_ticklabels : tuple, optional
        If supplied, should be a tuple of four bool values, corresponding to
        each side of the plot (top, right, bottom, left). If a value is True
        the corresponding axis in the output figure will have its ticklabels
        removed.

    Returns
    -------
    axes_colorbars : dict
    """
    output_axes_dict = {('bottom', 'left'): default_output_axes}
    if copy_properties_from >= len(axes_of_figures):
        copy_properties_from = 0
        sywarn('The figure specified as source for the new axes parameter '
               'does not exist. The first figure will be used!')

    axes_legend_props = {}
    axes_legend_labels = defaultdict(list)
    axes_legend_handles = defaultdict(list)
    axes_colorbars = {}

    figure_legend_ax_id = None
    last_axes_drawn_to = default_output_axes
    existing_colors = []

    title = ''
    for idx, axes in enumerate(axes_of_figures):
        cb_axes = _get_colorbar_axes(axes)
        axes = [a for a in axes if a not in cb_axes]
        axes_dict = classify_axes(axes)
        frame_on = any([_get_mpl_axes(source_ax, None)[0].get_frame_on()
                        for _, source_ax
                        in six.iteritems(get_sorted_axes(axes_dict))])

        for ax_id, source_ax in six.iteritems(get_sorted_axes(axes_dict)):
            # save old ids, required to find last added axes
            old_axes_ids = list(output_axes_dict.keys())
            target_ax = get_twin_axes(output_axes_dict, ax_id[0], ax_id[1])
            source_ax, target_ax = _get_mpl_axes(source_ax, target_ax)

            # Copy visibility/frame_on and other properties
            target_ax.set_frame_on(frame_on)
            _copy_axis_visibility(source_ax, target_ax)

            # move supported artists
            colorbars, handles, labels = _move_artists(
                source_ax, target_ax, existing_colors,
                auto_recolor=auto_recolor)

            # save the last added axes
            if ax_id not in old_axes_ids:
                last_axes_drawn_to = target_ax

            if len(title) == 0 or idx == copy_properties_from:
                title = source_ax.get_title()
                if len(title) > 0:
                    target_ax.set_title(title)

            if idx == copy_properties_from:
                copy_axes_parameter(source_ax, target_ax)

            # set converter from source axes to format and locate datetime
            # correctly in only scatter plots
            target_ax.xaxis.converter = source_ax.xaxis.converter
            # call _update_axisinfo to reformat date axis
            target_ax.xaxis._update_axisinfo()
            target_ax.yaxis._update_axisinfo()

            if auto_rescale:
                target_ax.autoscale()

            if remove_ticklabels is not None:
                # Explicitly change the tick locator to FixedLocator to work
                # around a bug where date locators would recurse infinitely
                # during pickle if the ticklabels are cleared.
                if ax_id[0] == 'top' and remove_ticklabels[0]:
                    target_ax.set_xlabel("")
                    target_ax.set_xticklabels([])
                    target_ax.xaxis.set_major_locator(
                        FixedLocator(source_ax.xaxis.get_xticks()))
                    target_ax.xaxis.set_minor_locator(
                        FixedLocator(source_ax.xaxis.get_xticks(minor=True)))
                if ax_id[1] == 'right' and remove_ticklabels[1]:
                    target_ax.set_ylabel("")
                    target_ax.set_yticklabels([])
                    target_ax.yaxis.set_major_locator(
                        FixedLocator(source_ax.get_yticks()))
                    target_ax.xaxis.set_minor_locator(
                        FixedLocator(source_ax.get_yticks(minor=True)))
                if ax_id[0] == 'bottom' and remove_ticklabels[2]:
                    target_ax.set_xlabel("")
                    target_ax.set_xticklabels([])
                    target_ax.xaxis.set_major_locator(
                        FixedLocator(source_ax.get_xticks()))
                    target_ax.xaxis.set_minor_locator(
                        FixedLocator(source_ax.get_xticks(minor=True)))
                if ax_id[1] == 'left' and remove_ticklabels[3]:
                    target_ax.set_ylabel("")
                    target_ax.set_yticklabels([])
                    target_ax.yaxis.set_major_locator(
                        FixedLocator(source_ax.get_yticks()))
                    target_ax.xaxis.set_minor_locator(
                        FixedLocator(source_ax.get_yticks(minor=True)))

            # Check if the axes has a legend and if it seems like a figure
            # legend
            labels_in_legend = set()
            legend = source_ax.get_legend()
            if legend is not None:
                labels_in_legend = {t.get_text() for t in legend.texts}
                if labels_in_legend != set(labels):
                    figure_legend_ax_id = ax_id

            if idx == copy_properties_from or legends_join:
                # Store labels/handles for recreating the legend
                axes_legend_labels[ax_id].extend(labels)
                axes_legend_handles[ax_id].extend(handles)

                # Attempt to recreate legend properties
                if legend is not None:
                    legend_props = {}
                    for prop in models.Legend.NODE_LEAFS:
                        value = None
                        if hasattr(legend, prop):
                            value = getattr(legend, prop)
                        elif hasattr(legend, '_{}'.format(prop)):
                            value = getattr(legend, '_{}'.format(prop))
                        elif hasattr(legend, 'get_{}'.format(prop)):
                            value = getattr(legend, 'get_{}'.format(prop))()
                        elif prop == 'frameon':
                            value = legend.get_frame_on()
                        if value is not None:
                            legend_props[prop] = value
                    if legend_props:
                        legend_props['show'] = True
                    axes_legend_props[ax_id] = legend_props

            if colorbars:
                axes_colorbars[ax_id] = colorbars

    figure_legend_props = axes_legend_props.get(figure_legend_ax_id)

    if add_colorbars and axes_colorbars:
        for colorbars in axes_colorbars.values():
            axes_ = list(get_sorted_axes(output_axes_dict).values())
            for artist_type, artists in six.iteritems(colorbars):
                for (artist, colorbar_params) in artists:
                    _add_colorbar(colorbar_params, artist, axes=axes_)

    if add_legends and figure_legend_props:
        figure_legend_props['loc'] = legend_location
        _draw_figure_legend(last_axes_drawn_to, figure_legend_props,
                            axes_legend_labels, axes_legend_handles)
    elif add_legends:
        _draw_axes_legends(output_axes_dict, axes_legend_props,
                           axes_legend_labels, axes_legend_handles)

    return axes_colorbars


def add_global_colorbar(axes_colorbars, figure):
    """
    Add a global colorbar to a figure.

    Parameters
    ----------
    axes_colorbars : dict
    figure : syfigure.Figure
    """
    for ax_id, colorbars in six.iteritems(axes_colorbars):
        for artist_type, artists in six.iteritems(colorbars):
            if artists:
                for (artist, colorbar_params) in artists:
                    if colorbar_params.pop('show', 'False') == 'True':
                        figure.colorbar(artist, **colorbar_params)
                        break
                break
        break


def _cleanup_legend_props(props):
    title = props.pop('title', None)
    if title and title != 'None':
        if isinstance(title, Text):
            title = title.get_text()
        if title != 'None':
            props['title'] = title
    if 'frameon' in props:
        props['frameon'] = props['frameon'] in ['True', True]
    if 'show' in props:
        props['show'] = props['show'] in ['True', True]
    if 'ncol' in props:
        props['ncol'] = int(props['ncol'])
    return props


def _draw_figure_legend(ax, figure_legend, axes_labels, axes_handles):
    """
    Draw one joined legend for all axes in the figure.

    Adds arrows to labels to denote which axes the artist is part of.

    Parameters
    ----------
    ax: matplotlib Axes
        The Axes where the legend will be drawn.
    figure_legend: dict
        Properties dictionary for the figure legend.
    axes_labels: dict
        A dict mapping axes ids to lists of labels.
    axes_handles: dict
        A dict mapping axes ids to lists of handles.
    """
    lookup = {('bottom', 'left'): r'$\downarrow\leftarrow$',
              ('bottom', 'right'): r'$\downarrow\rightarrow$',
              ('top', 'left'): r'$\uparrow\leftarrow$',
              ('top', 'right'): r'$\uparrow\rightarrow$'}
    legend_handles = []
    legend_labels = []
    multiple_axes = len(set(axes_labels.keys())) > 1
    props = _cleanup_legend_props(figure_legend)

    # Combine the lists of labels and handles for all axes
    for ax_name in axes_labels.keys():
        legend_handles.extend(axes_handles[ax_name])
        if multiple_axes:
            labels = ['{} ({})'.format(l, lookup[ax_name])
                      for l in axes_labels[ax_name]]
        else:
            labels = axes_labels[ax_name]
        legend_labels.extend(labels)

    if not len(legend_labels) or not len(legend_handles):
        return
    if not props.pop('show', False):
        return
    ax.legend(legend_handles, legend_labels, **props)


def _draw_axes_legends(axes_by_name, axes_legends, axes_labels, axes_handles):
    """
    Draw one axes legend for each specified axes legend in the figure.

    Parameters
    ----------
    axes_by_name: dict
        A dict mapping axes ids to matplotlib Axes objects.
    axes_legends: dict
        A dict mapping axes ids to properties dictionaries.
    axes_labels: dict
        A dict mapping axes ids to lists of labels.
    axes_handles: dict
        A dict mapping axes ids to lists of handles.
    """
    for ax_name, props in six.iteritems(axes_legends):
        ax = axes_by_name[ax_name]
        props = _cleanup_legend_props(props)
        handles = axes_handles[ax_name]
        labels = axes_labels[ax_name]

        if not props.pop('show', False):
            continue
        if not len(labels) or not len(handles):
            continue
        ax.legend(handles, labels, **props)


def parse_values_in_dict(d, data_table, extra_vars=None):
    """Parse the values in a dict with `parse_value`."""
    extra_vars = extra_vars or {}
    return {key: (common.parse_value(value, data_table, extra_vars)
                  if isinstance(value, six.text_type) else value)
            for key, value in six.iteritems(d)}


def parse_plots_container(plots_container, data_table):
    """
    Traverse a list of plots parsing all values and expanding iterators.
    """
    parsed_container = []
    for value in plots_container:
        if isinstance(value, dict):
            if value.get('type') == 'iterator':
                parsed_container.extend(
                    expand_iterator(value, data_table))
            else:
                parsed_dict = parse_values_in_dict(value, data_table)
                if 'plots' in value:
                    parsed_dict['plots'] = parse_plots_container(
                        value['plots'], data_table)
                parsed_container.append(parsed_dict)
        else:
            parsed_container.append(common.parse_value(value, data_table))
    return parsed_container


def expand_iterator(iterator_dict, data_table):
    iter_name, iter_expression = iterator_dict['iterable'].split('=', 1)
    iter_name = iter_name.strip()
    if not iter_name:
        iter_name = 'e'
    counter_name = iterator_dict.get('counter', 'i')
    iterable = common.parse_value(iter_expression.strip(), data_table)
    plots = iterator_dict['plots']
    if not plots:
        return
    plot = plots[0]

    parsed_container = []
    for i, e in enumerate(iterable):
        extra_vars = {counter_name: i, iter_name: e}
        parsed_container.append(
            parse_values_in_dict(plot, data_table, extra_vars))
    return parsed_container


def _draw_bar_labels(
        axes, x_coords, y0, values, bar_labels, bar_labels_valign,
        bar_labels_font=None):
    """Draw bar labels onto axes."""
    if y0 is None:
        y0 = np.zeros_like(values)
    y_min, y_max = axes.get_ylim()
    inside = np.logical_not(np.logical_or(y0 > y_max, y0 + values < y_min))

    # Calculate positions based on y limits or bar edges, whichever is smaller.
    y_bot = np.minimum(y0, y_max)
    y_bot = np.maximum(y_bot, y_min)
    y_top = np.minimum(y0 + values, y_max)
    y_top = np.maximum(y_top, y_min)

    if bar_labels_valign == 'over':
        y_pos = y_top
        text_valign = 'bottom'
    elif bar_labels_valign == 'top':
        y_pos = y_top
        text_valign = 'top'
    elif bar_labels_valign == 'center':
        y_pos = np.mean([y_bot, y_top], axis=0)
        text_valign = 'center'
    elif bar_labels_valign == 'bottom':
        y_pos = y_bot
        text_valign = 'bottom'
    elif bar_labels_valign == 'under':
        y_pos = y_bot
        text_valign = 'top'
    else:
        raise ValueError('Unknown value for bar_labels_valign: '
                         '{}'.format(bar_labels_valign))

    if bar_labels_font is None:
        bar_labels_font = {}
    for x, y, s, i in zip(x_coords, y_pos, bar_labels, inside):
        if i:  # Ignore bars that are entirely outside of ylimits
            axes.text(x, y, s, horizontalalignment='center',
                      verticalalignment=text_valign, **bar_labels_font)


def get_fill_coords(bin_edges, values, y0=None):
    """
    Return coordinates suitable for building a histogram using fill_between.
    """
    if y0 is None:
        y0 = np.zeros_like(values)
    fill_x = np.zeros((2*(values.size + 1),))
    fill_x[::2] = bin_edges
    fill_x[1::2] = bin_edges
    fill_y = np.zeros_like(fill_x)
    fill_y[1:-2:2] = values + y0
    fill_y[2:-1:2] = values + y0
    fill_y0 = np.zeros_like(fill_x)
    fill_y0[1:-2:2] = y0
    fill_y0[2:-1:2] = y0
    return fill_x, fill_y, fill_y0


# TODO: This could be put either in figure API or in add_barcontainer.
def barcontainer_plot(axes, values_list, labels=None, grouping='grouped',
                      **kwargs):
    if grouping not in ('grouped', 'stacked'):
        raise ValueError("Invalid value for 'grouping': {}".format(grouping))

    group = None
    last_values = None
    for i, (values, label) in enumerate(zip(values_list, labels)):
        kwargs_ = {}
        for k, v in kwargs.items():
            if v is None:
                continue
            elif isinstance(v, list):
                kwargs_[k] = v[i]
            else:
                kwargs_[k] = v

        if grouping == 'grouped':
            group = i, len(values_list)
        bar_plot(axes, values, label, group=group, y0=last_values, **kwargs_)
        if grouping == 'stacked':
            if last_values is None:
                last_values = np.array(values)
            else:
                last_values += np.array(values)


# TODO: This could be put either in figure API or in add_histcontainer.
def histcontainer_plot(axes, values_list, bin_min_edges, bin_max_edges,
                       **kwargs):
    last_values = None
    for i, values in enumerate(values_list):
        kwargs_ = {}
        for k, v in kwargs.items():
            if v is None:
                continue
            elif isinstance(v, list):
                kwargs_[k] = v[i]
            else:
                kwargs_[k] = v

        hist_plot(axes, values, bin_min_edges, bin_max_edges, y0=last_values,
                  **kwargs_)
        if last_values is None:
            last_values = np.array(values)
        else:
            last_values += np.array(values)


# TODO: I would like to put this method into typeutils/figure.py but this
# module is only working with pure mpl objects.
def bar_plot(axes, values, labels=None, histtype='bar', rwidth=0.8,
             bar_labels=None, bar_labels_valign='center',
             bar_labels_font=None, color=None, group=None, y0=None,
             capsize=10, rot_bin_labels=None, **kwargs):
    """Make a bar plot the way you want it."""
    if not isinstance(values, np.ndarray):
        values = np.array(values)
    if labels is None:
        labels = np.arange(len(values))
    if color is not None:
        kwargs['facecolor'] = color

    x_data = np.arange(len(values))
    left, width = x_data, rwidth

    if histtype == 'bar':
        # Assume unity bin width
        bin_width = 1
        padding = bin_width*(1 - rwidth)/2.0
        left = x_data - bin_width/2.0 + padding
        if group is not None:
            width *= bin_width/group[1]
            left += group[0]*width
        patches = axes.bar(
            left, height=values, width=width, bottom=y0, align='edge',
            capsize=capsize,
            **kwargs)
    else:
        # Use fill_between() instead of hist() to get around bugs in matplotlib
        # histograms with 'step' histtype.
        bin_edges = np.arange(len(values) + 1)
        fill_x, fill_y, fill_y0 = get_fill_coords(bin_edges, values, y0)

        kwargs.setdefault('facecolor', 'none')
        patches = axes.fill_between(fill_x, fill_y0, fill_y, **kwargs)

    # Draw bar labels
    if bar_labels is not None:
        x_coords = left + width/2.0
        _draw_bar_labels(axes, x_coords, y0, values, bar_labels,
                         bar_labels_valign, bar_labels_font)

    # Label the bins on the x axis.
    tick_label_kwargs = {}
    if rot_bin_labels == 'Clockwise':
        tick_label_kwargs = {'ha': 'left', 'rotation': -30}
    elif rot_bin_labels == 'Vertical':
        tick_label_kwargs = {'rotation': -90}
    elif rot_bin_labels == 'Counter clockwise':
        tick_label_kwargs = {'ha': 'right', 'rotation': 30}
    axes.set_xticks(x_data)
    axes.set_xticklabels(labels, **tick_label_kwargs)
    return patches


# TODO: I would like to put this method into typeutils/figure.py but this
# module is only working with pure mpl objects.
def box_plot(axes, values, bin_labels=None,
             color=None, filled=True, alpha=None, marker=None, linewidth=None,
             markersize=None, flier_color=None, manage_ticks=True,
             rot_bin_labels=None, **kwargs):
    """Make a box plot."""
    labels = bin_labels
    if bin_labels is None:
        bin_labels = np.arange(len(values))

    kwargs['sym'] = mpl_utils.lookup_marker(marker)
    flierprops = {}
    if markersize is not None:
        flierprops['markersize'] = markersize
    if flier_color:
        flierprops['markerfacecolor'] = flier_color
    kwargs['flierprops'] = flierprops
    if filled or color is not None:
        kwargs['patch_artist'] = True

    patches = axes.boxplot(values, manage_xticks=manage_ticks, **kwargs)

    if color is not None:
        if not isinstance(color, list):
            color = [color]*len(patches['boxes'])
        for patch, col in zip(patches['boxes'], color):
            patch.set_facecolor(col)
    if alpha:
        for patch_category in patches.values():
            for patch in patch_category:
                patch.set_alpha(alpha)
    if linewidth:
        for name, vals in patches.items():
            for patch in vals:
                patch.set_linewidth(linewidth)

    if labels is not None:
        for patch, label in zip(patches['boxes'], bin_labels):
            patch.remove()
            patch.set_label(label)
            axes.add_artist(patch)

    tick_label_kwargs = {}
    if rot_bin_labels == 'Clockwise':
        tick_label_kwargs = {'ha': 'left', 'rotation': -30}
    elif rot_bin_labels == 'Vertical':
        tick_label_kwargs = {'rotation': -90}
    elif rot_bin_labels == 'Counter clockwise':
        tick_label_kwargs = {'ha': 'right', 'rotation': 30}

    if manage_ticks:
        if 'vert' not in kwargs or kwargs['vert']:
            if 'positions' in kwargs and kwargs['positions'] is not None:
                axes.set_xticks(kwargs['positions'])
            else:
                axes.set_xticks(np.arange(len(values))+1)
            axes.set_xticklabels(bin_labels, **tick_label_kwargs)
        else:
            if 'positions' in kwargs and kwargs['positions'] is not None:
                axes.set_yticks(kwargs['positions'])
            else:
                axes.set_yticks(np.arange(len(values))+1)
            axes.set_yticklabels(bin_labels, **tick_label_kwargs)

    return patches


def timeline(figure_object, axes, xdata, values,
             y_start=0, y_height=0.5, colormap_name='accent (qualitative 8)',
             edgecolor='black', linewidth=2, label=None, text_visible=True,
             add_to_legend=True, filled=True,
             fontsize=12, fontcolor='black', last_step=None,
             **kwargs):

    if len(xdata) != len(values):
        raise SyDataError('Length of X and values must be the same '
                          'in a timeline plot')
    if len(xdata) == 0:
        return
    if len(xdata) < 2:
        raise SyDataError('Dataset for timeline cannot have only one entry')

    all_values = sorted(list(set(values)))
    if colormap_name == 'auto':
        colormap_name = 'tab20  (qualitative 20)'
    try:
        colormap = cm.get_cmap(colors.COLORMAPS[colormap_name])
    except KeyError:
        sywarn("Could not find colormap {}".format(colormap_name))
        colormap = cm.get_cmap(colors.COLORMAPS['tab20  (qualitative 20)'])

    vmin, vmax = colors.get_vmin_vmax(colormap_name)
    if vmax == 1:
        vmax = len(all_values)
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    color_mapping = {key: colormap(norm(i))
                     for i, key in enumerate(all_values)}

    if add_to_legend:
        for i, value in enumerate(all_values):
            axes.scatter([], [], color=colormap(norm(i)), label=value)

    if last_step is None:
        last_step = xdata[-1] - xdata[-2]

    x_starts = []
    x_start = xdata[0]
    labels = []
    cols = []
    prev = values[0]
    for i in range(1, len(xdata)):
        if values[i] != prev:
            if prev != '':
                labels.append(prev)
                x_starts.append((x_start, xdata[i] - x_start))
                cols.append(color_mapping[prev])
            prev = values[i]
            x_start = xdata[i]
    if prev != '':
        labels.append(prev)
        x_starts.append((x_start, xdata[-1] - x_start + last_step))
        cols.append(color_mapping[prev])

    if not filled:
        cols = '#00000000'
    axes.broken_barh(x_starts, (y_start, y_height),
                     facecolors=cols, edgecolor=edgecolor, linewidth=linewidth,
                     **kwargs)

    if label is not None:
        axes.text(x_starts[0][0], y_start+y_height, label+" ",
                  horizontalalignment='left', verticalalignment='bottom',
                  fontsize=12, color='black')

    if text_visible:
        for i, text in enumerate(labels):
            axes.text(x_starts[i][0]+x_starts[i][1]/2, y_start+y_height/2,
                      text, horizontalalignment='center',
                      verticalalignment='center',
                      fontsize=fontsize, color=fontcolor)


def draw_image(figure_object, axes, image, colormap_name='gray', origin=(0, 0),
               width=None, height=None, **kwargs):
    if len(image.shape) == 3 and image.shape[-1] == 1:
        image = image[:, :, 0]
    colormap = cm.get_cmap(colors.COLORMAPS[colormap_name])
    if width is None:
        width = image.shape[1]
    if height is None:
        height = image.shape[0]
    kwargs['extent'] = (origin[0], origin[0]+width,
                        origin[1]+height, origin[1])
    axes.imshow(image, cmap=colormap, **kwargs)


def draw_lines(figure_object, axes,
               startx=None, starty=None, endx=None, endy=None,
               label=None, linestyle='-', linewidth=None,
               color=None, alpha=None, zorder=None,
               marker='', markersize=None, markeredgewidth=None,
               markeredgecolor=None, markerfacecolor=None,
               **kwargs):

    # Promote xdata/ydata to lists or arrays.
    # Any non-scalar ones of them determine length.
    if isinstance(starty, np.ndarray) or isinstance(starty, list):
        N = len(starty)
    else:
        N = 1
    startx = make_iterable(startx, N)
    N = len(startx)
    starty = make_iterable(starty, N)
    endx = make_iterable(endx, N)
    endy = make_iterable(endy, N)

    if len(starty) != N:
        raise SyDataError('Length of starty does not match length of startx')
    if len(endx) != N:
        raise SyDataError('Length of endx does not match length of startx')
    if len(endy) != N:
        raise SyDataError('Length of endy does not match length of startx')

    if isinstance(label, np.ndarray) or isinstance(label, list):
        multi_labels = True
    else:
        multi_labels = False
    labels = make_iterable(label, N)
    linestyles = make_iterable(linestyle, N)
    linewidths = make_iterable(linewidth, N)
    colors = make_iterable(color, N)
    alphas = make_iterable(alpha, N)
    zorders = make_iterable(zorder, N)

    markers = make_iterable(marker, N)
    markersizes = make_iterable(markersize, N)
    markeredgewidths = make_iterable(markeredgewidth, N)
    markeredgecolors = make_iterable(markeredgecolor, N)
    markerfacecolors = make_iterable(markerfacecolor, N)

    if 'linestyle' in kwargs.keys() and kwargs['linestyle'] is None:
        kwargs['linestyle'] = 'none'
    if 'linestyle' not in kwargs.keys():
        kwargs['linestyle'] = '-'

    if 'marker' not in kwargs.keys():
        kwargs['marker'] = ''
    else:
        marker = kwargs.pop('marker')
        for key, value in six.iteritems(mpl_utils.MARKERS):
            if marker == key:
                break
            elif marker == value:
                marker = key
                break
        kwargs['marker'] = marker

    for i, (x0, y0, x1, y1) in enumerate(zip(startx, starty, endx, endy)):
        label = labels[i]
        if multi_labels is False and i != 0:
            label = None
        linestyle = linestyles[i]
        linewidth = linewidths[i]
        color = colors[i]
        alpha = alphas[i]
        zorder = zorders[i]
        marker = markers[i]
        if marker is None:
            marker = ''
        else:
            for key, value in six.iteritems(mpl_utils.MARKERS):
                if marker == key:
                    break
                elif marker == value:
                    marker = key
                    break

        markersize = markersizes[i]
        markeredgewidth = markeredgewidths[i]
        markeredgecolor = markeredgecolors[i]
        markerfacecolor = markerfacecolors[i]

        artist = matplotlib.lines.Line2D(
            [x0, x1], [y0, y1],
            alpha=alpha,
            linewidth=linewidth, linestyle=linestyle,
            color=color, marker=marker, markersize=markersize,
            markeredgewidth=markeredgewidth,
            markeredgecolor=markeredgecolor,
            markerfacecolor=markerfacecolor,
            label=label
        )
        axes.add_line(artist)
        axes.relim()
        axes.autoscale_view(True, True, True)


def draw_box_like(figure_object, axes, artist_fn,
                  xdata=None, ydata=None, width=None, height=None,
                  rotation=None, angle=0.0,
                  label=None, linestyle='-', linewidth=None, fill=True,
                  facecolor=None, edgecolor=None, alpha=None, zorder=None,
                  **kwargs):
    """Draws rectangles, ellipses or other objects
    defined by an XY point and width/height/rotation"""

    # Promote xdata/ydata to lists or arrays.
    # Any non-scalar ones of them determine length.
    if isinstance(ydata, np.ndarray) or isinstance(ydata, list):
        N = len(ydata)
    else:
        N = 1
    xdata = make_iterable(xdata, N)
    N = len(xdata)
    ydata = make_iterable(ydata, N)
    if len(ydata) != N:
        raise SyDataError('Length of ydata does not match length of xdata')
    # Promote width/height to lists or arrays
    width = make_iterable(width, N)
    height = make_iterable(height, N)
    if len(width) != N:
        raise SyDataError('Length of width does not match length of xdata')
    if len(height) != N:
        raise SyDataError('Length of height does not match length of xdata')

    if isinstance(label, np.ndarray) or isinstance(label, list):
        multi_labels = True
    else:
        multi_labels = False
    rotations = make_iterable(rotation, N)
    labels = make_iterable(label, N)
    angles = make_iterable(angle, N)
    linestyles = make_iterable(linestyle, N)
    linewidths = make_iterable(linewidth, N)
    facecolors = make_iterable(facecolor, N)
    edgecolors = make_iterable(edgecolor, N)
    alphas = make_iterable(alpha, N)
    zorders = make_iterable(zorder, N)
    fills = make_iterable(fill, N)

    if 'linestyle' in kwargs.keys() and kwargs['linestyle'] is None:
        kwargs['linestyle'] = 'none'
    if 'linestyle' not in kwargs.keys():
        kwargs['linestyle'] = '-'

    if 'marker' not in kwargs.keys():
        kwargs['marker'] = ''
    else:
        marker = kwargs.pop('marker')
        for key, value in six.iteritems(mpl_utils.MARKERS):
            if marker == key:
                break
            elif marker == value:
                marker = key
                break
        kwargs['marker'] = marker

    for i, (x0, y0, w, h) in enumerate(zip(xdata, ydata, width, height)):
        label = labels[i]
        if multi_labels is False and i != 0:
            label = None
        angle = angles[i]
        rotation = rotations[i]
        linestyle = linestyles[i]
        linewidth = linewidths[i]
        facecolor = facecolors[i]
        edgecolor = edgecolors[i]
        alpha = alphas[i]
        zorder = zorders[i]
        fill = fills[i]

        artist = artist_fn(
            x=x0, y=y0, width=w, height=h,
            angle=angle, alpha=alpha,
            linewidth=linewidth, linestyle=linestyle, fill=fill,
            facecolor=facecolor, edgecolor=edgecolor, label=label
        )
        axes.add_patch(artist)
        axes.relim()
        axes.autoscale_view(True, True, True)


def draw_rectangles(figure_object, axes, **kwargs):
    def artist_fn(x=None, y=None, width=None, height=None, **kwargs):
        return matplotlib.patches.Rectangle(
            [x, y], width, height, **kwargs)
    draw_box_like(figure_object, axes, artist_fn, **kwargs)


def draw_ellipses(figure_object, axes, **kwargs):
    def artist_fn(x=None, y=None, width=None, height=None, **kwargs):
        return matplotlib.patches.Ellipse(
            [x, y], width, height, **kwargs)
    draw_box_like(figure_object, axes, artist_fn, **kwargs)


def annotation(axes, text, textx, texty, background, arrow,
               annotate_x=None, annotate_y=None, fontsize=None, fontcolor=None,
               shrink=0.0, linewidth=None, alpha=None,
               horz_align=None, vert_align=None,
               textalpha=None, rotation=None,
               **kwargs):
    """Adds an annotation (text and arrow) to a graph.
    If no XY point is given for the annotation then only the text is drawn.
    """

    textx = make_iterable_or_none(textx, 1)
    texty = make_iterable_or_none(texty, len(textx))
    text = make_iterable_or_none(text, len(textx))
    fontcolor = make_iterable_or_none(fontcolor, len(textx))
    textalpha = make_iterable_or_none(textalpha, len(textx))
    rotation = make_iterable_or_none(rotation, len(textx))
    horz_align = make_iterable_or_none(horz_align, len(textx))
    vert_align = make_iterable_or_none(vert_align, len(textx))

    if arrow is not None:
        annotate_x = make_iterable_or_none(
            arrow.pop('annotate_x', None), len(textx))
        annotate_y = make_iterable_or_none(
            arrow.pop('annotate_y', None), len(textx))
        arrow_width = make_iterable_or_none(
            arrow.pop('arrow_width', None), len(textx))
        arrow_headwidth = make_iterable_or_none(
            arrow.pop('arrow_headwidth', None), len(textx))
        arrow_length = make_iterable_or_none(
            arrow.pop('arrow_length', None), len(textx))
        facecolor = make_iterable_or_none(
            arrow.pop('facecolor', 'black'), len(textx))
        edgecolor = make_iterable_or_none(
            arrow.pop('edgecolor', 'black'), len(textx))
        shrink = make_iterable_or_none(arrow.pop('shrink', None), len(textx))

    if background is not None:
        bg_color = make_iterable_or_none(
            background.pop('color', None), len(textx))
        bg_border = make_iterable_or_none(
            background.pop('border', None), len(textx))
        bg_style = background.pop('style', None)
        bg_hatch = background.pop('hatch', None)

    if annotate_x is not None and annotate_y is None:
        sywarn("Whenever annotate X is given you must also give annotate Y")
    if annotate_y is not None and annotate_x is None:
        sywarn("Whenever annotate Y is given you must also give annotate X")

    def calc_generic_args(i):
        args = {}
        if horz_align is not None:
            args['ha'] = horz_align[i]
        if vert_align is not None:
            args['va'] = vert_align[i]
        if rotation is not None:
            args['rotation'] = rotation[i]
        if background is not None:
            bbox = {}
            if bg_style is not None and bg_style != 'rounded':
                bbox['boxstyle'] = bg_style
            else:
                bbox['boxstyle'] = 'round'
            if bg_color is not None:
                bbox['facecolor'] = bg_color[i]
            if bg_border is not None:
                bbox['edgecolor'] = bg_border[i]
            # Note: hatch argument is currently ignored by matplotlib
            if bg_hatch is not None:
                bbox['hatch'] = bg_hatch
            args['bbox'] = bbox
        return args

    if arrow is None:
        for i, (t, x, y) in enumerate(zip(text, textx, texty)):
            args = calc_generic_args(i)
            if fontcolor is not None:
                args['color'] = fontcolor[i]
            patches = axes.text(x, y, t, fontsize=fontsize, **args)
            if textalpha is not None:
                patches.set_alpha(textalpha[i])
    else:
        arrowprops = {}
        for i, (t, x, y, ax, ay) in (
                enumerate(zip(text, textx, texty, annotate_x, annotate_y))):
            arrowprops['facecolor'] = facecolor[i]
            arrowprops['edgecolor'] = edgecolor[i]
            if shrink is not None:
                arrowprops['shrink'] = shrink[i]
            if arrow_width is not None:
                arrowprops['width'] = arrow_width[i]
            if arrow_headwidth is not None:
                arrowprops['headwidth'] = arrow_headwidth[i]
            if arrow_length is not None:
                arrowprops['headlength'] = arrow_length[i]
            args = calc_generic_args(i)
            patches = axes.annotate(
                t, xytext=(x, y), xy=(ax, ay),
                fontsize=fontsize,
                arrowprops=arrowprops,
                **args
            )
            if fontcolor is not None:
                patches.set_color(fontcolor[i])
            if textalpha is not None:
                patches.set_alpha(textalpha[i])


def piechart(axes, weights, fontsize=None, fontcolor=None, edgecolor=None,
             linewidth=None, alpha=None, labelhide=False, **kwargs):
    """Make a pie chart."""
    if 'colors' in kwargs:
        if not (isinstance(kwargs['colors'], list) or
                isinstance(kwargs['colors'], np.ndarray)):
            kwargs['colors'] = [kwargs['colors']] * len(weights)
    if 'explode' in kwargs and isinstance(kwargs['explode'], numbers.Number):
        kwargs['explode'] = [kwargs['explode']]*len(weights)
    if 'autopct' in kwargs and kwargs['autopct'] == 'Auto':
        kwargs['autopct'] = '%2d%%'
    wedgeprops = {}
    if linewidth is not None:
        wedgeprops['linewidth'] = linewidth
    if edgecolor is not None:
        wedgeprops['edgecolor'] = edgecolor

    patches = axes.pie(weights, wedgeprops=wedgeprops, **kwargs)

    for L in patches:
        for patch in L:
            if alpha:
                patch.set_alpha(alpha)
            if labelhide and isinstance(patch, matplotlib.text.Text):
                patch.set_text('')
            if fontsize and isinstance(patch, matplotlib.text.Text):
                patch.set_size(fontsize)
            if fontcolor and isinstance(patch, matplotlib.text.Text):
                patch.set_color(fontcolor)


def hist_plot(axes, values, bin_min_edges, bin_max_edges, bar_labels=None,
              bar_labels_valign='center', bar_labels_font=None,
              histtype='bar', color=None, y0=None, **kwargs):
    """Make a histogram plot."""
    if not isinstance(values, np.ndarray):
        values = np.array(values)
    if color is not None:
        kwargs['facecolor'] = color

    if histtype == 'bar':
        width = bin_max_edges - bin_min_edges
        patches = axes.bar(
            bin_min_edges, height=values, width=width, bottom=y0,
            align='edge', **kwargs)
    else:
        # Use fill_between() instead of hist() to get around bugs in matplotlib
        # histograms with 'step' histtype.
        bin_edges = np.append(bin_min_edges, bin_max_edges[-1])
        fill_x, fill_y, fill_y0 = get_fill_coords(bin_edges, values, y0)

        kwargs.setdefault('facecolor', 'none')
        patches = axes.fill_between(fill_x, fill_y0, fill_y, **kwargs)

        try:
            sticky_edges = patches.sticky_edges
        except AttributeError:
            # sticky_edges don't exist prior to matplotlib 2.0
            pass
        else:
            sticky_edges.y[:] = (0,)
            axes.autoscale_view()

    # Draw bar labels
    if bar_labels is not None:
        x_coords = (bin_min_edges + bin_max_edges)/2.0
        _draw_bar_labels(axes, x_coords, y0, values, bar_labels,
                         bar_labels_valign, bar_labels_font)

    return patches


def heatmap_plot(axes, xdata, ydata, zdata, colormap='auto',
                 normalization='linear', vmin=None, vmax=None, aspect='auto',
                 zlabels=None):
    """Create a heatmap."""
    # TODO: Check integrity of xdata and ydata! There should be no reoccuring
    # and no missing indices (x,y).
    unique_x = np.unique(xdata)
    unique_y = np.unique(ydata)
    masked_z = np.ma.masked_all(zdata.shape, zdata.dtype)
    finite_mask = np.isfinite(zdata)
    if isinstance(zdata, np.ma.MaskedArray):
        finite_mask = finite_mask.filled(False)
    masked_z[finite_mask] = zdata[finite_mask]
    if normalization == 'log':
        non_positive_mask = (masked_z <= 0).filled(False)
        if np.any(non_positive_mask):
            sywarn("Ignoring non-positive z-values when using log scale.")
            masked_z.mask = np.logical_or(masked_z.mask, non_positive_mask)

    if len(unique_x) == 1:
        next_x = unique_x[0] + 1
    else:
        x_step = np.median(np.diff(unique_x))
        next_x = max(unique_x) + x_step
    if len(unique_y) == 1:
        next_y = unique_y[0] + 1
    else:
        y_step = np.median(np.diff(unique_y))
        next_y = max(unique_y) + y_step
    x_to_index = dict(zip(unique_x, range(len(unique_x))))
    y_to_index = dict(zip(unique_y, range(len(unique_y))))
    extent = (min(unique_x), next_x, min(unique_y), next_y)
    Z = np.ma.masked_all((len(unique_y), len(unique_x)), dtype=float)
    for x, y, z in zip(xdata, ydata, masked_z):
        xi = x_to_index[x]
        yi = y_to_index[y]
        Z[yi, xi] = z

    # Set up colormap
    colormap = colors.COLORMAPS[colormap]
    if colormap is None:
        # Use sequential colormap by default
        colormap = 'viridis'
        try:
            if np.any(masked_z < 0) and np.any(masked_z > 0):
                # Use diverging colormap
                colormap = 'BrBG'
        except TypeError:
            pass

    if np.all(masked_z.mask):
        # There are no finite values in zdata. z-scale doesn't matter.
        if normalization == 'linear':
            vmin, vmax = 0, 1
        elif normalization == 'log':
            vmin, vmax = 1, 10
    else:
        if colormap in list(colors.DIVERGING_COLORMAPS.values()):
            zabsmax = max(np.abs(np.min(masked_z)), np.abs(np.max(masked_z)))
            if vmin is None:
                vmin = -zabsmax
            if vmax is None:
                vmax = zabsmax
        else:
            if vmin is None:
                vmin = np.min(masked_z)
            if vmax is None:
                vmax = np.max(masked_z)

    if normalization == 'linear':
        norm = matplotlib.colors.Normalize()
    elif normalization == 'log':
        norm = matplotlib.colors.LogNorm()
    heatmap = axes.imshow(
        Z, cmap=colormap, norm=norm, interpolation='none', aspect=aspect,
        extent=extent, vmin=vmin, vmax=vmax, origin='lower')

    # Draw zlabels if selected
    if zlabels is not None:
        for x, y, zlabel in zip(xdata, ydata, zlabels):
            # Never print masked values
            if zlabel is np.ma.masked:
                continue

            # Position in center of bin
            xpos = x + x_step/2
            ypos = y + y_step/2

            # Find a good text color for this bin, choosing white if the
            # bin color is dark and black if the bin color is bright.
            c = heatmap.cmap
            n = heatmap.norm
            xi = x_to_index[x]
            yi = y_to_index[y]
            bg_color_tuple = c(n(Z[yi, xi]))
            bg_brightness = sum(bg_color_tuple[:3]) / 3.0
            if bg_brightness > 0.5:
                text_color = '#000000'
            else:
                text_color = '#FFFFFF'

            axes.text(xpos, ypos, six.text_type(zlabel),
                      horizontalalignment='center',
                      verticalalignment='center',
                      color=text_color, fontsize='small')

    return heatmap


def make_axes_gridspec(parents, **kw):
    """
    Resize and reposition a parent axes, and return a child axes
    suitable for a colorbar. This function is similar to
    make_axes. Primary differences are

     * *make_axes_gridspec* only handles the *orientation* keyword
       and cannot handle the "location" keyword.

     * *make_axes_gridspec* should only be used with a subplot parent.

     * *make_axes* creates an instance of Axes. *make_axes_gridspec*
        creates an instance of Subplot.

     * *make_axes* updates the position of the
        parent. *make_axes_gridspec* replaces the grid_spec attribute
        of the parent with a new one.

    While this function is meant to be compatible with *make_axes*,
    there could be some minor differences.::

        cax, kw = make_axes_gridspec(parent, **kw)

    Keyword arguments may include the following (with defaults):

        *orientation*
            'vertical' or 'horizontal'

    %s

    All but the first of these are stripped from the input kw set.

    Returns (cax, kw), the child axes and the reduced kw dictionary to be
    passed when creating the colorbar instance.
    """

    orientation = kw.setdefault('orientation', 'vertical')
    kw['ticklocation'] = 'auto'

    fraction = kw.pop('fraction', 0.15)
    shrink = kw.pop('shrink', 1.0)
    aspect = kw.pop('aspect', 20)

    x1 = 1.0 - fraction

    # for shrinking
    pad_s = (1. - shrink) * 0.5
    wh_ratios = [pad_s, shrink, pad_s]

    gs_from_subplotspec = gridspec.GridSpecFromSubplotSpec
    parent = parents[0]

    if orientation == 'vertical':
        pad = kw.pop('pad', 0.05)
        if any([p.yaxis.get_ticks_position() == 'right' for p in parents]):
            pad += 0.10

        wh_space = 2 * pad / (1 - pad)

        gs = gs_from_subplotspec(1, 2,
                                 subplot_spec=parent.get_subplotspec(),
                                 wspace=wh_space,
                                 width_ratios=[x1 - pad, fraction]
                                 )

        gs2 = gs_from_subplotspec(3, 1,
                                  subplot_spec=gs[1],
                                  hspace=0.,
                                  height_ratios=wh_ratios,
                                  )

        anchor = (0.0, 0.5)
        panchor = (1.0, 0.5)
    else:
        pad = kw.pop('pad', 0.15)
        wh_space = 2 * pad / (1 - pad)

        gs = gs_from_subplotspec(2, 1,
                                 subplot_spec=parent.get_subplotspec(),
                                 hspace=wh_space,
                                 height_ratios=[x1 - pad, fraction]
                                 )

        gs2 = gs_from_subplotspec(1, 3,
                                  subplot_spec=gs[1],
                                  wspace=0.,
                                  width_ratios=wh_ratios,
                                  )

        aspect = 1.0 / aspect
        anchor = (0.5, 1.0)
        panchor = (0.5, 0.0)

    for parent_ in parents:
        parent_.set_subplotspec(gs[0])
        parent_.update_params()
        parent_.set_position(parent_.figbox)
        parent_.set_anchor(panchor)

    fig = parent.get_figure()
    cax = fig.add_subplot(gs2[1])
    cax.set_aspect(aspect, anchor=anchor, adjustable='box')
    return cax, kw


def _add_colorbar(colorbar, artist, axes=None):
    """
    Add a colorbar for given artist to the figure.

    Parameters
    ----------
    colorbar : dict
        Dictionary of parameters.
    artist : matplotlib.artist.Artist
        The artist which should be linked to the colorbar.
    axes : matplotlib.axes.Axes or list, optional
        None | parent axes object(s) from which space for a new colorbar axes
        will be stolen. If a list of axes is given they will all be resized to
        make room for the colorbar axes.

    Returns
    -------
    cb : matplotlib.colorbar.Colorbar
    """
    figure = artist.get_figure()

    if colorbar is not None and colorbar.get('show') == 'True':
        orientation = colorbar.get('orientation', 'vertical')
        ax = axes if axes is not None else figure.axes
        if isinstance(axes, Iterable):
            cax, kw = make_axes_gridspec(ax, orientation=orientation)
            cb = figure.colorbar(artist, cax=cax, **kw)
        else:
            cb = figure.colorbar(artist, ax=ax, orientation=orientation)
        cb_label = colorbar.get('label')
        if cb_label:
            cb.set_label(cb_label)
        return cb
    return None


def _recreate_colorbar(old_artist, new_artist):
    colorbar_params = _get_colorbar_properties(old_artist)
    _add_colorbar(colorbar_params, new_artist)


def _get_colorbar_properties(old_artist):
    """
    Returns the parameters for recreating the colorbar.

    Parameters
    ----------
    old_artist : matplotlib.artist.Artist
        The artist whose colorbar to copy.

    Returns
    -------
    colorbar : dict
        Dictionary of parameters.
    """
    cb = getattr(old_artist, 'colorbar')
    if cb is not None:
        colorbar = {'show': 'True',
                    'orientation': cb.orientation}
        if hasattr(cb, '_label') and cb._label:
            colorbar['label'] = cb._label
        return colorbar
    else:
        return {}


def is_numeric_ndarray(arr):
    return isinstance(arr, np.ndarray) and arr.dtype.kind in 'fuiMm'


class CreateFigure(object):
    """
    This :class:`CreateFigure` class is used to create a populate a
    ``matplotlib`` figure with data from `date_table` as defined in
    `parsed_param`.
    """
    def __init__(self, data_table, figure, parsed_param):

        self.data_table = data_table
        self.figure = figure
        self.parsed_param = copy.deepcopy(parsed_param)
        self.axes = {
            ('bottom', 'left'): self.figure.first_subplot().get_mpl_axes()}
        self.axes_by_name = {('bottom', 'left'): self.axes[('bottom', 'left')]}
        self.axes_legends = {}
        self.global_legend_properties = None
        self.last_axes_drawn_to = None
        self.xaxes_with_dates = {}

    def create_figure(self):
        fig_param = self.parsed_param['figure']
        self.apply_figure_parameters(fig_param)
        ax_params = fig_param.get('axes', {})
        self.apply_axes_parameters(ax_params)

        for axes_param in ax_params:
            xaxis = axes_param.get('xaxis', {})
            yaxis = axes_param.get('yaxis', {})
            xaxis_pos = xaxis.get('position', 'bottom')
            yaxis_pos = yaxis.get('position', 'left')
            ax = self.axes[(xaxis_pos, yaxis_pos)]
            plots = parse_plots_container(
                axes_param.get('plots', []), self.data_table)
            for plot_param in plots:
                plot_type = plot_param.pop('type')
                if plot_type == 'line':
                    self.add_lineplot(ax, plot_param)
                elif plot_type == 'scatter':
                    self.add_scatter(ax, plot_param)
                elif plot_type == 'bar':
                    self.add_bars(ax, plot_param)
                elif plot_type == 'barcontainer':
                    self.add_barcontainer(ax, plot_param)
                elif plot_type == 'hist':
                    self.add_hist(ax, plot_param)
                elif plot_type == 'histcontainer':
                    self.add_histcontainer(ax, plot_param)
                elif plot_type == 'heatmap':
                    self.add_heatmap(ax, plot_param)
                elif plot_type == 'box':
                    self.add_boxplot(ax, plot_param)
                elif plot_type == 'pie':
                    self.add_piechart(ax, plot_param)
                elif plot_type == 'annotation':
                    self.add_annotation(ax, plot_param)
                elif plot_type == 'timeline':
                    self.add_timeline(ax, plot_param)
                elif plot_type == 'image':
                    self.add_image(ax, plot_param)
                elif plot_type == 'lines':
                    self.add_lines(ax, plot_param)
                elif plot_type == 'rectangles':
                    self.add_rectangles(ax, plot_param)
                elif plot_type == 'ellipses':
                    self.add_ellipses(ax, plot_param)
            self.last_axes_drawn_to = ax

        self.draw_legends()

        for axes, xlim in six.iteritems(self.xaxes_with_dates):
            axes.set_xlim(xlim)
        return self.figure

    def update_date_axes_xlimits(self, axes, xlim):
        old_xlim = self.xaxes_with_dates.get(axes)
        if old_xlim:
            xlim = (min(old_xlim[0], xlim[0]), max(old_xlim[1], xlim[1]))
        self.xaxes_with_dates[axes] = xlim

    def apply_axes_parameters(self, parameters):
        """Create all defined axes."""
        for axes_params in parameters:
            axes_params = copy.deepcopy(axes_params)
            axes_params.pop('type')

            xaxis = axes_params.pop('xaxis', {})
            yaxis = axes_params.pop('yaxis', {})
            # Parsed in: apply_axes_grid_parameters()
            grid_params = axes_params.pop('grid', None)
            xaxis = parse_values_in_dict(xaxis, self.data_table)
            yaxis = parse_values_in_dict(yaxis, self.data_table)
            axes_params = parse_values_in_dict(axes_params, self.data_table)

            # add a grid if specified
            frameon = axes_params.pop('frameon', None)
            color = axes_params.pop('color', None)
            spinex = xaxis.pop('spinex', 'default')
            spiney = yaxis.pop('spiney', 'default')
            xlabel = xaxis.pop('label', None)
            ylabel = yaxis.pop('label', None)

            x_minor_ticks = xaxis.pop('minor_ticks', None)
            y_minor_ticks = yaxis.pop('minor_ticks', None)
            x_major_ticks = xaxis.pop('major_ticks', None)
            y_major_ticks = yaxis.pop('major_ticks', None)

            # create the defined axes
            xaxis_pos = xaxis.get('position', 'bottom')
            yaxis_pos = yaxis.get('position', 'left')

            for l, axis in zip('xy', [xaxis, yaxis]):
                for key in ['scale', 'lim']:
                    value = axis.get(key)
                    if value is not None:
                        axes_params[l+key] = value

            # save legend parameters for later handling
            self.axes_legends[(xaxis_pos, yaxis_pos)] = axes_params.pop(
                'legend', {'show': False})

            ax = get_twin_axes(self.axes, xaxis_pos, yaxis_pos)
            self.axes_by_name[(xaxis_pos, yaxis_pos)] = ax
            if color is not None:
                ax.set_facecolor(color)

            # If an axis is shared between two axes its label needs to be set
            # on the original axes in order to be shown. This question
            # describes the problem/bug:
            # https://stackoverflow.com/q/23702364/1529178
            if xlabel is not None:
                if xaxis_pos == 'bottom':
                    label_axes = self.axes[('bottom', 'left')]
                else:
                    label_axes = ax
                label_axes.set_xlabel(xlabel)
            if ylabel is not None:
                if yaxis_pos == 'left':
                    label_axes = self.axes[('bottom', 'left')]
                elif xaxis_pos == 'top':
                    label_axes = self.axes[('bottom', 'right')]
                else:
                    label_axes = ax
                label_axes.set_ylabel(ylabel)

            if grid_params is not None:
                self.apply_axes_grid_parameters(ax, grid_params)

            # evaluate parameters
            axes_params.pop('plots', None)
            if isinstance(ax, SyAxes):
                ax = ax.get_mpl_axes()
            color_cycle_name = axes_params.pop('color_cycle', 'default')
            color_cycle = colors.COLOR_CYCLES.get(color_cycle_name, 'default')

            ax.set(**axes_params)
            mpl_utils.set_color_cycle(ax, color_cycle)

            if spinex != 'default':
                ax.spines['bottom'].set_position(spinex)
                ax.spines['top'].set_color('none')
            if spiney != 'default':
                ax.spines['left'].set_position(spiney)
                ax.spines['right'].set_color('none')

            if x_major_ticks is not None:
                ax.set_xticks(x_major_ticks)
            if x_minor_ticks is not None:
                ax.set_xticks(x_minor_ticks, minor=True)
            if y_major_ticks is not None:
                ax.set_yticks(y_major_ticks)
            if y_minor_ticks is not None:
                ax.set_yticks(y_minor_ticks, minor=True)

            if xaxis.get('visible') is not None:
                ax.get_xaxis().set_visible(xaxis.get('visible'))
            if yaxis.get('visible') is not None:
                ax.get_yaxis().set_visible(yaxis.get('visible'))
            if frameon is not None:
                ax.set_frame_on(frameon)

    def add_bars(self, axes, bar):
        ydata = bar.pop('ydata')

        # get the column data if data is specified as string
        if (isinstance(ydata, six.text_type) and
                ydata in self.data_table.column_names()):
            ydata = self.data_table.get_column_to_array(ydata)

        if not is_numeric_ndarray(ydata):
            sywarn('The data for line plot is not accessible and '
                   'will not be plotted!')
            return

        bin_labels = bar.pop('bin_labels', None)
        bar_plot(axes, ydata, bin_labels, **bar)

    def add_barcontainer(self, axes, barcontainer):
        """Add a list of bar plots (stacked or grouped)."""
        plots = barcontainer.pop('plots')

        bar_list_params = defaultdict(list)
        listable_params = [
            # Mandatory:
            'ydata',
            # Very reasonable ones:
            'label', 'bar_labels', 'color', 'edgecolor',
            # Slightly less reasonable ones:
            'bar_labels_valign', 'linewidth', 'linestyle', 'alpha', 'zorder',
            'bin_labels', 'bar_labels_font'
            # Not allowed:
            # 'axes'
        ]

        color_cycle = itertools.cycle(mpl_utils.color_cycle(axes))

        # Create lists of parameters
        for i, bar in enumerate(plots):
            for k in listable_params:
                value = bar.get(k, None)
                if k == 'color' and value is None:
                    value = six.next(color_cycle)
                elif k == 'ydata' and not is_numeric_ndarray(value):
                    sywarn('The data for Bar plot in the Bar Container '
                           'is not accessible and will not be plotted!')
                    value = None
                bar_list_params[k].append(value)

        # Remove lists with only None
        for k, v in list(bar_list_params.items()):
            if all(e is None for e in v):
                del bar_list_params[k]
        bar_list_params = {k: v for k, v in bar_list_params.items()
                           if any(e is not None for e in v)}

        barcontainer.update(bar_list_params)
        ydata = barcontainer.pop('ydata', None)
        bin_labels = barcontainer.pop('bin_labels', None)
        grouping = barcontainer.pop('grouping', None)
        if ydata is None:
            sywarn('No y-data specified. Please check the configuration.')
        else:
            barcontainer_plot(axes, ydata, bin_labels, grouping=grouping,
                              **barcontainer)

    def add_boxplot(self, axes, args):
        ydata_old = args.pop('ydata')

        if not isinstance(ydata_old, list):
            ydata_old = [ydata_old]

        ydata = []
        for yvalue in ydata_old:
            if isinstance(yvalue, six.string_types):
                if yvalue in self.data_table.column_names():
                    yvalue = self.data_table.get_column_to_array(yvalue)
                else:
                    sywarn('Cannot find column named: '+yvalue)
            if isinstance(yvalue, list):
                yvalue = np.array(yvalue)
            if not is_numeric_ndarray(yvalue):
                sywarn('Some data for box plot is invalid and will '
                       'not be plotted!')
                ydata.append([])
            else:
                ydata.append(yvalue)

        positions = args.pop('positions', None)
        if positions is not None:
            if isinstance(positions, six.string_types):
                if positions in self.data_table.column_names():
                    positions = self.data_table.get_column_to_array(positions)
            elif isinstance(positions, numbers.Number):
                positions = np.arange(len(ydata)) + positions

        box_plot(axes, ydata, positions=positions, **args)

    def add_piechart(self, axes, args):
        weights = args.pop('weights')
        piechart(axes, weights, **args)

    def add_annotation(self, axes, args):
        text = args.pop('text')
        textx = args.pop('textx')
        texty = args.pop('texty')
        box_background = args.pop('boxbackground', None)
        if box_background is not None:
            box_background = parse_values_in_dict(
                box_background, self.data_table)
        arrow = args.pop('arrow', None)
        if arrow is not None:
            arrow = parse_values_in_dict(arrow, self.data_table)

        annotation(axes, text, textx, texty, box_background, arrow, **args)

    def add_timeline(self, axes, args):
        xdata = args.pop('xdata')
        values = args.pop('values')

        timeline(self, axes, xdata, values, **args)

    def add_image(self, axes, args):
        im = args.pop('image')
        draw_image(self, axes, im, **args)

    def add_lines(self, axes, args):
        draw_lines(self, axes, **args)

    def add_rectangles(self, axes, args):
        draw_rectangles(self, axes, **args)

    def add_ellipses(self, axes, args):
        draw_ellipses(self, axes, **args)

    def add_hist(self, axes, hist):
        bin_min_edges = hist.pop('bin_min_edges')
        bin_max_edges = hist.pop('bin_max_edges')
        ydata = hist.pop('ydata')

        # get the column data if data is specified as string
        if (isinstance(bin_min_edges, six.text_type) and
                bin_min_edges in self.data_table.column_names()):
            bin_min_edges = self.data_table.get_column_to_array(
                bin_min_edges)
        if (isinstance(bin_max_edges, six.text_type) and
                bin_max_edges in self.data_table.column_names()):
            bin_max_edges = self.data_table.get_column_to_array(
                bin_max_edges)
        if (isinstance(ydata, six.text_type) and
                ydata in self.data_table.column_names()):
            ydata = self.data_table.get_column_to_array(ydata)

        if (not is_numeric_ndarray(bin_min_edges) or
                not is_numeric_ndarray(bin_max_edges) or
                not is_numeric_ndarray(ydata)):
            sywarn('The data for hist plot is not accessible and '
                   'will not be plotted!')
            return
        # # TODO: Handle datetimes, at least for x data
        # xdate = xdata.dtype.kind == 'M'
        # ydate = ydata.dtype.kind == 'M'
        # if xdate or ydate:
        #     if xdate:
        #         xdata = xdata.astype(datetime)
        #     if ydate:
        #         ydata = ydata.astype(datetime)
        #     hist['xdate'] = xdate
        #     hist['ydate'] = ydate

        #     axes.plot_date(xdata, ydata, **hist)
        hist_plot(axes, ydata, bin_min_edges, bin_max_edges, **hist)

    def add_histcontainer(self, axes, histcontainer):
        """Add a list of hist stacked plots."""
        plots = histcontainer.pop('plots')

        # axes_desc = histcontainer.pop('axes', '_default_')
        # axes = self.axes_by_name.get(axes_desc)
        hist_list_params = defaultdict(list)
        listable_params = [
            # Mandatory:
            'ydata',
            # Very resonable ones:
            'label', 'bar_labels', 'color', 'edgecolor', 'bar_labels_font',
            # Slightly less resonable ones:
            'hist_labels_valign', 'linewidth', 'linestyle', 'alpha', 'zorder'
            # Not allowed:
            # 'bin_min_edges', 'bin_max_edges', 'axes', 'histtype'
        ]

        possible_glob_params = [
            'bin_min_edges', 'bin_max_edges',
        ]

        color_cycle = itertools.cycle(mpl_utils.color_cycle(axes))

        # Create lists of parameters
        for hist in plots:
            for k in listable_params:
                value = hist.get(k, histcontainer.get(k, None))
                if k == 'color' and value is None:
                    value = six.next(color_cycle)
                elif (k in ['bin_min_edges', 'bin_max_edges', 'ydata'] and
                      not is_numeric_ndarray(value)):
                    sywarn('The data for Histogram plot in the '
                           'Histogram Container is not '
                           'accessible and will not be plotted!')
                    value = None
                hist_list_params[k].append(value)

            for k in possible_glob_params:
                if k not in histcontainer:
                    value = hist.get(k, None)
                    if value is not None:
                        histcontainer[k] = value

        # Remove lists with only None
        for k, v in list(hist_list_params.items()):
            if all(e is None for e in v):
                del hist_list_params[k]
        hist_list_params = {k: v for k, v in hist_list_params.items()
                            if any(e is not None for e in v)}

        histcontainer.update(hist_list_params)
        bin_min_edges = histcontainer.pop('bin_min_edges', None)
        bin_max_edges = histcontainer.pop('bin_max_edges', None)
        ydata = histcontainer.pop('ydata', None)
        if bin_max_edges is None or bin_min_edges is None or ydata is None:
            if bin_min_edges is None:
                sywarn('"Bin min edges" are incorrect defined. '
                       'Check configuration.')
            if bin_max_edges is None:
                sywarn('"Bin max edges" are incorrect defined. '
                       'Check configuration.')
            if ydata is None:
                sywarn('"y-data" is incorrect defined. Check configuration.')
        else:
            histcontainer_plot(axes, ydata, bin_min_edges, bin_max_edges,
                               **histcontainer)

    def add_lineplot(self, axes, line):
        xdata = line.pop('xdata')
        ydata = line.pop('ydata')

        # get the column data if data is specified as string
        if (isinstance(xdata, six.text_type) and
                xdata in self.data_table.column_names()):
            xdata = self.data_table.get_column_to_array(xdata)
        if (isinstance(ydata, six.text_type) and
                ydata in self.data_table.column_names()):
            ydata = self.data_table.get_column_to_array(ydata)

        if not is_numeric_ndarray(xdata) or not is_numeric_ndarray(ydata):
            sywarn('The data for line plot is not accessible and '
                   'will not be plotted!')
            return

        if 'marker' in line:
            marker = line.pop('marker')
            for key, value in six.iteritems(mpl_utils.MARKERS):
                if marker == key:
                    break
                elif marker == value:
                    marker = key
                    break
            line['marker'] = marker

        # cleanup parameters
        if 'linestyle' in line.keys() and line['linestyle'] is None:
            line['linestyle'] = 'none'
        # required to plot as lines and not as markers
        if 'linestyle' not in line.keys():
            line['linestyle'] = '-'
        if 'marker' not in line.keys():
            line['marker'] = ''
        # make sure color values are given in correct format
        for color_key in ['color', 'markeredgecolor', 'markerfacecolor']:
            if color_key in line:
                line[color_key] = colors.parse_to_mpl_color(line[color_key])

        xdate = xdata.dtype.kind == 'M'
        ydate = ydata.dtype.kind == 'M'
        if xdate or ydate:
            if xdate:
                xdata = xdata.astype(datetime)
            if ydate:
                ydata = ydata.astype(datetime)
            line['xdate'] = xdate
            line['ydate'] = ydate

            axes.plot_date(xdata, ydata, **line)

            if xdate:
                self.update_date_axes_xlimits(axes, axes.get_xlim())
        else:
            axes.plot(xdata, ydata, **line)

    def add_scatter(self, axes, scatter):
        xdata = scatter.pop('xdata')
        ydata = scatter.pop('ydata')
        colorbar = scatter.pop('colorbar', None)
        errorbar = scatter.pop('errorbar', None)
        if errorbar is not None:
            errorbar = parse_values_in_dict(errorbar, self.data_table)

        # get the column data if data is specified as string
        if (isinstance(xdata, six.text_type) and
                xdata in self.data_table.column_names()):
            xdata = self.data_table.get_column_to_array(xdata)
        if (isinstance(ydata, six.text_type) and
                ydata in self.data_table.column_names()):
            ydata = self.data_table.get_column_to_array(ydata)

        if not is_numeric_ndarray(xdata) or not is_numeric_ndarray(ydata):
            sywarn('The data for scatter plot is not accessible and '
                   'will not be plotted!')
            return

        xdate = xdata.dtype.kind == 'M'
        ydate = ydata.dtype.kind == 'M'
        if xdate or ydate:
            if xdate:
                xdata = xdata.astype(datetime)
            if ydate:
                ydata = ydata.astype(datetime)

        # make sure color values are given in correct format
        vmin = scatter.get('vmin')
        vmax = scatter.get('vmax')

        if 'color' in scatter:
            color = scatter.pop('color')
            if (isinstance(color, six.text_type) and
                    color in self.data_table.column_names()):
                color = self.data_table.get_column_to_array(color)
            elif isinstance(color, np.ndarray):
                # Set up colormap
                colormap = colors.COLORMAPS[scatter.get('cmap', 'auto')]
                if colormap is None:
                    # Use sequential colormap 'magma' by default
                    colormap = 'magma'
                    try:
                        if np.any(color < 0) and np.any(color > 0):
                            # Use diverging colormap
                            colormap = 'BrBG'
                    except TypeError:
                        pass

                if colormap in list(colors.DIVERGING_COLORMAPS.values()):
                    c_abs_max = max(abs(min(color)),
                                    abs(max(color)))
                    if vmin is None:
                        vmin = -c_abs_max
                    if vmax is None:
                        vmax = c_abs_max
                else:
                    if vmin is None:
                        vmin = min(color)
                    if vmax is None:
                        vmax = max(color)
                scatter['vmin'] = vmin
                scatter['vmax'] = vmax
                scatter['cmap'] = colormap
            else:
                color = colors.parse_to_mpl_color(color)
            scatter['c'] = color

        if 'marker' in scatter:
            marker = scatter.pop('marker', 'circle')
            for key, value in six.iteritems(mpl_utils.MARKERS):
                if marker == key:
                    break
                elif marker == value:
                    marker = key
                    break
            scatter['marker'] = marker

        # plot error bars before scatter to appear below
        if errorbar is not None:
            alpha = errorbar.pop('alpha', None)
            res = axes.errorbar(xdata, ydata, fmt='none',
                                barsabove=False, **errorbar)
            artists = list(res[1]) + list(res[2])
            if alpha is not None:
                for artist in artists:
                    artist.set_alpha(alpha)

        # plot scatter
        artist = axes.scatter(xdata, ydata, **scatter)

        if xdate:
            axes.xaxis_date(tz=None)
        if ydate:
            axes.yaxis_date(tz=None)

        axes.autoscale_view()

        if xdate:
            # fix autoscaling for scatter plots
            # the datetime must be converted to floats to be comparable
            xmin = mpl_dates.date2num(xdata.min())
            xmax = mpl_dates.date2num(xdata.max())
            xr = xmax - xmin
            xlim = (xmin - xr * axes._xmargin, xmax + xr * axes._xmargin)
            self.update_date_axes_xlimits(axes, xlim)

        _add_colorbar(colorbar, artist,
                      axes=list(get_sorted_axes(self.axes_by_name).values()))

    def add_heatmap(self, axes, heatmap):
        xdata = heatmap.pop('xdata')
        ydata = heatmap.pop('ydata')
        zdata = heatmap.pop('zdata')
        colorbar = heatmap.pop('colorbar', None)

        # get the column data if data is specified as string
        if (isinstance(xdata, six.text_type) and
                xdata in self.data_table.column_names()):
            xdata = self.data_table.get_column_to_array(xdata)
        if (isinstance(ydata, six.text_type) and
                ydata in self.data_table.column_names()):
            ydata = self.data_table.get_column_to_array(ydata)
        if (isinstance(zdata, six.text_type) and
                zdata in self.data_table.column_names()):
            zdata = self.data_table.get_column_to_array(zdata)

        if (not is_numeric_ndarray(xdata) or
                not is_numeric_ndarray(ydata) or
                not is_numeric_ndarray(zdata)):
            sywarn('The data for heatmap plot is not accessible and '
                   'will not be plotted!')
            return

        diverging = heatmap.get('colormap') in list(
            colors.DIVERGING_COLORMAPS.keys())
        log_scale = heatmap.get('normalization') == 'log'
        if diverging and log_scale:
            raise SyConfigurationError(
                "Can't use diverging colormaps with logarithmic colormap "
                "scale.")

        xdate = xdata.dtype.kind == 'M'
        ydate = ydata.dtype.kind == 'M'
        if xdate or ydate:
            if xdate:
                xdata = xdata.astype(datetime)
            if ydate:
                ydata = ydata.astype(datetime)

        artist = heatmap_plot(axes, xdata, ydata, zdata, **heatmap)
        _add_colorbar(colorbar, artist,
                      axes=list(get_sorted_axes(self.axes_by_name).values()))

        if xdate:
            axes.xaxis_date(tz=None)
        if ydate:
            axes.yaxis_date(tz=None)

        axes.autoscale_view()

        if xdate:
            # fix autoscaling for scatter plots
            # the datetime must be converted to floats to be comparable
            xmin = mpl_dates.date2num(xdata.min())
            xmax = mpl_dates.date2num(xdata.max())
            xr = xmax - xmin
            xlim = (xmin - xr * axes._xmargin, xmax + xr * axes._xmargin)
            self.update_date_axes_xlimits(axes, xlim)

    def draw_legends(self):
        axes_labels = {}
        axes_handles = {}
        for ax_name, ax in self.axes.items():
            handles, labels = ax.get_legend_handles_labels()
            axes_labels[ax_name] = labels
            axes_handles[ax_name] = handles
        if self.global_legend_properties is not None:
            ax = self.last_axes_drawn_to or self.axes.get(('bottom', 'left'))
            # print(self.global_legend_properties)
            # print(axes_labels)
            # print(axes_handles)
            _draw_figure_legend(ax, self.global_legend_properties,
                                axes_labels, axes_handles)
        else:
            _draw_axes_legends(self.axes, self.axes_legends,
                               axes_labels, axes_handles)

    def apply_figure_parameters(self, parameters):
        parameters = parse_values_in_dict(parameters, self.data_table)
        for param, value in six.iteritems(parameters):
            if param == 'title':
                self.figure.set_title(value)
                # set the default tight layout to false
                # if figure suptitle is set
                self.figure.get_mpl_figure().set_tight_layout(False)
                self.figure.subplots_adjust(top=0.85)
            elif param == 'legend':
                self.global_legend_properties = value

    def apply_axes_grid_parameters(self, axes, params):
        parsed_params = parse_values_in_dict(params, self.data_table)
        if parsed_params.pop('show', False):
            axes.grid(**parsed_params)

    def apply_axes_legend_parameters(self, axes, params):
        parsed_params = parse_values_in_dict(params, self.data_table)
        if parsed_params.pop('show', False):
            axes.legend(**parsed_params)
