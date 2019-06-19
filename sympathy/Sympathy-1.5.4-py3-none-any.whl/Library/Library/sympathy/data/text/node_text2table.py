# coding=utf-8
# Copyright (c) 2013, 2017, Combine Control Systems AB
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
"""
Convert Text(s) into Table(s). The rows of the incoming Text will be rows in
the resulting output Table.
"""
import numpy as np
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust

NAME = 'Text'


class Text2Table(synode.Node):
    parameters = synode.parameters()
    parameters.set_string(
        'name',
        label='Output name',
        value=NAME,
        description='Specify name for output column. Must be a legal name.')

    name = 'Text to Table'
    description = 'Convert Text of Table.'
    inputs = Ports([Port.Text('Input Text', name='text')])
    outputs = Ports([Port.Table('Table with input Text', name='table')])

    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C) 2013 Combine Control Systems AB'
    nodeid = 'org.sysess.sympathy.data.text.text2table'
    version = '0.1'
    icon = 'text2table.svg'
    tags = Tags(Tag.DataProcessing.Convert)

    def execute(self, node_context):
        name = node_context.parameters['name'].value
        table = node_context.output[0]
        text = node_context.input[0]
        table.set_column_from_array(
            name,
            np.array(text.get().splitlines()))


Texts2Tables = node_helper.list_node_factory(
    Text2Table,
    {'text': {'name': 'texts'}},
    {'table': {'name': 'tables'}},
    name='Texts to Tables',
    nodeid='org.sysess.sympathy.data.text.texts2tables')


class Table2Text(synode.Node):
    name = 'Table to Text'
    description = 'Convert Table to Text'
    author = 'Magnus Sandén <magnus.sanden@combine.se>'
    copyright = '(C) 2017 Combine Control Systems AB'
    nodeid = 'org.sysess.sympathy.data.text.table2text'
    version = '0.1'
    icon = 'table2text.svg'
    tags = Tags(Tag.DataProcessing.Convert)

    parameters = synode.parameters()
    parameters.set_string(
        'name', label='Column name',
        description='Specify name for input column.',
        editor=synode.editors.combo_editor(options=[], edit=True))

    inputs = Ports([Port.Table('Table with input Text', name='table')])
    outputs = Ports([Port.Text('Output Text', name='text')])

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['name'], node_context.input[0])

    def execute(self, node_context):
        name = node_context.parameters['name'].value
        table = node_context.input[0]
        text = node_context.output[0]
        text.set("".join(table.get_column_to_array(name)))
