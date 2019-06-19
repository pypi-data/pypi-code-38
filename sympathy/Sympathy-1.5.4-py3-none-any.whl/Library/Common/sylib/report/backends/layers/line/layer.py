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

from sylib.report import layers
from sylib.report import icons


class Layer(layers.Layer):
    """Line layer."""

    meta = {
        'icon': icons.SvgIcon.line,
        'label': 'Line Plot',
        'default-data': {
            'type': 'line',
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
                  'default': 'Line Plot'}),

        ('line-style', {'type': 'list',
                        'label': 'Line Style',
                        'icon': icons.SvgIcon.blank,
                        'options': ['-', '--', '-.', ':'],
                        'default': '-'}),

        ('line-width', {'type': 'float',
                        'label': 'Line Width',
                        'icon': icons.SvgIcon.blank,
                        'range': {'min': 0.1, 'max': 30.0, 'step': 0.25},
                        'default': 1.0}),

        ('restart', {'type': 'boolean',
                     'label': 'Lift pen when x decreases',
                     'icon': icons.SvgIcon.blank,
                     'default': False}),

        ('line-color', {'type': 'color',
                        'label': 'Line Color',
                        'icon': icons.SvgIcon.blank,
                        'default': '#000000'}),

        ('alpha', {'type': 'float',
                   'label': 'Alpha',
                   'range': {'min': 0, 'max': 1, 'step': 0.1},
                   'icon': icons.SvgIcon.blank,
                   'default': 1.0})
    ))
