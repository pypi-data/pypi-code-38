# -*- coding: utf-8 -*-
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
There are many situations where you may want to throw away some of the columns
of a table. Perhaps the amount of data is large and you want to trim it to
increase performance, or perhaps some column was just needed as an intermediary
step in some analysis.

If you want to remove columns from a Table the standard libray has two nodes
(plus two list variants) for doing that. The node :ref:`Select columns in
Table` will let you select what columns to keep in a gui, while the node
:ref:`Select columns in Table with Table` instead takes a second input table
with a filter column containing the names of all the columns that should be
kept (if *complement* is disabled) or all the columns that should be thrown
away (if *complement* is enabled).
"""
import re

from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import (Port, Ports, Tag, Tags,
                                     adjust)
from sympathy.api.exceptions import sywarn
from sympathy.utils import dtypes


class SelectColumnsTable(synode.Node):
    """
    Select columns to propagate.

    :Ref. nodes: :ref:`Select columns in Table with Table`
    """

    author = ('Alexander Busck <alexander.busck@combine.se>, '
              'Erik der Hagopian <erik.hagopian@combine.se>')
    copyright = '(c) 2013, 2017 Combine Control Systems AB'
    description = 'Select columns from input to propagate to output.'
    icon = 'select_table_columns.svg'
    name = 'Select columns in Table'
    nodeid = 'org.sysess.sympathy.data.table.selecttablecolumns'
    tags = Tags(Tag.DataProcessing.Select)
    version = '1.0'
    inputs = Ports([Port.Table('Input')])
    outputs = Ports([Port.Table('Output')])
    parameters = synode.parameters()
    editor = synode.Editors.multilist_editor(edit=True)

    parameters.set_list(
        'columns', label='Select columns', description='Select columns.',
        value=[], editor=editor)

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'], node_context.input[0])

    def update_parameters(self, old_params):
        cols = old_params['columns']
        if not cols.editor.get('mode', False):
            try:
                complement = old_params['complement'].value
                del old_params['complement']
            except KeyError:
                complement = False

            if complement:
                cols._multiselect_mode = 'unselected'
            else:
                cols._multiselect_mode = 'selected_exists'

    def execute(self, node_context):
        in_table = node_context.input[0]
        out_table = node_context.output[0]
        self.select_columns(
            in_table, out_table, node_context.parameters['columns'])

    @staticmethod
    def select_columns(input_table, output_table, parameter):
        output_table.set_name(input_table.get_name())
        output_table.set_table_attributes(input_table.get_table_attributes())

        for name in parameter.selected_names(input_table.column_names()):
            output_table.update_column(name, input_table, name)


SelectColumnsTables = node_helper.list_node_factory(
    SelectColumnsTable,
    [0], [0],
    name='Select columns in Tables',
    nodeid='org.sysess.sympathy.data.table.selecttablescolumns')


def select_columns(input_table, output_table, column_names, complement=False):
    if complement:
        input_column_names = input_table.column_names()
        for column in column_names:
            try:
                input_column_names.remove(column)
            except ValueError:
                pass
        for column in input_column_names:
            output_table.update_column(column, input_table, column)
    else:
        for column in input_table.column_names():
            if column in column_names:
                output_table.update_column(column, input_table, column)


class SelectTableColumnsFromTable(synode.Node):
    """
    :Ref. nodes: :ref:`Select columns in Table`
    """

    name = 'Select columns in Table with Table'
    description = ('Select columns in Table by using column '
                   'in selection Table.')

    icon = 'select_table_columns.svg'

    nodeid = 'org.sysess.sympathy.data.table.selecttablecolumnsfromtable'
    author = 'Greger Cronquist <greger.cronquist@combine.se>'
    copyright = '(c) 2013 Combine Control Systems AB'
    version = '1.0'
    tags = Tags(Tag.DataProcessing.Select)

    inputs = Ports([
        Port.Table('Selection', name='port1', requiresdata=True),
        Port.Table('Input Table', name='port2', requiresdata=True)])
    outputs = Ports([
        Port.Table('Table with columns in Selection removed', name='port1')])

    parameters = synode.parameters()
    parameters.set_boolean(
        'complement', value=False, label="Remove selected columns",
        description=(
            'When enabled, the selected columns will be removed. '
            'When disabled, the non-selected columns will be '
            'removed.'))
    parameters.set_list(
        'selection_column', label="Column with column names",
        description=('Select column in Selection Table '
                     'used for column name filtration.'),
        value=[0],
        editor=synode.Util.combo_editor(edit=True, filter=True))

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['selection_column'],
               node_context.input['port1'])

    def execute(self, node_context):
        """Execute"""
        selection_column_name = (
            node_context.parameters['selection_column'].selected)
        select_complement = node_context.parameters['complement'].value

        selection_table = node_context.input['port1']
        input_table = node_context.input['port2']
        output_table = node_context.output['port1']
        output_table.set_name(input_table.get_name())
        output_table.set_table_attributes(input_table.get_table_attributes())

        if input_table.is_empty():
            return

        if selection_column_name in selection_table.column_names():
            column_names = [column_name for column_name in
                            selection_table.get_column_to_array(
                                selection_column_name)]
        else:
            sywarn('The selected column does not seem to exist. '
                   'Assuming empty input.')
            column_names = []

        select_columns(input_table, output_table, column_names,
                       complement=select_complement)


SelectTableColumnsFromTables = node_helper.list_node_factory(
    SelectTableColumnsFromTable,
    ['port2'], ['port1'],
    name='Select columns in Tables with Table',
    nodeid='org.sysess.sympathy.data.table.selecttablecolumnsfromtables')


class SelectTableColumnsRegex(synode.Node):
    """Select all columns whose names match a regex."""

    author = "Magnus Sandén <magnus.sanden@combine.se>"
    copyright = "(c) 2016 Combine Control Systems AB"
    version = '1.0'

    name = 'Select columns in Table with Regex'
    description = "Select all columns whose names match a regex."
    nodeid = 'org.sysess.sympathy.data.table.selecttablecolumnsregex'
    icon = 'select_table_columns.svg'
    tags = Tags(Tag.DataProcessing.Select)

    inputs = Ports([Port.Table('Input Table', name='port1')])
    outputs = Ports([Port.Table(
        'Table with a subset of the incoming columns', name='port2')])

    parameters = synode.parameters()
    parameters.set_boolean(
        'complement', value=False,
        label="Remove matching columns",
        description=(
            'When enabled, matching columns will be removed. '
            'When disabled, non-matching columns will be removed.'))
    parameters.set_string(
        'regex', label='Regex:',
        description='Regex for matching column names.', value="")

    def execute(self, node_context):
        parameters = node_context.parameters
        regex = re.compile(parameters['regex'].value)
        complement = parameters['complement'].value
        input_table = node_context.input['port1']
        output_table = node_context.output['port2']
        output_table.set_name(input_table.get_name())
        output_table.set_table_attributes(input_table.get_table_attributes())
        for column in input_table.column_names():
            if bool(regex.match(column)) != complement:
                output_table.update_column(column, input_table, column)


class SelectColumnTypesSuper(synode.Node):
    """Select columns of specific type to propagate."""

    author = 'Andreas Tågerud <andreas.tagerud@combine.se>'
    copyright = '(c) 2017 Combine Control Systems AB'
    description = 'Select column types from input to propagate to output.'
    icon = 'select_table_columns.svg'
    tags = Tags(Tag.DataProcessing.Select)

    parameters = synode.parameters()
    editor = synode.Util.multilist_editor(mode=False, filter=False)

    parameters.set_list(
        'types', label='Select types', description='Select types',
        value=[], editor=editor)

    def adjust_parameters(self, node_context):
        node_context.parameters['types'].adjust(dtypes.typenames())

    def _execute(self, in_table, out_table, types):
        types = [dtypes.dtype(name).kind for name in types]
        out_table.set_name(in_table.get_name())
        out_table.set_table_attributes(in_table.get_table_attributes())

        for name in in_table.column_names():
            col_type = in_table.column_type(name).kind
            if col_type in types:
                out_table.update_column(name, in_table)

    def _get_types(self, node_context):
        return node_context.parameters['types'].selected_names(
            dtypes.typenames())


class SelectColumnTypesTable(SelectColumnTypesSuper):
    name = 'Select column by type in Table'
    nodeid = 'org.sysess.sympathy.data.table.selecttablecolumnstype'
    version = '1.0'
    inputs = Ports([Port.Table('Input')])
    outputs = Ports([Port.Table('Output')])

    def execute(self, node_context):
        in_table = node_context.input[0]
        out_table = node_context.output[0]
        self._execute(in_table, out_table, self._get_types(node_context))


SelectColumnTypesTables = node_helper.list_node_factory(
    SelectColumnTypesTable,
    [0], [0],
    name='Select column by type in Tables',
    nodeid='org.sysess.sympathy.data.table.selecttablescolumnstype')
