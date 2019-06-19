# Copyright (c) 2016-2017, Combine Control Systems AB
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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from sympathy.api import qt as qt_compat
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, join_doc
from sylib import util
from sympathy.api.exceptions import SyDataError

QtGui = qt_compat.import_module('QtGui')
QtCore = qt_compat.import_module('QtCore')

COMMON_DOCSTRING = """
Filter the row in a table according to a comparison relation between the
elements of two column. One of the column, C1, is located in the Table
that will be filtered while the other, C0, is a column in a reference Table.

The comparison relation can be defined as a lambda function in the
configuration GUI or one of the predefined relations can be used.

The predefined relations are the following:
    - Match C1 in C0
        keeps the row if the corresponding element in C1 exists in any row
        in C0.
    - Don't match C1 in C0
        keeps the row if corresponding element in C1 do not exist in any row
        in C0.

A custom filter function can be defined by writing a lambda function. The
lambda function will be called once for each item in the selected column C1
with the full column C0 available under the name `C0`. The lambda function
should return True or False.

See https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions
for a description of lambda functions. Have a look at the :ref:`Table
API<tableapi>` to see all the available methods and attributes.
"""

COLUMN_FILTERS = {
    'Match C1 in C0': 'lambda x: x in C0',
    "Don't match C1 in C0": 'lambda x: x not in C0'
}


def execute_filter_query(table1, table2, parameter_root):
    c0_column_name = parameter_root['c0_column'].selected
    c0_df = table1.to_dataframe()

    c1_column_name = parameter_root['c1_column'].selected
    c1_df = table2.to_dataframe()
    # special case if incoming table has no rows

    if c0_column_name is None or c1_column_name is None:
        raise SyDataError('Selected columns are not valid.')

    c0_column = c0_df[c0_column_name]
    c1_column = c1_df[c1_column_name]
    # Expose columns as C0 and C1 when evaluating lambda function
    env = {
        'C0': c0_column.values,
        'C1': c1_column.values
    }
    use_custom_predicate = parameter_root['use_custom_predicate'].value

    if use_custom_predicate:
        predicate = util.base_eval(
            parameter_root['predicate_function'].value, env)
        selection = c1_column.apply(predicate)
    else:
        selected_filter_name = parameter_root['filter_functions'].selected
        selection = c1_column.isin(c0_column)
        if not selected_filter_name.startswith('Match'):
            selection = - selection
    return selection


class ColumnFilterWidget(QtGui.QWidget):

    def __init__(self, table1, table2, parameters, parent=None):
        super(ColumnFilterWidget, self).__init__(parent)
        self._table1 = table1
        self._table2 = table2
        self._parameters = parameters
        self._init_gui()

    def _init_gui(self):
        vlayout = QtGui.QVBoxLayout()

        self._init_gui_from_input()

        self._filters_pwidget = (
            self._parameters['filter_functions'].gui())
        self._use_custom_predicate_pw = (
            self._parameters['use_custom_predicate'].gui())
        self._predicate_pwidget = (
            self._parameters['predicate_function'].gui())

        preview_button = QtGui.QPushButton("Preview")
        self._preview_text = QtGui.QTextEdit("")
        self._preview_text.setReadOnly(True)

        vlayout.addWidget(self._parameters['c0_column'].gui())
        vlayout.addWidget(self._parameters['c1_column'].gui())
        vlayout.addWidget(self._filters_pwidget)
        vlayout.addWidget(self._use_custom_predicate_pw)
        vlayout.addWidget(self._predicate_pwidget)
        vlayout.addWidget(preview_button)
        vlayout.addWidget(self._preview_text)

        self._post_init_gui_from_parameters()

        self.setLayout(vlayout)

        self._filters_pwidget.editor().currentIndexChanged[int].connect(
            self._filter_changed)
        self._use_custom_predicate_pw.stateChanged[int].connect(
            self._use_custom_predicate_changed)
        preview_button.clicked[bool].connect(
            self._preview_clicked)

    def _init_gui_from_input(self):
        def column_names(port):
            if port.is_valid():
                return port.column_names()
            else:
                return []

        self._parameters['c0_column'].list = column_names(self._table1)
        self._parameters['c1_column'].list = column_names(self._table2)

    def _post_init_gui_from_parameters(self):
        use_custom_predicate = (
            self._parameters['use_custom_predicate'].value)
        self._use_custom_predicate_changed()
        if not use_custom_predicate:
            self._filter_changed(
                self._parameters['filter_functions'].value[0])

    def _filter_changed(self, index):
        selected_filter_name = (
            self._parameters['filter_functions'].selected)
        self._predicate_pwidget.set_value(COLUMN_FILTERS[selected_filter_name])

    def _use_custom_predicate_changed(self):
        use_custom_predicate = (
            self._parameters['use_custom_predicate'].value)

        self._predicate_pwidget.setEnabled(use_custom_predicate)
        self._filters_pwidget.setEnabled(not use_custom_predicate)

    def _preview_clicked(self):
        selection = execute_filter_query(
            self._table1, self._table2, self._parameters)
        self._preview_text.setText(str(self._table2.to_dataframe()[selection]))


