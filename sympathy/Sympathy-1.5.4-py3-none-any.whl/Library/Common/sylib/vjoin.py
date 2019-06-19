# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
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
from sympathy.api import node as synode


NAN = 'Complement with nan or empty string'
MASK = 'Mask missing values'


def set_fill_strategy_param(params, value):
    params.set_list(
        'fill_strategy', value=[value], plist=[NAN, MASK],
        label='Complement strategy',
        description=('When "{}" is selected missing columns will be replaced '
                     'by columns of nan or empty strings. '
                     'When "{}" is selected missing columns will be result in '
                     'masked values'.format(NAN, MASK)),
        editor=synode.Util.combo_editor())


def base_params():
    parameters = synode.parameters()
    parameters.set_boolean(
        'fill', value=True, label='Complement missing columns',
        description='Select if columns that are not represented in all '
                    'Tables should be complemented')
    set_fill_strategy_param(parameters, 1)
    parameters.set_string(
        'output_index',
        label='Output index',
        value='',
        description=('Specify name for output index column. '
                     'If left empty, no index column will be created'),
        editor=synode.Util.lineedit_editor('(none)'))
    parameters.set_integer(
        'minimum_increment',
        value=1,
        label='Increment for empty tables',
        description=('Specify the increment in the outgoing index column '
                     'for tables with no rows. Either 1 or 0.'),
        editor=synode.Util.bounded_spinbox_editor(0, 1, 1))

    return parameters


def base_controller():
    controller = (
        synode.controller(
            when=synode.field('fill', 'checked'),
            action=synode.field('fill_strategy', 'enabled')),
        synode.controller(
            when=synode.field('output_index', 'value', ''),
            action=synode.field('minimum_increment', 'disabled')))
    return controller


def base_values(parameters):
    input_index = ''
    try:
        output_index = parameters['output_index'].value
    except Exception:
        output_index = ''
    try:
        minimum_increment = parameters['minimum_increment'].value
    except Exception:
        minimum_increment = 0

    try:
        fill = parameters['fill'].value
    except Exception:
        fill = False

    if fill:
        try:
            if parameters['fill_strategy'].selected == MASK:
                fill = None
        except Exception:
            pass
    return (input_index, output_index, minimum_increment, fill)
