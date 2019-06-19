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
Ensure the existence of one or several signals in :ref:`Tables` by either
getting an exception or adding a dummy signal to the dataset.
"""
import numpy as np

from sympathy.api import node as synode
from sympathy.api import table
from sympathy.api import exceptions, dtypes
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust

REPORTING = ['Exception', 'Dummy Signal', 'Masked Signal', 'Zero Signal']
EXE, DUMMY, MASK, ZERO = REPORTING


def ensure_columns(in_table, out_table, selection_table, selection_col,
                   types_col, mode):
    out_table.update(in_table)
    column_names = selection_table.get_column_to_array(selection_col)
    if mode == MASK or mode == ZERO:
        types = selection_table.get_column_to_array(types_col)

    for i, column_name in enumerate(column_names):

        if column_name not in out_table:
            if mode == EXE:
                raise exceptions.SyDataError(
                    "Column {} missing.".format(column_name))
            elif mode == DUMMY:
                attr = {'info': 'Missing column'}
                out_table.set_column_from_array(
                    column_name,
                    np.repeat(np.nan, out_table.number_of_rows()),
                    attr)
            elif mode == MASK:
                attr = {'info': 'Missing column'}
                out_table.set_column_from_array(
                    column_name,
                    np.ma.MaskedArray(
                        np.empty(
                            out_table.number_of_rows(),
                            dtype=dtypes.dtype(types[i])),
                        mask=True),
                    attr)
            elif mode == ZERO:
                attr = {'info': 'Missing column'}
                out_table.set_column_from_array(
                    column_name,
                    np.zeros(
                        out_table.number_of_rows(),
                        dtype=dtypes.dtype(types[i])),
                    attr)


class EnsureColumnsOperation(synode.Node):
    """
    Ensure the existence of columns in Tables by using an additional
    Table with the name of the columns that must exist. Select to get
    the result of the check as the form of an exception or as an added
    dummy signal. The type of the dummy signal is by default float with
    all elements set to NaN. Finally mask, can also be used. In that case,
    a type column also needs to be selected. Otherwise it is ignored.
    When mask is used, and ensured columns are missing, these will be created
    as fully masked arrays of the select types.

    :Ref. nodes: :ref:`Rename columns in Tables`
    """

    name = 'Ensure columns in Tables with Table'
    author = 'Daniel Hedendahl <daniel.hedendahl@combine.se>'
    copyright = '(C) 2014 Combine Control Systems AB'
    version = '1.0'
    description = 'Ensure the existence of column in Table.'
    nodeid = 'org.sysess.sympathy.data.table.ensuretablecolumns'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    icon = 'ensure_column.svg'

    inputs = Ports([
        Port.Table('Selection', name='selection'),
        Port.Tables('Input Tables', name='tables')])
    outputs = Ports([Port.Tables('Output Table', name='tables')])

    parameters = synode.parameters()
    parameters.set_list(
        'columns', label='Column with column names',
        description=(
            'Name of column with names of the columns that must exist'),
        editor=synode.Util.combo_editor(edit=True, filter=True))

    parameters.set_list(
        'types', label='Column with column types',
        description=(
            'Name of column with types of the columns that must exist, '
            'only for use with "Masked Signal" reporting'),
        editor=synode.Util.combo_editor(edit=True, filter=True))

    parameters.set_list(
        'reporting', label='Action of missing columns:',
        plist=REPORTING, value=[0],
        description='Select action if columns are missing',
        editor=synode.Util.combo_editor())

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'],
               node_context.input['selection'])

        adjust(node_context.parameters['types'],
               node_context.input['selection'])

    def execute(self, node_context):
        parameter_group = synode.parameters(node_context.parameters)
        try:
            selection_col = parameter_group['columns'].selected
        except KeyError:
            selection_col = None

        try:
            types_col = parameter_group['types'].selected
        except KeyError:
            types_col = None

        input_files = node_context.input['tables']
        output_files = node_context.output['tables']
        for input_file in input_files:
            output_file = table.File()
            output_file.set_name(input_file.get_name())

            selection_table = node_context.input['selection']
            if selection_col is not None:
                mode = parameter_group['reporting'].selected
                ensure_columns(input_file, output_file, selection_table,
                               selection_col, types_col, mode)

            output_files.append(output_file)
