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
"""Renderer of histogram plots for MPL."""
import functools
import six
import numpy as np

from sylib.report import editor_type
from sylib.report import plugins
from sylib.report import models
mpl_backend = plugins.get_backend('mpl')


def get_x_axis_range(layer_model, data):
    axis_id = layer_model.children[0].children[0].data['axis']
    axis_model = layer_model.parent.parent.children[0].find_node(
        models.GraphAxis, axis_id)
    if axis_model.data['extent']:
        axis_min = np.amin(data)
        axis_max = np.amax(data)
    else:
        axis_min = axis_model.data['min']
        axis_max = axis_model.data['max']
    return axis_min, axis_max


def get_x_axis_width(layer_model, data):
    axis_min, axis_max = get_x_axis_range(layer_model, data)
    return axis_max - axis_min


def create_layer(binding_context, parameters):
    """
    Build layer for MPL and bind properties using binding context.
    :param binding_context: Binding context.
    :param parameters: Dictionary containing:
                       'layer_model': a models.GraphLayer instance,
                       'axes': the MPL-axes to add layer to,
                       'canvas': canvas (Qt-widget) that we are rendering to,
                       'z_order': Z-order of layer.
    :return: MPL-element which can be added to Axes.
    """
    # This is our context to be shared by setters of bindings.
    context = {
        'binding_context': binding_context,
        'patches': [],
        'bin_values': [],
        'bin_edges': [],
        'layer_model': parameters['layer_model'],
        'axes': parameters['axes'],
        'canvas': parameters['canvas'],
        'z_order': parameters['z_order'],
        'properties': []
    }

    # Update histogram by removing old patches and adding new by redrawing
    # everything.
    def update_bin_count(context_, bin_count_):
        # Remove old patches.
        for patch in context_['patches']:
            patch.remove()

        (data_,), _ = context_['layer_model'].extract_data_and_properties()
        if len(data_) == 0:
            return
        x_range = get_x_axis_range(context_['layer_model'], data_)
        (context_['bin_values'], context_['bin_edges'],
         context_['patches']) = \
            context_['axes'].hist(data_, bins=bin_count_, range=x_range,
                                  zorder=context['z_order'])

        # Matplotlib disables pixel snapping for first patch in histograms as a
        # workaround for some other bug. See the matplotlib issue for details:
        # https://github.com/matplotlib/matplotlib/issues/4212
        if len(context_['patches']):
            context_['patches'][0].set_snap(True)

        # Apply all properties to the new patches.
        for p_ in context_['properties']:
            context_['binding_context'].notify(p_)

        context_['canvas'].draw_idle()

    def update_data(context_, bin_count_property, _):
        bin_count = bin_count_property.get()
        update_bin_count(context_, bin_count)

    def get_bar_width(context_, obj):
        w = obj.get_width()
        (data_,), _ = context_['layer_model'].extract_data_and_properties()
        x_width = get_x_axis_width(context_['layer_model'], data_)
        properties_ = context_['layer_model'].properties_as_dict()
        bin_count = properties_['bin-count'].get()
        return w / x_width * bin_count

    def set_bar_width(context_, obj, v):
        (data_,), _ = context_['layer_model'].extract_data_and_properties()
        x_width = get_x_axis_width(context_['layer_model'], data_)
        properties_ = context_['layer_model'].properties_as_dict()
        bin_count = properties_['bin-count'].get()
        w = v * x_width / bin_count
        obj.set_width(w)

    # Bind patch properties.
    properties = parameters['layer_model'].properties_as_dict()
    for p, v in six.iteritems(properties):
        if p == 'bin-count':
            mpl_backend.wrap_and_bind(
                binding_context,
                parameters['canvas'],
                source_property=v,
                target_getter=v.get,
                target_setter=functools.partial(update_bin_count, context))
        elif p == 'bar-width':
            context['properties'].append(v)
            mpl_backend.bind_artist_list(
                binding_context,
                {'property': v,
                 'artists': lambda: context['patches'],
                 'getter_func': lambda obj: functools.partial(
                     get_bar_width, context, obj),
                 'setter_func': lambda obj: functools.partial(
                     set_bar_width, context, obj),
                 'canvas': parameters['canvas'],
                 'kind': 'numeric'})
        elif p == 'face-color':
            context['properties'].append(v)
            mpl_backend.bind_artist_list(binding_context,
                                         {'property': v,
                                          'artists':
                                              lambda: context['patches'],
                                          'getter_func':
                                              lambda obj: obj.get_facecolor,
                                          'setter_func':
                                              lambda obj: obj.set_facecolor,
                                          'canvas': parameters['canvas'],
                                          'kind': 'color'})
        elif p == 'edge-color':
            context['properties'].append(v)
            mpl_backend.bind_artist_list(binding_context,
                                         {'property': v,
                                          'artists':
                                              lambda: context['patches'],
                                          'getter_func':
                                              lambda obj: obj.get_edgecolor,
                                          'setter_func':
                                              lambda obj: obj.set_edgecolor,
                                          'canvas': parameters['canvas'],
                                          'kind': 'color'})
        elif p == 'alpha':
            context['properties'].append(v)
            mpl_backend.bind_artist_list(binding_context,
                                         {'property': v,
                                          'artists':
                                              lambda: context['patches'],
                                          'getter_func':
                                              lambda obj: obj.get_alpha,
                                          'setter_func':
                                              lambda obj: obj.set_alpha,
                                          'canvas': parameters['canvas'],
                                          'kind': 'numeric'})

    # Bind values. This must be done after the previous if statement since
    # the value of "bin-count" must be set properly first.
    _, (data_source_property,) = \
        context['layer_model'].extract_data_and_properties()

    # This is used to force update of axis range.
    data_source_property.editor.tags.add(
        editor_type.EditorTags.force_rebuild_after_edit)

    mpl_backend.wrap_and_bind(
        binding_context,
        parameters['canvas'],
        source_property=data_source_property,
        target_getter=data_source_property.get,
        target_setter=functools.partial(update_data, context,
                                        properties['bin-count']))
