# Copyright (c) 2018, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Combine Control Systems AB nor the
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
import numpy as np
import six

from sympathy.api import node
from sympathy.api.exceptions import SyDataError
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust


class IndexTable(node.Node):
    name = 'Index table'
    description = (
        'Uses index-table to perform row indexation from value-table.\n'
        'No other datatypes than integer or boolean are allowed in the index '
        'column')
    author = 'Mathias Broxvall'
    copyright = '(C) 2018 Combine Control Systems AB'
    version = '0.1'
    icon = 'lookup.svg'

    nodeid = 'org.sysess.sympathy.data.table.indextable'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    inputs = Ports([
        Port.Table('Value table', name='value'),
        Port.Table('Index table', name='index')
    ])
    outputs = Ports([
        Port.Table('Result table', name='out')
    ])

    editor = node.Util.list_editor(filter=True, edit=True)

    parameters = node.parameters()
    parameters.set_list(
        'index column', label='Select indexing column',
        description='Select column used for indexing.',
        value=[], editor=editor)
    parameters.set_boolean(
        'at_one', label='Start at one',
        description='Start indexing at one, otherwise at zero',
        value=False, editor=editor)
    parameters.set_list(
                'operation', label='Operation',
                list=['Include', 'Exclude'], value=[0],
                description='If to include or exclude rows',
                editor=node.Util.combo_editor().value())

    def execute(self, node_context):
        index_tbl = node_context.input['index']
        value_tbl = node_context.input['value']
        out_tbl = node_context.output['out']
        at_one = node_context.parameters['at_one'].value
        exclude = node_context.parameters['operation'].value == [1]

        index_index = node_context.parameters['index column'].value
        try:
            indices = index_tbl.cols()[index_index[0]].data
        except IndexError:
            raise SyDataError('Invalid column selection for index')

        if indices.dtype.kind == 'i':

            try:
                fail = at_one and np.min(np.ma.compressed(indices)) < 1
            except ValueError:
                fail = False

            if fail:
                raise SyDataError('Start at one requires integer column '
                                  'with values >= 1.')
            indices = indices - at_one
        elif at_one:
            raise SyDataError('Invalid datatype {} in index column. '
                              'Start at one requires integer column.'
                              .format(indices.dtype))

        if indices.dtype.kind not in ['b', 'i']:
            raise SyDataError('Invalid datatype {} in index column'
                              .format(indices.dtype))

        for col in value_tbl.cols():
            if exclude:
                mask = np.ones(col.data.shape[0], dtype=bool)
                mask[indices] = False
                out_tbl.set_column_from_array(col.name, col.data[mask])
            else:
                out_tbl.set_column_from_array(col.name, col.data[indices])

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['index column'],
               node_context.input['index'])


class CreateIndexTable(node.Node):
    """
    Create an index column for table data.

    The name of the resulting index column depends on the *name* parameter and
    its values are computed depending on the *method* used and the *columns*
    selected.
    """
    name = 'Create Index Table'
    description = 'Create an index column for table data'
    icon = 'lookup.svg'
    nodeid = 'org.sysess.sympathy.data.table.createindextable'
    tags = Tags(Tag.DataProcessing.Index)

    inputs = Ports([
        Port.Table('Input table', name='input'),
    ])
    outputs = Ports([
        Port.Table('Output table', name='output')
    ])

    _enumerate_rows, _enumerate_unique = _options = [
        'Enumerate rows', 'Enumerate unique rows']

    parameters = node.parameters()
    parameters.set_string(
        'method', label='Select index creation method',
        description='Select method used for index creation.',
        value=_enumerate_rows,
        editor=node.Editors.combo_editor(options=_options))

    parameters.set_list(
        'columns', label='Select columns',
        description='Select columns used for building the index.',
        value=[], editor=node.Editors.multilist_editor(edit=True))

    parameters.set_string(
        'name', label='Name of index column',
        description='Select name for index column.',
        value='index')

    controllers = node.controller(
        when=node.field('method', 'value', value=_enumerate_rows),
        action=node.field('columns', 'disabled'))

    def execute(self, node_context):
        input_ = node_context.input['input']
        output = node_context.output['output']
        output.source(input_)
        method = node_context.parameters['method'].value
        name = node_context.parameters['name'].value

        method = node_context.parameters['method'].value
        if method == self._enumerate_rows:
            output[name] = np.arange(input_.number_of_rows())
        elif method == self._enumerate_unique:
            selected_names = node_context.parameters['columns'].selected_names(
                input_.column_names())
            unique = {}
            indices = []
            count = 0
            for values in six.moves.zip(*[input_[col].tolist()
                                          for col in selected_names]):
                values = tuple(values)
                i = unique.get(values)
                if i is not None:
                    indices.append(i)
                else:
                    unique[values] = count
                    indices.append(count)
                    count += 1
            output[name] = np.array(indices)

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'],
               node_context.input['input'])
