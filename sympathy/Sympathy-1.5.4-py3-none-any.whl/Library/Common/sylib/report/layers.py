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

import collections

from . import editor_type
from . import scales


type_to_editor = {
    'boolean': editor_type.Boolean,
    'list': editor_type.ImmutableList,
    'float': editor_type.Float,
    'integer': editor_type.Integer,
    'color': editor_type.Color,
    'colorscale': editor_type.ColorScale,
    'string': editor_type.String,
    'datasource': editor_type.DataSource,
    'image': editor_type.Image
}


class Layer(object):
    """
    A layer contains a dictionary with definitions of all available properties.
    If a property is missing in one layer it must be added to the data
    structure containing its default value.
    """

    property_definitions = None
    properties = None

    @classmethod
    def create_properties(cls, layer_model, property_class):
        """
        Create layer properties.
        :param layer_model: models.GraphLayer object.
        :param property_class: Usually models.Property.
        """
        properties = collections.OrderedDict()

        # Handle specified and unspecified properties.
        for k, v in list(cls.property_definitions.items()):
            # If we have already added the property, skip it.
            if k in properties:
                continue
            # Add missing parameter into model containing default value.
            if 'options' in v:
                def create_options_getter(x):
                    return lambda: x['options']
                options_getter = create_options_getter(v)
            else:
                options_getter = lambda: None
            editor = type_to_editor[v['type']](options_getter)
            editor.value_range = v.get('range', None)
            is_bindable = v.get('scale_bindable', False)
            parameters = {
                'property': k,
                'label': v['label'],  # Label of property.
                'icon': v['icon'],    # Icon of property.
                'editor': editor,
                'data': layer_model.data,
                'scale_bindable': is_bindable
            }
            # Side-effects...
            # Add specified property to data dict.
            if k in layer_model.data:
                if (is_bindable and
                   isinstance(layer_model.data[k], collections.Mapping) and
                   'binding' in layer_model.data[k]):
                    if layer_model.data[k]['binding'] is not None:
                        parameters['scale_binding'] = scales.ScaleBinding(
                            layer_model.data[k]['binding']['data'],
                            layer_model.data[k]['binding']['scale'])
                elif (not is_bindable and
                      isinstance(layer_model.data[k], collections.Mapping) and
                      'binding' in layer_model.data[k]):
                    # Correct structure if binding is not allowed but
                    # data provides it anyway.
                    layer_model.data[k] = layer_model.data[k]['value']
            # Add default property to data dict.
            else:
                if is_bindable:
                    layer_model.data[k] = {
                        'value': v['default'],
                        'binding': None
                    }
                else:
                    layer_model.data[k] = v['default']
            properties[k] = property_class(parameters, parent=layer_model)
            # Make sure that proper updates happen when a layer is renamed.
            if k == 'name':
                properties[k].editor.tags.add(
                    editor_type.EditorTags.force_update_after_edit)

        return properties
