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

from sylib.report import editor_type
from sylib.report import plugins
mpl_backend = plugins.get_backend('mpl')


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
        'lines': [],
        'layer_model': parameters['layer_model'],
        'axes': parameters['axes'],
        'canvas': parameters['canvas'],
        'z_order': parameters['z_order'],
        'properties': []
    }

    def update_data(context_, _):
        # Remove old lines.
        for line in context_['lines']:
            line.remove()
        context_['lines'] = []

        (data_,), _ = context_['layer_model'].extract_data_and_properties()
        if len(data_) == 0:
            return
        properties_ = parameters['layer_model'].properties_as_dict()
        for x in data_:
            context_['lines'].append(context_['axes'].axvline(
                x, zorder=context_['z_order'],
                color=properties_['color'].get(),
                linewidth=properties_['line-width'].get(),
                alpha=properties_['alpha'].get()))

        context_['canvas'].draw_idle()

    # Bind values.
    _, (data_source_property,) = \
        context['layer_model'].extract_data_and_properties()

    # This is used to force update of axis range.
    data_source_property.editor.tags.add(
        editor_type.EditorTags.force_rebuild_after_edit)

    # Bind line properties.
    properties = parameters['layer_model'].properties_as_dict()

    for property_name in ('color', 'line-width', 'alpha'):
        mpl_backend.wrap_and_bind(binding_context,
                                  parameters['canvas'],
                                  properties[property_name],
                                  properties[property_name].get,
                                  functools.partial(update_data, context))