class ColumnFilterNode(synode.Node):
    __doc__ = join_doc(
        COMMON_DOCSTRING,
        """
        :Ref. nodes: :ref:`Select rows in Tables`
        """)

    name = 'Filter rows in Table'
    description = 'Filter column using Tables.'
    inputs = Ports([
        Port.Table('Table with column, C0, with reference values',
                   name='port0', requiresdata=True),
        Port.Table('Table with column, C1', name='port1', requiresdata=True)])
    outputs = Ports([Port.Table('Filtered Table', name='port0')])
    tags = Tags(Tag.DataProcessing.Select)

    author = 'Alexander Busck <alexander.busck@combine.se>'
    copyright = '(c) 2013 Combine Control Systems AB'
    nodeid = 'org.sysess.sympathy.filters.columnfilternode'
    version = '1.1'
    icon = 'filter.svg'

    parameters = synode.parameters()
    parameters.set_list(
        'c0_column', label='Select C0 column',
        description=('Select the column in Table1, upper port, to use as '
                     'reference column C0 in the comparison.'),
        editor=synode.Util.combo_editor(edit=True))
    parameters.set_list(
        'c1_column', label='Select C1 column',
        description=('Select the column in Table2, lower port, to use as '
                     'object column C1 in the comparison.'),
        editor=synode.Util.combo_editor(edit=True))
    parameters.set_list(
        'filter_functions', label='Select filter function',
        list=list(COLUMN_FILTERS.keys()),
        description='All available pre-defined filter functions.',
        editor=synode.Util.combo_editor())
    parameters.set_boolean(
        'use_custom_predicate', label='Use custom filter function',
        description='Use a custom filter (predicate) function to filter.')
    parameters.set_string(
        'predicate_function', label='Filter function',
        description='The predicate function to use when filtering.')

    def exec_parameter_view(self, node_context):
        table1 = node_context.input['port0']
        table2 = node_context.input['port1']
        parameters = node_context.parameters

        return ColumnFilterWidget(table1, table2, parameters)

    def execute(self, node_context):
        table1 = node_context.input['port0']
        table2 = node_context.input['port1']
        out_table = node_context.output['port0']
        parameters = node_context.parameters
        import warnings
        warnings.simplefilter('error', FutureWarning)

        selection = execute_filter_query(table1, table2, parameters)
        sliced_table = table2[selection]
        sliced_table.set_name(table2.get_name())
        sliced_table.set_table_attributes(table2.get_table_attributes())
        out_table.update(sliced_table)


ColumnFilterTables = node_helper.list_node_factory(
    ColumnFilterNode,
    ['port0', 'port1'], ['port0'],
    name='Filter rows in Tables',
    nodeid='org.sysess.sympathy.filters.columnfiltertables')
