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
The operation of vertical join, or VJoin, stacks the columns from
the incoming :ref:`Tables` that have the same name vertically upon
each other, under the condition that they exist in all Tables. If the
condition is fulfilled the number of rows in the outgoing Table will
be equal to the sum of the number of rows in the incoming Tables. If
there exist no overlap over all Tables the output will be an empty
Table.

In the GUI it is possible to override the overlap requirement and let
the node work in a state where the output will include all columns
that exist in the incoming Tables. The columns that do not exist in
all Tables are either ignored, created as a "masked" value, or
complemented with default values.  The strategy for this is decided by
the "Complement missing columns"-checkbox as well as the
"Complement-strategy" combo options. In the case of complementing with
a value a column with numerical values is filled with NaNs while for a
column with strings the elements it is filled with empty strings.

When the columns stacked have different types, the node will try to find a
result type to accommodate the new values. For example, combining an integer
and a boolean would result in an integer column with the boolean values
translated from False to 0 and True to 1. LIMITATION: If the types differ and
part of the column is date-time or time-delta no resulting type can be found.

An index column will be created in the outgoing Table if a name is specified
for the column in the GUI, by default the index column has the name
"VJoin-index". In the index column, elements in the joined output that
originate from the same incoming Table will be given the same index number.
If one wants to do the reversed operation, :ref:`VSplit Table`, the index
column is important. No index column will be created if the specified name
is an empty string.

In the GUI it is also possible to specify the name of an incoming index column,
a column with information about previous VJoin operations. If the specified
index column exists in the incoming Tables the information of the previous join
operations will be regarded when the new index column is constructed. The new
index column will replace the old ones in the output of the node.

An increment will be applied to the outgoing index column if there exist
incoming Tables with the number of rows equal to zero. The size of this
increment can be specified in the GUI of the node, where default value is 0.
The vertical join, or VJoin, is one of two operations that merge the
content of a number of :ref:`Tables` into a new Table. The other operation
in this category is the horizontal join, see :ref:`HJoin Table` to obtain more
information.
"""
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import exceptions as exc
from sylib import vjoin


class VJoinBase(synode.Node):
    parameters = vjoin.base_params()
    controllers = vjoin.base_controller()
    tags = Tags(Tag.DataProcessing.TransformStructure)

    def update_parameters(self, old_params):
        if 'fill_strategy' not in old_params:
            vjoin.set_fill_strategy_param(old_params, 0)

    def vjoin(self, output_table, input_tables, input_index, output_index,
              fill, minimum_increment):

        try:
            output_table.vjoin(
                input_tables,
                input_index,
                output_index,
                fill,
                minimum_increment)
        except exc.SyColumnTypeError:
            raise exc.SyDataError(
                'Input columns to stack have incompatible types',
                details=(
                    'Input columns to stack have incompatible types. '
                    'Keep in mind that datetime and timedelta cannot be '
                    'combined with other types'))


class VJoinTableNode(VJoinBase):
    """
    Vertical join of two Tables.

    :Opposite node: :ref:`VSplit Table`
    :Ref. nodes: :ref:`VJoin Tables pairwise`, :ref:`VJoin Tables`
    """

    author = "Alexander Busck <alexander.busck@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.0'
    icon = 'vjoin_table.svg'

    name = 'VJoin Table'
    description = ('Vertical join of two Tables.')
    nodeid = 'org.sysess.sympathy.data.table.vjointablenode'

    inputs = Ports([
        Port.Table('Input Table 1', name='port1'),
        Port.Table('Input Table 2', name='port2')])
    outputs = Ports([Port.Table('Joined Table', name='port1')])

    def execute(self, node_context):
        input_table1 = node_context.input['port1']
        input_table2 = node_context.input['port2']
        output_table = node_context.output['port1']
        input_index, output_index, minimum_increment, fill = vjoin.base_values(
            node_context.parameters)

        self.vjoin(
            output_table,
            [input_table1, input_table2],
            input_index,
            output_index,
            fill,
            minimum_increment)


VJoinTableMultipleNode = node_helper.list_node_factory(
    VJoinTableNode,
    ['port1', 'port2'], ['port1'],
    name='VJoin Tables pairwise',
    nodeid='org.sysess.sympathy.data.table.vjointablenodelist')


class VJoinTablesNode(VJoinBase):
    """
    Vertical join of Tables.

    :Opposite node: :ref:`VSplit Table`
    :Ref. nodes: :ref:`VJoin Table`, :ref:`VJoin Tables pairwise`
    """

    author = "Alexander Busck <alexander.busck@combine.se>"
    copyright = "(C) 2012 Combine Control Systems AB"
    version = '1.0'
    icon = 'vjoin_table.svg'

    name = 'VJoin Tables'
    description = ('Vertical join of Tables.')
    nodeid = 'org.sysess.sympathy.data.table.vjointablenodes'

    inputs = Ports([Port.Tables('Input Tables', name='port1')])
    outputs = Ports([Port.Table('Joined Tables', name='port1')])

    def execute(self, node_context):
        input_tables = node_context.input['port1']
        output_table = node_context.output['port1']
        input_index, output_index, minimum_increment, fill = vjoin.base_values(
            node_context.parameters)

        self.vjoin(
            output_table,
            input_tables,
            input_index,
            output_index,
            fill,
            minimum_increment)
