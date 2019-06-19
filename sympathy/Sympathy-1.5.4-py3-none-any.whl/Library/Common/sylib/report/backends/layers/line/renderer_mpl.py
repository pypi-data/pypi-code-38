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
import numpy as np

from sylib.report import editor_type
from sylib.report import plugins
mpl_backend = plugins.get_backend('mpl')


def create_layer(binding_context, parameters):
    """
    Build layer for MPL and bind properties using binding context.

    Parameters
    ----------
    binding_context
        Binding context.
    parameters : dictionary
        Should contain:
            'layer_model': a models.GraphLayer instance,
            'axes': the MPL-axes to add layer to,
            'canvas': current canvas (QtWidget) we are rendering to,
            'z_order': Z-order of layer.

    Returns
    -------
    matplotlib.artist.Artist
        MPL-element which can be added to Axes.
    """
    # Find data for each axis.
    (x_data, y_data), data_source_properties = \
        parameters['layer_model'].extract_data_and_properties()

    properties = parameters['layer_model'].properties_as_dict()

    # Side-effect: Line2D-object added to axes.
    if len(x_data) == len(y_data) and len(x_data) > 0:
        if properties['restart'].get():
            line_objects = []
            decrease_mask = np.flatnonzero(np.diff(x_data) < 0)
            prev_i = 0
            for i in decrease_mask + 1:
                line_objects.extend(parameters['axes'].plot(
                    x_data[prev_i:i], y_data[prev_i:i],
                    zorder=parameters['z_order']))
                prev_i = i
            line_objects.extend(parameters['axes'].plot(
                x_data[prev_i:], y_data[prev_i:],
                zorder=parameters['z_order']))
        else:
            line_objects = parameters['axes'].plot(
                x_data, y_data, zorder=parameters['z_order'])
    else:
        line_objects = parameters['axes'].plot(
            0, 0, zorder=parameters['z_order'])

    _, data_source_properties = \
        parameters['layer_model'].extract_data_and_properties()

    # This is used to force update of axis range.
    data_source_properties[0].editor.tags.add(
        editor_type.EditorTags.force_rebuild_after_edit)
    data_source_properties[1].editor.tags.add(
        editor_type.EditorTags.force_rebuild_after_edit)
    properties['restart'].editor.tags.add(
        editor_type.EditorTags.force_rebuild_after_edit)

    # Bind stuff.
    for line_object in line_objects:
        mpl_backend.bind_artist(binding_context,
                                {'property': properties['line-style'],
                                 'getter': line_object.get_linestyle,
                                 'setter': line_object.set_linestyle,
                                 'canvas': parameters['canvas'],
                                 'kind': 'string'})

        mpl_backend.bind_artist(binding_context,
                                {'property': properties['line-width'],
                                 'getter': line_object.get_linewidth,
                                 'setter': line_object.set_linewidth,
                                 'canvas': parameters['canvas'],
                                 'kind': 'numeric'})

        mpl_backend.bind_artist(binding_context,
                                {'property': properties['line-color'],
                                 'getter': line_object.get_color,
                                 'setter': line_object.set_color,
                                 'canvas': parameters['canvas'],
                                 'kind': 'color'})

        mpl_backend.bind_artist(binding_context,
                                {'property': properties['alpha'],
                                 'getter': line_object.get_alpha,
                                 'setter': line_object.set_alpha,
                                 'canvas': parameters['canvas'],
                                 'kind': 'numeric'})
