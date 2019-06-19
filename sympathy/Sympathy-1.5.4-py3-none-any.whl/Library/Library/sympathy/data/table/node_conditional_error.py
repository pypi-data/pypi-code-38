# -*- coding: utf-8 -*-
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

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import SyNodeError, sywarn
from sylib import util


ERROR_LEVEL = ['Error', 'Warning', 'Output']


class ConditionalError(synode.Node):
    """
    Raise an error if the supplied predicate function returns True.

    See https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions
    for a description of lambda functions. Have a look at the :ref:`Data type
    APIs<datatypeapis>` to see what methods and attributes are available on the
    data type that you are working with.
    """

    name = 'Conditional error/warning'
    author = u'Magnus Sandén <magnus.sanden@combine.se>'
    copyright = 'Copyright (c) 2016 Combine Control Systems AB'
    version = '1.0'
    icon = ''
    description = "Raise an error if a predicate is True."
    nodeid = 'org.sysess.sympathy.data.table.conditionalerror'
    icon = 'error.svg'
    tags = Tags(Tag.Development.Test)

    inputs = Ports([Port.Custom('<a>', 'Input', name='in')])
    outputs = Ports([Port.Custom('<a>', 'Output', name='out')])

    parameters = synode.parameters()
    parameters.set_string(
        'predicate',
        label='Predicate function:',
        value='lambda arg: True  # Identity filter',
        description='Error message is printed if this function returns True.',
        editor=synode.Util.code_editor())
    parameters.set_string(
        'error_msg',
        label='Error message:',
        value='Error!',
        description='Error message to display to the user.')
    parameters.set_list(
        'error_type',
        label='Severity:',
        list=ERROR_LEVEL,
        value=[0],
        description='The level "Error" stops flow execution.',
        editor=synode.Util.combo_editor())

    def execute(self, node_context):
        predicate_str = node_context.parameters['predicate'].value
        error_type = node_context.parameters['error_type'].selected
        error_msg = node_context.parameters['error_msg'].value
        in_table = node_context.input['in']
        out_table = node_context.output['out']

        # Evaluate predicate function
        if util.base_eval(predicate_str)(in_table):
            if error_type == 'Error':
                raise SyNodeError(error_msg)
            elif error_type == 'Warning':
                sywarn(error_msg)
            elif error_type == 'Output':
                print(error_msg)
            else:
                raise ValueError('Unknown error_type')

        # Output is equal to input
        out_table.source(in_table)
