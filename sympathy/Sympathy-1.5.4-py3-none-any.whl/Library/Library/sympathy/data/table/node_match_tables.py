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
To compare the number of rows in two :ref:`Tables` and resize one of them,
in order to have two Tables with equal numbers of rows, is the functionality
of the nodes in the considered category. For example, this may be helpful if
one would like to horisontal join two Tables with different number of rows,
which is not possible according to the definition of a Table,
see :ref:`Tables` and :ref:`HJoin Table`.

In the procedure of the node, the Table connected to the upper of the two
inputs is used as reference while the Table coming in through the lower port
is the one that is going to be modified. The modification can either be a
contraction or an extension of the Table depending if it is longer or shorter
than the reference Table, respectively.

The extension will be preformed according to one of the following strategies:
    - Use last value
    - Fill with zeroes (or empty strings/dates or similar)
    - Fill with NaNs (or None or similar)

"""
import numpy as np
from sympathy.api import table
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags


class MatchTablesBase(object):
    author = 'Greger Cronquist <greger.cronquist@combine.se'
    copyright = '(c) 2013 Combine Control Systems AB'
    version = '1.0'
    icon = 'match_tables.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    parameters = synode.parameters()
    parameters.set_list(
        'fill', value=[0], label='Extend values',
        description=(
            'Specify the values to use if the input has to be extended.'),
        plist=['Last value', '0.0 or empty string', 'np.NaN or empty string'],
        editor=synode.Util.combo_editor().value())

    def _match_table(self, parameters, guide, input_table):
        guide_length = guide.number_of_rows()
        table_length = input_table.number_of_rows()

        if guide_length == 0:
            output_table = input_table[:0]
        else:
            if guide_length == table_length:
                output_table = input_table
            elif guide_length < table_length:
                output_table = input_table[:guide_length]
            elif guide_length > table_length:
                output_table = table.File()
                fill_table = table.File()
                fill_method = parameters['fill'].value[0]
                length_diff = guide_length - table_length

                for name in input_table.column_names():
                    dtype = input_table.column_type(name)

                    if fill_method == 0:
                        # Repeat last value:
                        last_value = input_table.get_column_to_array(
                            name, table_length - 1)

                        if np.ma.is_masked(last_value):
                            column = np.ma.masked_all(length_diff, dtype=dtype)
                        else:
                            column = np.full(length_diff, last_value,
                                             dtype=dtype)
                    elif fill_method == 1:
                        # Use zero-like fill values.
                        if dtype.kind in ['S', 'U']:
                            dtype = dtype.kind + '1'
                        else:
                            dtype = dtype
                        column = np.zeros(length_diff, dtype=dtype)
                    elif fill_method == 2:
                        # Use NaN or empty string.
                        if dtype.kind in ['S', 'U']:
                            dtype = dtype.kind + '1'
                            column = np.zeros(length_diff, dtype=dtype)
                        else:
                            column = np.full(length_diff, np.nan, dtype='f2')
                    else:
                        assert False, 'Unknown extension method.'

                    fill_table[name] = column

                output_table.vjoin([input_table, fill_table])
                output_table.set_attributes(input_table.get_attributes())
                output_table.set_name(input_table.get_name())
        return output_table


class MatchTwoTables(MatchTablesBase, synode.Node):
    """
    Match column lengths in Table with column lengths of reference Table.
    """

    name = 'Match Table lengths'
    nodeid = 'org.sysess.sympathy.data.table.matchtwotables'
    description = 'Match the column lengths of two Tables.'
    inputs = Ports([
        Port.Table('Guide', name='guide'),
        Port.Table('Input Table', name='input')])
    outputs = Ports([Port.Table('Length matched Table', name='output')])

    def __init__(self):
        super(MatchTwoTables, self).__init__()

    def execute(self, node_context):
        output = self._match_table(node_context.parameters,
                                   node_context.input['guide'],
                                   node_context.input['input'])
        node_context.output['output'].update(output)


MatchTwoTablesMultiple = node_helper.list_node_factory(
    MatchTwoTables,
    ['guide', 'input'], ['output'],
    name='Match Tables lengths',
    nodeid='org.sysess.sympathy.data.table.matchtwotablesmultiple')
