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

from sylib.report import icons
from sylib.report import layers


class Layer(layers.Layer):
    """Heatmap layer."""

    meta = {
        'icon': icons.SvgIcon.histogram2d,
        'label': 'Heatmap',
        'default-data': {
            'type': 'histogram2d',
            'data': [
                {
                    'source': '',
                    'axis': ''
                },
                {
                    'source': '',
                    'axis': ''
                }
            ]
        }
    }
    property_definitions = collections.OrderedDict((
        ('name', {'type': 'string',
                  'label': 'Name',
                  'icon': icons.SvgIcon.blank,
                  'default': 'Heatmap Plot'}),

        ('x-bin-count', {'type': 'integer',
                         'label': 'X Bin Count',
                         'icon': icons.SvgIcon.blank,
                         'range': {'min': 1, 'max': 100000, 'step': 1},
                         'default': 10}),

        ('y-bin-count', {'type': 'integer',
                         'label': 'Y Bin Count',
                         'icon': icons.SvgIcon.blank,
                         'range': {'min': 1, 'max': 100000, 'step': 1},
                         'default': 10}),

        ('reduce-func', {'type': 'list',
                         'label': 'Reduction function',
                         'icon': icons.SvgIcon.blank,
                         'options': ['count', 'median', 'mean', 'min', 'max'],
                         'default': 'count'}),

        ('z-source', {'type': 'datasource',
                      'label': 'Bin values',
                      'icon': icons.SvgIcon.blank,
                      'default': ''}),

        ('color', {'type': 'colorscale',
                   'label': 'Color Scale',
                   'icon': icons.SvgIcon.blank,
                   'default': 'pink'}),

        ('colorbar', {'type': 'boolean',
                      'label': 'Colorbar',
                      'icon': icons.SvgIcon.blank,
                      'default': True}),

        ('draw-numbers', {'type': 'boolean',
                          'label': 'Draw numbers',
                          'icon': icons.SvgIcon.blank,
                          'default': False}),

        ('draw_edges', {'type': 'boolean',
                        'label': 'Draw edges',
                        'icon': icons.SvgIcon.blank,
                        'default': False}),

        ('edgecolor', {'type': 'color',
                       'label': 'Edge color',
                       'icon': icons.SvgIcon.blank,
                       'default': '#000000'}),

        ('smoothing', {'type': 'list',
                       'label': 'Smoothing',
                       'icon': icons.SvgIcon.blank,
                       'options': ['nearest', 'bilinear', 'bicubic'],
                       'default': 'nearest'}),

        ('alpha', {'type': 'float',
                   'label': 'Alpha',
                   'range': {'min': 0.0, 'max': 1.0, 'step': 0.1},
                   'icon': icons.SvgIcon.blank,
                   'default': 1.0})
    ))
