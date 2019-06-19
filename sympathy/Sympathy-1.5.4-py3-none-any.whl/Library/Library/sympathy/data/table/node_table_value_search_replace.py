# -*- coding:utf-8 -*-
# Copyright (c) 2013, 2017 Combine Control Systems AB
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
r"""
In the standard library there exist four nodes which perform a search and
replace of values among the elements in Tables. Of the four nodes, one
operates on single Table while the second operates on multiple Tables.
The third and fourth are the same but instead of a GUI configuration, they take
another table as configuration. See below.

In the configuration of the nodes one has to specify the columns in the Tables
which will be regarded during the execution of the node. The node works with
string, unicode, integer, and float values.

For string and unicode columns the search and replace expressions may be
regular expressions. Here, it is possible to use ()-grouping in the search
expression to reuse the match of the expression within the parentheses in the
replacement expression. In the regular expression for the replacement use
``\\1`` (or higher numbers) to insert matches.

As an example let's say that you have an input table with a column containing
the strings ``x``, ``y``, and ``z``. If you enter the search expression
``(.*)`` and the replacement expression ``\\1_new`` the output will be the
strings ``x_new``, ``y_new``, and ``z_new``.

For the expression table (for the 'with Table' versions) it should it have the
following structure:

+------------------------+------------------------------+
| Find column            | Replacement column           |
+========================+==============================+
| Expression to find 1   | Replacement for expression 1 |
+------------------------+------------------------------+
| Expression to find 2   | Replacement for expression 2 |
+------------------------+------------------------------+
| ...                    | ...                          |
+------------------------+------------------------------+

"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from sympathy.api import node as synode
from sympathy.api import table
import re
import math
import numpy as np
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import SyConfigurationError


CONFIG_ERROR_MSG = (
    'A search, replacement, or default value for column {} is not of the '
    'same type as the column data (or could not be converted).\n'
    'Valid types are: integer, float, text, and byte.\n'
    'Please review configuration.')


def _convert(value, type_, column):
    if type_.kind == 'b':
        raise SyConfigurationError(CONFIG_ERROR_MSG.format(column))
    try:
        return type_.type(value)
    except ValueError:
        raise SyConfigurationError(CONFIG_ERROR_MSG.format(column))


def replace_table_values(out_table, columns, params):
    def new_dtype(dtype):
        if dtype.kind in ['U', 'S']:
            return np.dtype(dtype.kind)
        return dtype

    def isnan(val):
        if isinstance(val, float):
            return math.isnan(val)
        return False

    find, replace, use_default, default, ignore, literal = params
    out_table_tmp = table.File()

    for col_name in columns:
        table_col = out_table.col(col_name)
        col_type = new_dtype(table_col.data.dtype)
        mask = None
        if isinstance(table_col.data, np.ma.MaskedArray):
            mask = table_col.data.mask
        find = find if literal else _convert(find, col_type, col_name)
        replace = replace if literal else _convert(replace, col_type, col_name)
        flag = 0 if not ignore else re.I

        if not use_default:
            col = out_table.get_column_to_series(col_name)
            if literal:
                if col_type.kind in ['U', 'S']:
                    col = col.str.replace(find, replace, flags=flag)
                    col = col.values
                else:
                    continue
            else:
                col.replace(find, replace, inplace=True)
                col = col.values
            col = np.array(col, dtype=col_type)
        else:
            default = _convert(default, col_type, col_name)
            if mask is not None:
                col = table_col.data.data
            else:
                col = table_col.data

            if literal:
                rexp = re.compile(find, flags=flag)
                if col_type.kind in ['U', 'S']:
                    col = [rexp.sub(replace, value)
                           if rexp.search(value)
                           else default
                           for value in col.tolist()]
                    col = np.array(col, dtype=col_type)
                else:
                    continue
            else:
                bindex = col == find
                col[bindex] = replace
                col[~bindex] = default

        col = np.array(col, dtype=col_type)

        if mask is not None:
            col = np.ma.MaskedArray(col, mask)

        out_table_tmp.set_column_from_array(col_name, col)

    out_table_tmp.set_attributes(out_table.get_attributes())
    out_table_tmp.set_name(out_table.get_name())
    out_table.update(out_table_tmp)
    return out_table


def _set_literal(params, value=True):
    params.set_boolean(
        'literal', label='Text replacement only (using regex)',
        description=(
            'Perform regex replacements in string columns, i.e., columns with '
            'types text and bytes, other columns are ignored. '
            'Disable this option to replace full values, without using '
            'regex across all types of columns.'),
        value=value)


def common_params(parameters):
    _set_literal(parameters)
    parameters.set_boolean(
        'ignore_case', label='Ignore case',
        description='Ignore case when searching', value=False)
    return parameters


class TableSearchBase(synode.Node):
    author = 'Greger Cronquist <greger.cronquist@combine.se>'
    copyright = '(c) 2013 Combine Control Systems AB'
    version = '1.0'
    icon = 'search_replace.svg'
    tags = Tags(Tag.DataProcessing.TransformData)

    parameters = synode.parameters()
    editor = synode.Editors.multilist_editor(edit=True)

    parameters.set_list(
        'columns', label='Select columns',
        description='Select the columns to use perform replacement on',
        value=[], editor=editor)
    parameters.set_string('find', label='Search expression',
                          value='',
                          description='Specify search expression.')
    parameters.set_string('replace', label='Replacement expression',
                          value='',
                          description='Specify replace expression.')
    parameters = common_params(parameters)
    parameters.set_boolean('use_default', label='Use default',
                           value=False,
                           description='Use default value when not found.')
    parameters.set_string('default', label='Default value',
                          value='',
                          description='Specify default value')

    controllers = (
        synode.controller(
            when=synode.field('use_default', state='checked'),
            action=synode.field('default', state='enabled')
        ),
        synode.controller(
            when=synode.field('literal', state='checked'),
            action=synode.field('ignore_case', state='enabled')
        ),
    )

    def update_parameters(self, old_params):
        cols = old_params['columns']
        if not cols.editor.get('mode', False):
            cols._multiselect_mode = 'selected_exists'

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'], node_context.input[0])

    def _get_params(self, node_context):
        params = node_context.parameters
        find = params['find'].value
        replace = params['replace'].value
        use_default = params['use_default'].value
        default = params['default'].value
        ignore = params['ignore_case'].value
        literal = params['literal'].value
        return find, replace, use_default, default, ignore, literal

    def _replace_in_table(self, in_table, columns, params):
        if in_table.number_of_rows() == 0:
            # Table contained no values (but perhaps empty columns).
            # Return original table to not mess up column types.
            return in_table

        out_table = table.File()
        out_table.source(in_table)
        replace_table_values(out_table, columns, params)
        return out_table


class TableValueSearchReplace(TableSearchBase):
    """Search and replace string and unicode values in Table."""

    name = 'Replace values in Table'
    description = 'Search and replace values in Table.'
    nodeid = 'org.sysess.sympathy.data.table.tablevaluesearchreplace'
    inputs = Ports([Port.Table('Input Table', name='table')])
    outputs = Ports([Port.Table('Table with replaced values', name='table')])

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'], node_context.input[0])

    def execute(self, node_context):
        in_table = node_context.input[0]
        columns = node_context.parameters['columns'].selected_names(
            in_table.names())
        out_table = self._replace_in_table(
            in_table, columns, self._get_params(node_context))
        node_context.output[0].update(out_table)


TableValueSearchReplaceMultiple = node_helper.list_node_factory(
    TableValueSearchReplace,
    {'table': {'name': 'tables'}}, {'table': {'name': 'tables'}},
    name='Replace values in Tables',
    nodeid='org.sysess.sympathy.data.table.tablevaluesearchreplacemultiple')


class TableValueSearchReplaceWithTableSuper(synode.Node):
    description = (
        'Searches for and replaces values in specified columns using a table')
    author = (
        'Greger Cronquist <greger.cronquist@combine.se>, '
        'Andreas Tågerud <andreas.tagerud@combine.se>')
    copyright = '(c) 2017 System Engineering Society'
    version = '1.0'
    icon = 'search_replace.svg'
    tags = Tags(Tag.DataProcessing.TransformData)

    parameters = synode.parameters()
    editor_cols = synode.Util.multilist_editor(edit=True)
    editor_col = synode.Util.selectionlist_editor('', filter=True, edit=True)
    parameters.set_list(
        'column', label='Columns to replace values in',
        description='Select in which to perform replacement', value=[],
        editor=editor_cols)
    parameters.set_list(
        'find', label='Column with search expressions',
        description='Select which column contains search expressions',
        value=[], editor=editor_col)
    parameters.set_list(
        'replace', label='Column with replace expressions',
        description='Select which column contains replacements', value=[],
        editor=editor_col)
    parameters = common_params(parameters)

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['find'],
               node_context.input['expressions'])
        adjust(node_context.parameters['replace'],
               node_context.input['expressions'])
        adjust(node_context.parameters['column'],
               node_context.input['data'])

    def execute_once(self, node_context, in_table):
        parameters = node_context.parameters
        exp = node_context.input['expressions']
        ignore = parameters['ignore_case'].value
        try:
            find = exp.get_column_to_array(parameters['find'].selected)
            replace = exp.get_column_to_array(parameters['replace'].selected)
        except (KeyError, ValueError):
            raise SyConfigurationError(
                'One or more of the selected columns do not seem to exist')

        out_table = table.File()
        value_names = parameters['column'].value_names
        out_table.source(in_table)
        for find_val, replace_val in zip(list(find), list(replace)):
            replace_table_values(
                out_table, value_names,
                (find_val, replace_val, False, None,
                    ignore, parameters['literal'].value))
        return out_table


class TableValueSearchReplaceWithTable(TableValueSearchReplaceWithTableSuper):
    name = 'Replace values in Table with Table'
    nodeid = 'org.sysess.sympathy.data.table.tablevaluesearchreplacewithtable'

    inputs = Ports([
        Port.Table('Expressions', name='expressions', requiresdata=True),
        Port.Table('Table Data', name='data', requiresdata=True)])
    outputs = Ports([Port.Table('Table with replaced values', name='data')])

    def execute(self, node_context):
        in_table = node_context.input['data']
        if not in_table.is_empty():
            node_context.output['data'].source(
                self.execute_once(node_context, in_table))


TableValueSearchReplaceWithTableMultiple = node_helper.list_node_factory(
    TableValueSearchReplaceWithTable, ['data'], ['data'],
    name='Replace values in Tables with Table',
    nodeid='org.sysess.sympathy.data.table.tablesvaluesearchreplacewithtable')
