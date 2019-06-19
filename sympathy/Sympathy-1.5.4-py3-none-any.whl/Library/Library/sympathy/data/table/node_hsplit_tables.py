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
The horisontal split, or HSplit, nodes split the incoming Tables into new
Tables by columns. Compared to the :ref:`VSplit Table` nodes where the split
procedure can be regulated by a selected index column, these nodes will place
every column in the incoming Tables into separate Tables in an outgoing list.
"""
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags


class HSplitTableNode(synode.Node):
    """
    Horisontal split of a Table. The output is a list of Tables, where the
    columns in the incoming Table are placed in separate Tables in the output.

    :Opposite node: :ref:`HJoin Tables`
    :Ref. nodes: :ref:`HSplit Tables`
    """

    author = "Greger Cronquist <greger.cronquist@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.0'
    icon = 'hsplit_table.svg'

    name = 'HSplit Table'
    description = ('Split a Table into multiple Tables by columns, '
                   'every column becomes a new table.')
    nodeid = 'org.sysess.sympathy.data.table.hsplittablenode'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    inputs = Ports([Port.Table('Input Table', name='port1')])
    outputs = Ports([Port.Tables('Joined Tables', name='port1')])

    def execute(self, node_context):
        tablefile = node_context.input['port1']
        outfilelist = node_context.output['port1']
        columns = tablefile.column_names()
        number_of_columns = len(columns)
        original_name = tablefile.get_name()
        for col_number, column in enumerate(columns):
            table_outfile = outfilelist.create()
            table_outfile.update_column(column, tablefile, column)
            table_outfile.set_name(u'{0}-{1}'.format(
                original_name, col_number))
            outfilelist.append(table_outfile)
            self.set_progress(100.0 * (col_number + 1) /
                              number_of_columns)


class HSplitTablesNode(synode.Node):
    """
    Horisontal split of Tables. The output is a list of Tables, where the
    columns in the incoming Tables are placed in separate Tables in the
    output.

    :Ref. nodes: :ref:`HSplit Table`
    """

    author = "Greger Cronquist <greger.cronquist@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.0'
    icon = 'hsplit_table.svg'

    name = 'HSplit Tables'
    description = ('Split a list of Table into multiple Tables, '
                   'every column becomes a new table.')
    nodeid = 'org.sysess.sympathy.data.table.hsplittablenodes'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    inputs = Ports([Port.Tables('Input Tables', name='port1')])
    outputs = Ports([Port.Tables('Joined Tables', name='port1')])

    def execute(self, node_context):
        infilelist = node_context.input['port1']
        outfilelist = node_context.output['port1']
        for intable in infilelist:
            original_name = intable.get_name()
            for col_number, column in enumerate(intable.column_names()):
                output = outfilelist.create()
                output.update_column(column, intable, column)
                output.set_name(u'{0}-{1}'.format(original_name, col_number))
                outfilelist.append(output)
