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
The operation of horizontal join, or HJoin, stacks the columns in the incoming
:ref:`Tables` horizontally beside each other. The outgoing Table will have all
the columns from all the incoming Tables.

If the setting 'Complement missing rows' is false then all Tables that should
be joined must have the same number of rows. Otherwise, Tables with different
number of rows are padded with masked values.

If a column name exists in both inputs the latter Table (or lower port) will
take precedence and the corresponding column from the former Table (or upper
port) will be lost.

The node always tries to give the output table a name, so if the chosen
port has a table without name, the other port will be used. This is
to preserve backwards compatibility.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import SyDataError


def _join_table(table1, table2, first_name, mask=False, rename=False):
    if ((table1.number_of_rows() != table2.number_of_rows())
            and table1.number_of_columns() and table2.number_of_columns()
            and not mask):
        raise SyDataError(
            'Number of rows mismatch in tables ({} vs {})'.format(
                table1.number_of_rows(), table2.number_of_rows()))
    name1 = table1.get_name()
    name2 = table2.get_name()
    if not name1:
        name = name2
    elif not name2:
        name = name1
    else:
        name = name1 if first_name else name2
    table1.hjoin(table2, mask=mask, rename=rename)
    table1.set_name(name)
    return table1


class HJoinTableSuper(synode.Node):
    author = "Alexander Busck <alexander.busck@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.1'
    icon = 'hjoin_table.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    parameters = {}
    parameter_root = synode.parameters(parameters)
    parameter_root.set_boolean(
        'mask', value=True, label='Complement missing rows',
        description='Select if rows that are not represented in all '
                    'Tables should be complemented with masked values')
    parameter_root.set_boolean(
        'rename', value=False, label='Rename duplicate columns',
        description=('If true columns with same name as an earlier column '
                     'will be renamed and joined, otherwise columns will '
                     'overwrite existing data'))
    parameter_root.set_list(
        'name',
        plist=['Lower', 'Upper'],
        label='Input port name for joined table',
        description='Select which port decides the output table(s) names',
        value=[0],
        editor=synode.Util.combo_editor())

    def update_parameters(self, old_params):
        if 'mask' not in old_params:
            old_params['mask'] = self.parameter_root['mask']
            old_params['mask'].value = False
        if 'rename' not in old_params:
            old_params['rename'] = self.parameter_root['rename']
            old_params['rename'].value = False


class HJoinTable(HJoinTableSuper):
    """
    Horizontal join of two Tables into a single Table.

    :Opposite node: :ref:`HSplit Table`
    """

    name = 'HJoin Table'
    description = 'Horizontal join of two Tables'
    nodeid = 'org.sysess.sympathy.data.table.hjointable'

    inputs = Ports([
        Port.Table('Input Table 1', name='port1'),
        Port.Table('Input Table 2', name='port2')])
    outputs = Ports([Port.Table(
        'Table with horizontally joined data', name='port1')])

    def execute(self, node_context):
        """Execute"""
        node_context.output['port1'].source(_join_table(
            node_context.input['port1'],
            node_context.input['port2'],
            node_context.parameters['name'].value[0],
            mask=node_context.parameters['mask'].value,
            rename=node_context.parameters['rename'].value
        ))


HJoinTables = node_helper.list_node_factory(
    HJoinTable,
    ['port1', 'port2'], ['port1'],
    nodeid='org.sysess.sympathy.data.table.hjointables',
    name='HJoin Tables pairwise')


class HJoinTablesSingle(synode.Node):
    """
    Horizontal join of all incoming Tables into a single outgoing Table.
    Columns from Tables later in the list will take precedence in the case when
    a certain column name exists in two or more Tables.

    :Opposite node: :ref:`HSplit Table`
    """

    author = "Greger Cronquist <greger.cronquist@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.0'
    icon = 'hjoin_table.svg'
    name = 'HJoin Tables'
    description = 'HJoin Tables to Table'
    nodeid = 'org.sysess.sympathy.data.table.hjointablessingle'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    inputs = Ports([Port.Tables('Input Tables', name='port1')])
    outputs = Ports([
        Port.Table('Table with horizontally joined data from the incoming '
                   'list of Tables.', name='port1')])

    parameters = {}
    parameter_root = synode.parameters(parameters)
    parameter_root.set_boolean(
        'mask', value=True, label='Complement missing rows',
        description='Select if rows that are not represented in all '
                    'Tables should be complemented with masked values')
    parameter_root.set_boolean(
        'rename', value=False, label='Rename duplicate columns',
        description=('If true columns with same name as an earlier column '
                     'will be renamed and joined, otherwise columns will '
                     'overwrite existing data'))

    def update_parameters(self, old_params):
        if 'mask' not in old_params:
            old_params['mask'] = self.parameter_root['mask']
            old_params['mask'].value = False
        if 'rename' not in old_params:
            old_params['rename'] = self.parameter_root['rename']
            old_params['rename'].value = False

    def execute(self, node_context):
        """Execute"""
        in_files = node_context.input['port1']
        out_tablefile = node_context.output['port1']

        if not in_files:
            return

        for i, table in enumerate(in_files):
            progress = (100.0 * i) / len(in_files)
            self.set_progress(progress)
            out_tablefile.hjoin(
                table,
                mask=node_context.parameters['mask'].value,
                rename=node_context.parameters['rename'].value)
        out_tablefile.set_name(in_files[-1].get_name())
