# Copyright (c) 2013, Combine Control Systems AB
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
This category of nodes filter out the rows in Tables for which a specified
column has repeated values. The Tables in the output will have lesser or
equal number of rows as the incoming Tables.

In the configuration GUI the column to filter by is selected.
"""

from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Tag, Tags, adjust
from sympathy.api import table


class UniqueOperation(node_helper.TableOperation):
    """Filter out rows in Tables for which a selected column has repeated
    values.
    """

    author = 'Greger Cronquist <greger.cronquist@combine.se>'
    copyright = '(c) 2013 Combine Control Systems AB'
    nodeid = 'org.sysess.sympathy.data.table.uniquetables'
    icon = 'unique_table.svg'
    version = '1.0'
    inputs = ['Input']
    outputs = ['Output']
    tags = Tags(Tag.DataProcessing.Select)

    @staticmethod
    def get_parameters(parameter_group):
        editor = synode.Util.multilist_editor(edit=True)
        parameter_group.set_list(
            'column', label='Columns to filter by',
            description='Columns to use as uniqueness filter.',
            editor=editor)

    def adjust_table_parameters(self, in_table, parameters):
        adjust(parameters['column'], in_table['Input'])

    def execute_table(self, in_table, out_table, parameters):
        current_selected = parameters['column'].selected_names(
            in_table['Input'].names())
        if not (in_table['Input'].number_of_rows() and current_selected):
            out_table['Output'].update(in_table['Input'])
            return

        df = in_table['Input'].to_dataframe()
        df2 = df.drop_duplicates(current_selected)

        out_table['Output'].source(table.File.from_dataframe(df2))
        out_table['Output'].set_attributes(in_table['Input'].get_attributes())
        out_table['Output'].set_name(in_table['Input'].get_name())


UniqueTable = node_helper.table_node_factory(
    'UniqueTable', UniqueOperation,
    'Unique Table', 'org.sysess.sympathy.data.table.uniquetable')


UniqueTables = node_helper.tables_node_factory(
    'UniqueTables', UniqueOperation,
    'Unique Tables', 'org.sysess.sympathy.data.table.uniquetables')
