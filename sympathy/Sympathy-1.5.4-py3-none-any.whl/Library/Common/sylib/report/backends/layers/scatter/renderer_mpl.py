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
"""Renderer of scatter plots for MPL."""
import functools
import six
from sylib.report import plugins
from sylib.report import editor_type
mpl_backend = plugins.get_backend('mpl')


# Mapping between symbol name to symbol used in MPL.
SYMBOL_NAME_TO_SYMBOL = {
    'point': '.',
    'circle': 'o',
    'square': 's'
}
SYMBOL_TO_MARKER_NAME = {v: k for k, v in six.iteritems(SYMBOL_NAME_TO_SYMBOL)}


def create_layer(binding_context, parameters):
    """Build layer for MPL and bind properties using binding context.
    :param binding_context: Binding context.
    :param parameters: Dictionary containing:
                       'layer_model': a models.GraphLayer instance
                       'axes': the MPL-axes to add layer to
                       'canvas': current canvas (Qt-widget) we are rendering to
                       'z_order': Z-order of layer.
    """
    context = {
        'binding_context': binding_context,
        'path_collection': None,
        'layer_model': parameters['layer_model'],
        'axes': parameters['axes'],
        'canvas': parameters['canvas'],
        'z_order': parameters['z_order'],
        'properties': [],
        'drawing': False
    }

    def update_data(context_, _):
        properties_ = context_['layer_model'].properties_as_dict()
        # Remove old path collection first.
        if context_['path_collection'] is not None:
            context_['path_collection'].remove()
            context_['path_collection'] = None

        (x_data_, y_data_), _ = \
            context_['layer_model'].extract_data_and_properties()
        if len(x_data_) != len(y_data_) or len(x_data_) == 0:
            return

        scale = functools.partial(mpl_backend.calculate_scaled_value,
                                  context_['layer_model'])
        size = scale(properties_['size'])
        face_color = scale(properties_['face-color'])
        edge_color = scale(properties_['edge-color'])
        alpha = scale(properties_['alpha'])
        marker = properties_['symbol'].get()

        context_['path_collection'] = context_['axes'].scatter(
            x_data_, y_data_, s=size, c=face_color, alpha=alpha,
            marker=SYMBOL_NAME_TO_SYMBOL.get(marker, 'o'),
            edgecolors=edge_color,
            zorder=context_['z_order'])

        context_['canvas'].draw_idle()

    (x_data, y_data), data_source_properties = context[
        'layer_model'].extract_data_and_properties()

    if len(x_data) == len(y_data) and len(x_data) > 0:
        update_data(context, None)

    if data_source_properties is not None:
        mpl_backend.wrap_and_bind(binding_context,
                                  parameters['canvas'],
                                  data_source_properties[0],
                                  data_source_properties[0].get,
                                  functools.partial(update_data, context))
        mpl_backend.wrap_and_bind(binding_context,
                                  parameters['canvas'],
                                  data_source_properties[1],
                                  data_source_properties[1].get,
                                  functools.partial(update_data, context))
        # This is used to force update of axis range.
        data_source_properties[0].editor.tags.add(
            editor_type.EditorTags.force_rebuild_after_edit)
        data_source_properties[1].editor.tags.add(
            editor_type.EditorTags.force_rebuild_after_edit)

    # Bind stuff.
    properties = parameters['layer_model'].properties_as_dict()

    for property_name in ('symbol', 'size', 'face-color', 'edge-color',
                          'alpha'):
        mpl_backend.wrap_and_bind(binding_context,
                                  parameters['canvas'],
                                  properties[property_name],
                                  properties[property_name].get,
                                  functools.partial(update_data, context))
