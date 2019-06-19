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
from sympathy.api import node
from sympathy.api import table
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Tag, Tags


class DropNaNOperation(node_helper.TableOperation):
    """Remove rows or columns with NaN (not a number) in them."""

    author = 'Greger Cronquist <greger.cronquist@combine.se>'
    copyright = '(c) 2014 Combine Control Systems AB'
    description = 'Drop columns or rows with NaN values'
    version = '1.0'
    icon = 'drop_nan.svg'
    tags = Tags(Tag.DataProcessing.Select)

    inputs = ['Input']
    outputs = ['Output']

    @staticmethod
    def get_parameters(parameter_group):
        parameter_group.set_list(
            'direction', label='Drop',
            list=['Rows with NaN', 'Columns with NaN'],
            description='Select along which axis to drop values',
            editor=node.Util.combo_editor())

    def execute_table(self, in_table, out_table, parameter_root):
        in_frame = in_table['Input'].to_dataframe()
        if parameter_root['direction'].value[0] == 0:
            out_frame = in_frame.dropna(axis=0)
        else:
            out_frame = in_frame.dropna(axis=1)
        out_table['Output'].source(table.File.from_dataframe(out_frame))
        out_table['Output'].set_attributes(in_table['Input'].get_attributes())
        out_table['Output'].set_name(in_table['Input'].get_name())


DropNaNTable = node_helper.table_node_factory(
    'DropNaNTable', DropNaNOperation,
    'Drop NaN Table', 'org.sysess.sympathy.data.table.dropnantable')


DropNaNTables = node_helper.tables_node_factory(
    'DropNaNTables', DropNaNOperation,
    'Drop NaN Tables', 'org.sysess.sympathy.data.table.dropnantables')
