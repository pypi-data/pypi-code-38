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
"""Renderer of heatmap plots for MPL."""
from __future__ import (
    print_function, division, unicode_literals, absolute_import)
import functools
import itertools
import six
import numpy as np
import matplotlib.colors
from sympathy.api import exceptions as syexceptions

from sylib.report import models
from sylib.report import plugins
from sylib.report import editor_type
from sylib.report import data_manager
mpl_backend = plugins.get_backend('mpl')


def get_axis_range(layer_model, dimension, data):
    axis_id = layer_model.children[0].children[dimension].data['axis']
    axis_model = layer_model.parent.parent.children[0].find_node(
        models.GraphAxis, axis_id)
    if axis_model.data['extent']:
        axis_min = np.amin(data)
        axis_max = np.amax(data)
    else:
        axis_min = axis_model.data['min']
        axis_max = axis_model.data['max']
    return axis_min, axis_max


def get_reduce_function(f_name):
    if f_name == 'median':
        return np.median
    elif f_name == 'mean':
        return np.mean
    elif f_name == 'min':
        return np.amin
    elif f_name == 'max':
        return np.amax


def create_layer(binding_context, parameters):
    """
    Build layer for MPL and bind properties using binding context.
    :param binding_context: Binding context.
    :param parameters: Dictionary containing:
                       'layer_model': a model.GraphLayer instance,
                       'axes': the MPL-axes to add layer to,
                       'canvas': canvas (Qt-widget) that we are rendering to,
                       'z_order': Z-order of layer.
    :return: MPL-element which can be added to Axes.
    """
    # This is our context to be shared by setters of bindings.
    context = {
        'binding_context': binding_context,
        'artist': {'pcol': None, 'colorbar': None, 'texts': []},
        'x_bin_values': [],
        'x_bin_edges': [],
        'layer_model': parameters['layer_model'],
        'axes': parameters['axes'],
        'canvas': parameters['canvas'],
        'z_order': parameters['z_order'],
        'properties': []
    }

    def update_data(context_, _):
        properties_ = context_['layer_model'].properties_as_dict()
        # Remove old artist.
        if context_['artist']['colorbar'] is not None:
            ax = context_['artist']['colorbar'].ax
            fig = ax.figure
            try:
                context_['artist']['colorbar'].remove()
            except AttributeError:
                # The remove method on colorbar objects was added
                # in matplotlib 1.4. This fall back will not restore the
                # plot's gridspec so the call to subplots_adjust won't do
                # anything in this case.
                fig.delaxes(context_['artist']['colorbar'].ax)
            fig.subplots_adjust(left=0.1, bottom=0.1, right=0.97, top=0.92)
            context_['artist']['colorbar'] = None
        if context_['artist']['pcol'] is not None:
            try:
                context_['artist']['pcol'].remove()
            except NotImplementedError:
                # The remove method is not implemented for some versions of
                # matplotlib.
                context_['axes'].images.remove(context_['artist']['pcol'])
            context_['artist']['pcol'] = None
        if context_['artist']['texts']:
            for text_artist in context_['artist']['texts']:
                text_artist.remove()
            context_['artist']['texts'] = []

        (x_data, y_data), _ = (context_['layer_model']
                               .extract_data_and_properties())
        if len(x_data) == 0 or len(y_data) == 0:
            context_['canvas'].draw_idle()
            return
        x_bins = properties_['x-bin-count'].get()
        y_bins = properties_['y-bin-count'].get()

        # Make sure that the histogram will fill up the entire plot
        x_range = get_axis_range(context_['layer_model'], 0, x_data)
        y_range = get_axis_range(context_['layer_model'], 1, y_data)

        if properties_['reduce-func'].get() == 'count':
            # Use numpy method for histograms
            (context_['bin_values'],
             context_['x_bin_edges'],
             context_['y_bin_edges']) = np.histogram2d(
                 x_data, y_data, range=(x_range, y_range),
                 bins=(x_bins, y_bins), normed=False)
        else:
            # Use manual method for other types of reductions
            context_['x_bin_edges'] = np.linspace(
                x_range[0], x_range[1], x_bins + 1)
            context_['y_bin_edges'] = np.linspace(
                y_range[0], y_range[1], y_bins + 1)

            within_x = np.logical_and(
                x_range[0] <= x_data, x_data < x_range[1])
            within_y = np.logical_and(
                y_range[0] <= y_data, y_data < y_range[1])
            within_range = np.logical_and(within_x, within_y)
            if not x_data[within_range].size or not y_data[within_range].size:
                context_['canvas'].draw_idle()
                return

            x_bin_indices = np.digitize(
                x_data[within_range], context_['x_bin_edges'])
            y_bin_indices = np.digitize(y_data[
                within_range], context_['y_bin_edges'])

            z_source = properties_['z-source'].get()
            z_data = data_manager.data_source.data(z_source)

            context_['bin_values'] = np.zeros((x_bins, y_bins))
            reduce_f = get_reduce_function(properties['reduce-func'].get())

            # Build the values buffer. The values buffer holds a list of z
            # values for each bin.
            values_buffer = np.empty((x_bins, y_bins), dtype=object)
            for x_bin_index, y_bin_index, z in six.moves.zip(
                    x_bin_indices, y_bin_indices, z_data):
                if 0 < x_bin_index <= x_bins and 0 < y_bin_index <= y_bins:
                    xi = x_bin_index - 1
                    yi = y_bin_index - 1
                else:
                    print("bin doesn't exist: (x_bin_index, y_bin_index)")
                    continue
                if values_buffer[xi, yi] is None:
                    values_buffer[xi, yi] = []
                values_buffer[xi, yi].append(z)

            # Now go through the values buffer and reduce each list into the
            # real z data for that bin.
            for xi, yi in itertools.product(six.moves.range(x_bins),
                                            six.moves.range(y_bins)):
                z_values = values_buffer[xi, yi]
                if z_values is not None:
                    context_['bin_values'][xi, yi] = reduce_f(z_values)
                else:
                    context_['bin_values'][xi, yi] = np.nan

        data = np.ma.masked_invalid(context_['bin_values'].T)

        scale_model = context_['layer_model'].root_node().find_node(
            models.RootScale, properties_['color'].get())

        norm = None
        cmap = None
        vmin = None
        vmax = None

        if data is not None and scale_model is None:
            # scale_model is None, perhaps this is a predefined color map?
            color_scale_name = properties_['color'].get()
            if color_scale_name in mpl_backend.COLOR_SCALES:
                mpl_cmap_name = mpl_backend.COLOR_SCALES[color_scale_name]
                try:
                    cmap = matplotlib.cm.get_cmap(mpl_cmap_name)
                except ValueError:
                    syexceptions.sywarn("Unknown color scale {}".format(
                        color_scale_name))
                vmin = np.nanmin(data)
                vmax = np.nanmax(data)
        elif data is not None and scale_model is not None:
            # Normalization options
            use_extent = scale_model.find_child_property('extent').get()
            scale_domain = scale_model.find_child_property('domain').get()
            if use_extent:
                vmin = np.nanmin(data)
                vmax = np.nanmax(data)
            else:
                vmin = scale_domain[0]
                vmax = scale_domain[-1]

            # Create colormap normalization
            scale_type = scale_model.find_child_property('type').get()
            if scale_type == 'log':
                norm = matplotlib.colors.LogNorm(vmin=vmin, vmax=vmax)
            elif scale_type == 'linear':
                norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
            else:
                syexceptions.sywarn(
                    "Unknown scale type '{}'. Falling "
                    "back to linear scale.".format(scale_type))
                norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)

            # Create colormap
            if use_extent:
                scale_range = scale_model.find_child_property('range').get()
                scale_norm = matplotlib.colors.Normalize(
                    vmin=scale_domain[0], vmax=scale_domain[-1])
                normalized_domain = scale_norm(scale_domain)
                cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
                    'hist2d', list(zip(normalized_domain, scale_range)))
            else:
                scale_range = scale_model.find_child_property('range').get()
                normalized_domain = norm(scale_domain)
                cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
                    'hist2d', list(zip(normalized_domain, scale_range)))

        pcol_kwargs = dict(
            cmap=cmap,
            norm=norm,
            vmin=vmin,
            vmax=vmax,
            alpha=properties_['alpha'].get())

        # Choose pcolor implementation depending on settings:
        #   pcolorfast: The fastest alternative, but it can't handle polar
        #               coordinates, log axes, or bin edgecolors.
        #   pcolormesh: Also quite fast, can handle most situations
        draw_edges = properties_['draw_edges'].get()
        if parameters['axes'].name == 'rectilinear' and not draw_edges:
            pcol = parameters['axes'].pcolorfast
        else:
            pcol = parameters['axes'].pcolormesh

        # Enable drawing bin edges if selected
        if draw_edges:
            pcol_kwargs['edgecolor'] = properties_['edgecolor'].get()
            pcol_kwargs['linewidth'] = 0.5
            pcol_kwargs['antialiased'] = True

        context_['artist']['pcol'] = pcol(context_['x_bin_edges'],
                                          context_['y_bin_edges'],
                                          data,
                                          **pcol_kwargs)

        # Try to enable smoothing if selected
        smoothing = properties_['smoothing'].get()
        if smoothing != 'nearest':
            try:
                context_['artist']['pcol'].set_interpolation(smoothing)
            except AttributeError:
                syexceptions.sywarn(
                    "No smoothing available. Smoothing is not available e.g. "
                    "when using polar coordinates or drawing bin edges.")

        # Draw numbers if selected
        if properties_['draw-numbers'].get():
            x_edges = context_['x_bin_edges']
            y_edges = context_['y_bin_edges']
            xpos = x_edges[:-1] + np.diff(x_edges) / 2.
            ypos = y_edges[:-1] + np.diff(y_edges) / 2.
            text_artists = []

            for (ix, x), (iy, y) in itertools.product(enumerate(xpos),
                                                      enumerate(ypos)):
                # Find a good text color for this bin, choosing white if the
                # bin color is dark and black if the bin color is bright.
                bin_value = context_['bin_values'][ix, iy]
                if np.isfinite(bin_value):
                    if cmap is None:
                        cmap = context_['artist']['pcol'].cmap
                    if norm is None:
                        norm = context_['artist']['pcol'].norm
                    bg_color_tuple = cmap(norm(bin_value))
                    bg_brightness = sum(bg_color_tuple[:3]) / 3.0
                    if bg_brightness > 0.5:
                        text_color = '#000000'
                    else:
                        text_color = '#FFFFFF'

                    text_artists.append(parameters['axes'].text(
                        x, y, str(int(bin_value)),
                        horizontalalignment='center',
                        verticalalignment='center',
                        color=text_color))
            context_['artist']['texts'] = text_artists

        # Create colorbar if selected
        if properties_['colorbar'].get():
            context_['artist']['colorbar'] = (
                parameters['axes'].figure.colorbar(
                    context_['artist']['pcol'], ax=parameters['axes']))

        context_['canvas'].draw_idle()

    properties = parameters['layer_model'].properties_as_dict()

    for p, v in six.iteritems(properties):
        if p in ('x-bin-count', 'y-bin-count',  # Need recalculating bin values
                 'z-source', 'reduce-func',  # Need recalculating bin values
                 'alpha', 'color', 'edgecolor', 'draw_edges',  # Need redoing pcolor?
                 'smoothing', 'colorbar', 'draw-numbers'):  # Perhaps only need setting options on some artist?
            mpl_backend.wrap_and_bind(
                binding_context,
                parameters['canvas'],
                source_property=v,
                target_getter=v.get,
                target_setter=functools.partial(update_data, context))

    _, (x_data_source_property, y_data_source_property) = \
        context['layer_model'].extract_data_and_properties()

    # This is used to force update of axis range.
    x_data_source_property.editor.tags.add(
        editor_type.EditorTags.force_rebuild_after_edit)
    y_data_source_property.editor.tags.add(
        editor_type.EditorTags.force_rebuild_after_edit)

    mpl_backend.wrap_and_bind(
        binding_context,
        parameters['canvas'],
        source_property=x_data_source_property,
        target_getter=x_data_source_property.get,
        target_setter=functools.partial(update_data, context))

    mpl_backend.wrap_and_bind(
        binding_context,
        parameters['canvas'],
        source_property=y_data_source_property,
        target_getter=y_data_source_property.get,
        target_setter=functools.partial(update_data, context))
