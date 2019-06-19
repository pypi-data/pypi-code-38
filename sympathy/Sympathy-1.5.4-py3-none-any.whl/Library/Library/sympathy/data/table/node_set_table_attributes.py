# coding=utf8
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
Nodes for setting and getting a Table (or a list of Tables) names.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import numpy as np
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api import table
from sympathy.api.exceptions import SyDataError


class SetNameSuper(synode.Node):
    author = 'Greger Cronquist <greger.cronquist@combine.se>'
    copyright = '(c) 2013 Sysem Engineering Society'
    version = '1.0'
    icon = 'rename_table.svg'
    tags = Tags(Tag.DataProcessing.TransformMeta)

    parameters = synode.parameters()
    parameters.set_string(
        'name', label='Name',
        description='Name to assign to the table(s).')


class SetTableName(SetNameSuper):
    """Set the name of a Table."""

    name = 'Set Table Name'
    description = 'Set the name of a Table'
    nodeid = 'org.sysess.sympathy.data.table.settablename'

    inputs = Ports([Port.Table('Input Table')])
    outputs = Ports([Port.Table(
        'Table with the name attribute changed according to node '
        'configuration')])

    def execute(self, node_context):
        node_context.output[0].update(node_context.input[0])
        node_context.output[0].set_name(node_context.parameters['name'].value)
        node_context.output[0].set_table_attributes(
            node_context.input[0].get_table_attributes())


SetTablesName = node_helper.list_node_factory(
    SetTableName,
    [0], [0],
    name='Set Tables Name',
    nodeid='org.sysess.sympathy.data.table.settablesname')


class SetTablesNameTable(synode.Node):
    """Set name of a list of tables using another table with names."""

    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(c) 2013 Sysem Engineering Society'
    version = '1.0'
    icon = 'rename_table.svg'
    name = 'Set Tables Name with Table'
    description = 'Set the name of a list of Tables'
    nodeid = 'org.sysess.sympathy.data.table.settablesnametable'
    tags = Tags(Tag.DataProcessing.TransformMeta)

    parameters = synode.parameters()
    editor = synode.Util.selectionlist_editor('single', filter=True, edit=True)
    parameters.set_list(
        'names', label='Select name column',
        description='Select the columns with Table names',
        value=[0], editor=editor)

    inputs = Ports([
        Port.Tables('Input Tables', name='input'),
        Port.Table('A Table containing a column with names', name='names')])
    outputs = Ports([Port.Tables(
        'The list of Tables with the name attribute changed according to node '
        'configuration. All Tables will get the same name.', name='output')])

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['names'],
               node_context.input[1])

    def validate_data(self, node_context):
        try:
            column_names = node_context.input[1].column_names()
        except ValueError:
            column_names = []
        return node_context.parameters['names'].selected in column_names

    def execute(self, node_context):
        if not len(node_context.input[0]):
            return

        names_column = node_context.parameters['names'].selected
        if not self.validate_data(node_context):
            raise SyDataError('Selected column name needs to exist.')

        if node_context.input[1].is_empty():
            return
        names = node_context.input[1].get_column_to_array(names_column)
        output_list = node_context.output[0]
        for input_table, new_name in zip(node_context.input[0], names):
            output = table.File()
            output.update(input_table)
            output.set_name(new_name)
            output.set_table_attributes(
                input_table.get_table_attributes())
            output_list.append(output)


class GetTableNameSuper(synode.Node):
    author = 'Andreas Tågerud<andreas.tagerud@combine.se>'
    copyright = '(c) 2017 Combine Control Systems AB'
    version = '1.0'
    icon = 'rename_table.svg'
    tags = Tags(Tag.DataProcessing.TransformMeta)


class GetTableName(GetTableNameSuper):
    """Get the name of a Table."""

    name = 'Get Table Name'
    description = 'Get name of a Table'
    nodeid = 'org.sysess.sympathy.data.table.gettablesnamestable'

    inputs = Ports([Port.Table('Input Table', name='port1')])
    outputs = Ports([Port.Table('Table name', name='port1')])

    def execute(self, node_context):
        node_context.output['port1'].set_column_from_array(
            'Table names', np.array([node_context.input['port1'].get_name()]))


class GetTablesNames(GetTableNameSuper):
    """Get the names of a list of Tables."""

    name = 'Get Tables Name'
    description = 'Get names of a list of Tables'
    nodeid = 'org.sysess.sympathy.data.table.gettablesnamestables'

    inputs = Ports([Port.Tables('Input Tables', name='port1')])
    outputs = Ports([Port.Table('All table names', name='port1')])

    def execute(self, node_context):
        names = [table.get_name() if table.get_name() is not None else ''
                 for table in node_context.input['port1']]
        node_context.output['port1'].set_column_from_array(
            'Table names', np.array(names))
