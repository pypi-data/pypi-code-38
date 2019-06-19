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
The operation of vertical split, or VSplit, performs a rowwise split of
:ref:`Tables`.

If an index column is specified in the configuration GUI the split will be
performed according to defined groups in this column. Otherwise the
node will place every row of the incoming Table into separate Tables in
the outgoing list.

In the index column the elements of the rows, that belong to the same group,
should all have the same value. An example of an index column is created by the
:ref:`VJoin Table` node, where the elements in the joined output that
originates from the same incoming Table will be given the same index number.

If "One table for each row" is used, the selected index is ignored and the
split is performed as if each row had their own distinct index value.
Otherwise, for tables where the selected index column is missing,
"Action on missing Index" controls the behavior.

Yet another available option in the node is to remove columns that after the
split contain only NaNs or empty strings. This is called "Remove complement
columns" in the configuration GUI and is (loosly speaking) the reversal of the
creation of complements for missing columns preformed by the :ref:`VJoin Table`
node.
"""
import numpy as np
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import SyDataError

_missing_options = [
    'Multiple tables, one for each row',
    'Single table, one table for all rows',
    'Error']


def _set_missing_index(parameters):
    parameters.set_string(
        'missing_index',
        label='Action on missing index',
        value=_missing_options[0],
        description=(
            'Choose name how to handle tables where the selected index column '
            ' is missing.'),
        editor=synode.Util.combo_editor(options=_missing_options))


def _missing_action(parameters):
    index = parameters['missing_index'].value
    action = False
    if 'Multi' in index:
        action = 'm'
    elif 'Single' in index:
        action = 's'
    else:
        action = 'e'
    return action


class VSplitBase(synode.Node):
    parameters = synode.parameters()
    parameters.set_boolean(
        'no_index',
        label='One table for each row.',
        value=True,
        description=(
            'If checked, each row in the input table will be put in a '
            'different table in the output. If unchecked, you need to specify '
            'an index column which will then be used to determine what rows '
            'go in which table.'))

    parameters.set_string(
        'input_index',
        label='Index column',
        value='',
        description=(
            'Choose name for index column. All rows with the same value in '
            'this column will end up in the same output table.'),
        editor=synode.Util.combo_editor(edit=True))

    _set_missing_index(parameters)

    parameters.set_boolean(
        'remove_fill', value=False, label='Remove complement columns',
        description=('After splitting, remove columns that contain only '
                     'NaN or empty strings.'))
    tags = Tags(Tag.DataProcessing.TransformStructure)

    controllers = synode.controller(
        when=synode.field('no_index', 'checked'),
        action=(synode.field('input_index', 'disabled'),
                synode.field('missing_index', 'disabled')))

    def update_parameters(self, old_params):
        # Add no_index checkbox with backward compatible value.

        if 'no_index' not in old_params:
            old_params['no_index'] = self.parameters['no_index']
            old_params['no_index'].value = (
                not old_params['input_index'].value)

        if 'missing_index' not in old_params:
            _set_missing_index(old_params)

        # Update editor for input index. Old version of node had a simple
        # lineedit (editor=None).
        if old_params['input_index'].editor is None:
            old_params['input_index'].editor = (
                synode.Util.combo_editor(edit=True))

        if 'require_index' in old_params:
            if old_params['require_index'].value is True:
                old_params['missing_index'].value = 'Error'
            del old_params['require_index']


class VSplitTableNode(VSplitBase):
    """
    Vertical split of Table into Tables.

    :Opposite node: :ref:`VJoin Table`
    :Ref. nodes: :ref:`VSplit Tables`
    """

    author = "Alexander Busck <alexander.busck@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.0'
    icon = 'vsplit_table.svg'

    name = 'VSplit Table'
    description = 'Vertical split of Table into Tables.'
    nodeid = 'org.sysess.sympathy.data.table.vsplittablenode'

    inputs = Ports([Port.Table('Input Table', name='port1')])
    outputs = Ports([Port.Tables('Split Tables', name='port1')])

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['input_index'],
               node_context.input[0])

    def execute(self, node_context):
        input_table = node_context.input['port1']
        output_tables = node_context.output['port1']
        input_index = node_context.parameters['input_index'].value
        missing_action = _missing_action(node_context.parameters)
        no_index = node_context.parameters['no_index'].value

        if no_index:
            input_index = None
            missing_action = 'm'

        if input_index not in input_table:
            if missing_action == 'm':
                input_index = None
            elif missing_action == 's':
                input_index = np.zeros(input_table.number_of_rows(), dtype=int)
            else:
                raise SyDataError(
                    'Selected and required input index is missing.')

        input_table.vsplit(
            output_tables,
            input_index,
            node_context.parameters['remove_fill'].value)


class VSplitTablesNode(VSplitBase):
    """
    Vertical split of Tables into Tables.

    :Opposite node: :ref:`VJoin Tables`
    :Ref. nodes: :ref:`VSplit Table`
    """

    author = "Alexander Busck <alexander.busck@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.0'
    icon = 'vsplit_table.svg'

    name = 'VSplit Tables'
    description = ('Vertical split of Tables into Tables.')
    nodeid = 'org.sysess.sympathy.data.table.vsplittablenodes'

    inputs = Ports([Port.Tables('Input Tables', name='port1')])
    outputs = Ports([Port.Tables('Split Tables', name='port1')])

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['input_index'],
               node_context.input[0])

    def execute(self, node_context):
        input_list = node_context.input['port1']
        output_tables = node_context.output['port1']
        input_index = node_context.parameters['input_index'].value
        number_of_files = len(input_list)
        missing_action = _missing_action(node_context.parameters)
        no_index = node_context.parameters['no_index'].value

        if no_index:
            input_index = None
            missing_action = 'm'

        for i, table in enumerate(input_list):
            index = input_index
            if input_index not in table:
                if missing_action == 'm':
                    index = None
                elif missing_action == 's':
                    index = np.empty(table.number_of_rows(), dtype=int)
                    index.fill(i)
                else:
                    raise SyDataError(
                        'Selected and required input index is missing.')

            table.vsplit(
                output_tables,
                index,
                node_context.parameters['remove_fill'].value)

            self.set_progress(100.0 * (i + 1) / number_of_files)
