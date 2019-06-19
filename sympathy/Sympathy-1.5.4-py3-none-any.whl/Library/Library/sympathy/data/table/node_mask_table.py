# Copyright (c) 2018 Combine Control Systems AB
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
import numpy as np
from sympathy.api import node as synode
from sympathy.api.nodeconfig import (Port, Ports, Tag, Tags,
                                     adjust)


def selected_columns_op(input_table, output_table, columns, set_progress,
                        update=True):
    if update:
        output_table.set_name(input_table.get_name())
        output_table.set_table_attributes(input_table.get_table_attributes())

    column_names = input_table.column_names()
    selected_names = set(columns.selected_names(column_names))
    n_column_names = len(column_names)

    for i, name in enumerate(column_names):
        set_progress(i * (100. / n_column_names))
        if name in selected_names:
            yield name
        elif update:
            output_table.update_column(name, input_table, name)


class FillMaskedTable(synode.Node):
    """
    Fill masked values in Table.

    :Opposite. nodes: :ref:`Mask values in Table`
    """

    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(c) 2018 Combine Control Systems AB'
    description = 'Fill masked values in Table.'
    icon = 'select_table_columns.svg'
    name = 'Fill masked values in Table'
    nodeid = 'org.sysess.sympathy.table.fillmaskedvalues'
    tags = Tags(Tag.DataProcessing.Select)
    version = '1.0'
    inputs = Ports([Port.Table('Input')])
    outputs = Ports([Port.Table('Output')])
    parameters = synode.parameters()

    parameters.set_list(
        'columns', label='Select columns', description='Select columns.',
        value=[], editor=synode.Editors.multilist_editor(edit=True))
    parameters.set_string(
        'value', label='Value', description='Specified fill value',
        value='')

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'], node_context.input[0])

    def execute(self, node_context):
        in_table = node_context.input[0]
        out_table = node_context.output[0]
        self.fill_columns(
            in_table, out_table, node_context.parameters['columns'],
            self.set_progress, node_context.parameters['value'])

    @staticmethod
    def fill_columns(input_table, output_table, columns, set_progress, fill):

        def fill_conv(column):
            dtype = column.dtype
            if dtype.kind in ['U', 'S']:
                dtype = np.dtype(dtype.kind)
            return column.filled(dtype.type(fill.value))

        for name in selected_columns_op(input_table, output_table, columns,
                                        set_progress):
            array = input_table.get_column_to_array(name)
            if isinstance(array, np.ma.MaskedArray):
                output_table.set_column_from_array(
                    name, fill_conv(array))
                output_table.set_column_attributes(
                    name, input_table.get_column_attributes(name))
            else:
                output_table.update_column(name, input_table, name)


class MaskTable(synode.Node):
    """
    Mask values in Table.

    :Opposite. nodes: :ref:`Fill masked values in Table`
    """

    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(c) 2018 Combine Control Systems AB'
    description = 'Mask values in Table.'
    icon = 'select_table_columns.svg'
    name = 'Mask values in Table'
    nodeid = 'org.sysess.sympathy.table.maskvalues'
    tags = Tags(Tag.DataProcessing.Select)
    version = '1.0'
    inputs = Ports([Port.Table('Input')])
    outputs = Ports([Port.Table('Output')])
    parameters = synode.parameters()

    parameters.set_list(
        'columns', label='Select columns', description='Select columns.',
        value=[], editor=synode.Editors.multilist_editor(edit=True))
    parameters.set_string(
        'value', label='Value', description='Specified fill value',
        value='')

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'], node_context.input[0])

    def execute(self, node_context):
        in_table = node_context.input[0]
        out_table = node_context.output[0]
        self.mask_columns(
            in_table, out_table, node_context.parameters['columns'],
            self.set_progress, node_context.parameters['value'])

    @staticmethod
    def mask_columns(input_table, output_table, columns, set_progress, fill):

        def mask_conv(column):
            dtype = column.dtype
            if dtype.kind in ['U', 'S']:
                dtype = np.dtype(dtype.kind)

            value = dtype.type(fill.value)

            if dtype.kind == 'f' and np.isnan(value):
                mask = np.isnan(column)
            elif dtype.kind in ['m', 'M'] and np.isnat(value):
                mask = np.isnat(column)
            else:
                mask = column == value

            if isinstance(column, np.ma.MaskedArray):
                mask |= column.mask
                res = np.ma.MaskedArray(column.data, mask, dtype=dtype)
            else:
                res = np.ma.MaskedArray(column, mask, dtype=dtype)
            return res

        for name in selected_columns_op(input_table, output_table, columns,
                                        set_progress):
            output_table.set_column_from_array(
                name, mask_conv(input_table.get_column_to_array(name)))
            output_table.set_column_attributes(
                name, input_table.get_column_attributes(name))


class DropMaskTable(synode.Node):
    """
    Drop masked values in Table.

    :Ref. nodes: :ref:`Fill masked values in Table`,
                 :ref:`Mask values in Table`
    """
    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(c) 2018 Combine Control Systems AB'
    description = 'Drop masked values in Table.'
    icon = 'select_table_columns.svg'
    name = 'Drop masked values in Table'
    nodeid = 'org.sysess.sympathy.table.dropmaskvalues'
    tags = Tags(Tag.DataProcessing.Select)
    version = '1.0'
    inputs = Ports([Port.Table('Input')])
    outputs = Ports([Port.Table('Output')])
    parameters = synode.parameters()

    parameters.set_list(
        'columns', label='Select columns', description='Select columns.',
        value=[], editor=synode.Editors.multilist_editor(edit=True))

    directions = ['Rows', 'Columns']

    parameters.set_string(
        'direction', label='Drop',
        value=directions[0],
        description='Select along which axis to drop values',
        editor=synode.Editors.combo_editor(options=directions))

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'], node_context.input[0])

    def execute(self, node_context):
        in_table = node_context.input[0]
        out_table = node_context.output[0]
        self.drop_columns(
            in_table, out_table, node_context.parameters['columns'],
            self.set_progress, node_context.parameters['direction'])

    @staticmethod
    def drop_columns(input_table, output_table, columns, set_progress,
                     direction):

        def mask_conv(column):
            dtype = column.dtype
            if dtype.kind in ['U', 'S']:
                dtype = np.dtype(dtype.kind)

        if direction.value == 'Columns':

            for name in selected_columns_op(input_table, output_table, columns,
                                            set_progress):
                array = input_table.get_column_to_array(name)
                if isinstance(array, np.ma.MaskedArray):
                    if not np.any(array.mask):
                        output_table.set_column_from_array(
                            name, array.data)
                        output_table.set_column_attributes(
                            name, input_table.get_column_attributes(name))
                else:
                    output_table.update_column(name, input_table, name)

        elif direction.value == 'Rows':
            mask = np.zeros(input_table.number_of_rows(), dtype=bool)
            for name in selected_columns_op(input_table, output_table, columns,
                                            set_progress, update=False):
                array = input_table.get_column_to_array(name)
                if isinstance(array, np.ma.MaskedArray):
                    mask |= array.mask
            if not np.any(mask):
                output_table.update(input_table)
            else:
                for name in input_table.column_names():
                    array = input_table.get_column_to_array(name)
                    array = array[~mask]

                    if isinstance(array, np.ma.MaskedArray):
                        if not np.any(array.mask):
                            array = array.data

                    output_table.set_column_from_array(
                        name, array)
                    output_table.set_column_attributes(
                        name, input_table.get_column_attributes(name))
