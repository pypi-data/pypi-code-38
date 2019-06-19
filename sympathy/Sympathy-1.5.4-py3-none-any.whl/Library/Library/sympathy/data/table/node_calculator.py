# coding=utf-8
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
The calculator node can apply calculations on each data column in a list.
The calculations are written as Python code and can consist of simple
arithmetic calculations, Python function calls, or calls to functions defined
in plugins.

Calculations
^^^^^^^^^^^^
You declare each calculation by typing a name in the text line labeled *Signal
name* and entering the calculation in the textfield labeled *Calculation*. You
can use any of the signals in the list *Signal names* in your calculation.

To use a signal from an incoming table type simply drag-and-drop the signal
name from the list of available signals to the calculation field.
To use a signal from the incoming generic data use *arg* in a way that fits the
data format as can be seen below:

To add a function, drag-and-drop it from the *Avaliable functions* tree
structure. Note that any signal that you reference in the calculation must
exist in all incoming data structures.

To add a new calculation, press the *New* button and the *Calculation* field as
well as *Signal name* will be cleared. If you want to edit a calculation
simply click on the calculation in the *List of calculations*. The signal name
will then appear under *Signal name* and the calculation will appear in the
*Calculation* field. The calculation will be updated in the *Calculation*
field, *List of calculations* and preview simultaneously. To remove a
calculation, mark a calculation in *List of calculations* and press the
*Remove* button. The result of your calculation is written to a column in an
outgoing table.

If something goes wrong when you define the calculations you will get an error
or warning message in the preview window and at the top of the window.

Some commonly used operators and functions can be found under the function tree
structure (labeled *Common functions*) and can be added to a calculation by
double-clicking or dragging the function name to the calculation area. If you
want more information about a function, hover its name and its documentation
will appear as a tooltip.

The signals that you access in the calculations are returned as numpy arrays,
the same as if you had called :meth:`get_column_to_array` from the
:ref:`tableapi`. This means that simple arithmetics and the functions from
numpy and pandas work out of the box. But if you want to apply some other
function which only works on a single element of the column you may need to use
Python list comprehensions. For (the contrived) example::

  filenames = np.array([value + value for value in signal])

where signal is a table column.

Calculation Attributes
^^^^^^^^^^^^^^^^^^^^^^
Each calculation can have any number of custom associated attributes.  These
are, at least for now, much more limited than calculations.  Each attribute has
a string for its name and another string for its value and both are treated as
text and are not evaluated as python expressions. The use for these is being
able to associate metadata to output columns created by calculations. For
example:

+------+-------+
| Name | Value |
+======+=======+
| unit |  ms   |
+------+-------+

will attach milliseconds for unit to a specific column.


Output
^^^^^^
Each column of the output will have a *calculation* attribute with a string
representation of the calculation used to create that column.

In the configuration, there is an option on how to handle exceptions
(Action on calculation failure) produced by the node, for example missing
signals or erroneous calculations.

In the list of calculations there is also the option to disable individual
calculations, i.e., exclude them from the output. This makes it possible to
make intermediary calculations that does not have the same lengths as the
the calculations that are actually output by the node. This could for example
be useful for constants.

Compatibility
^^^^^^^^^^^^^
Under python 2 the calculations are evaluated with future imports ``division``
and ``unicode_literals`` activated. This means that in both python 2 and python
3 the calculation `1/2` will give 0.5 as result, and the calculation `'hello'`
will result in a unicode-aware text object (`unicode` in python 2 and `str` in
python 3). To get floor division use the operator ``//`` and to get a binary
string (`str` in python 2 and `bytes` in python 3) use the syntax ``b'hello'``.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from collections import OrderedDict
import sys
import json

from sympathy.types import types
from sympathy.api import table
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import exceptions

from sylib.calculator import calculator_model as models
from sylib.calculator import calculator_gui
import sylib.calculator.plugins

FAILURE_STRATEGIES = OrderedDict([('Exception', 0), ('Skip calculation', 1)])

GENERIC_DOC = """
The Calculator nodes can perform calculations on any given input. Any type can
by used as input and it is accessed by the keyword *arg*.

These nodes do not support the ${} notation of older :ref:`Calculator Table`
nodes.

Tuples can be used either with the same datatypes e.g.,
(:ref:`Table`, :ref:`Table`), (:ref:`ADAF`, :ref:`ADAF`, :ref:`ADAF`),
etc, or with different datatypes e.g., (:ref:`Table`, :ref:`ADAF`),
(:ref:`ADAF`, :ref:`ADAFs`, :ref:`Tables`). Any combination is possible.
The items in a tuple are accessed by index,
like so: ``arg[0]``, ``arg[1]``, etc.

Calculated signals can be accessed with the *res* keyword in the same way.

Some examples::

    - Table         - ``arg.col('signal1').data``
    - Tables        - ``arg[0].col('signal1').data``
    - ADAF          - ``arg.sys['system0']['raster0']['signal0'].y``
                       for signal values and
                      ``arg.sys['system0']['raster0']['signal0'].t`` for the
                      timeseries
    - ADAFs         - ``arg[0].sys['system0']['raster0']['signal0'].y`` for
                      signal values and
                      ``arg[0].sys['system0']['raster0']['signal0'].t`` for the
                      timeseries
    - Text          - ``arg.dtext`` for the text
    - Texts         - ``arg[0].dtext`` for the text
    - Datasource    - ``arg`` for Datasource object
    - Datasources   - ``arg[0]`` for Datasource in Datasources
    - Tuple         - Objects are accessed as ``arg[0]``, ``arg[1]``, ...


Example calculations::

  New signal = arg.col('Old signal').data + 1
  area = arg.col('width').data * arg.col('height').data
  result = (arg.col('signal0').data == 2) &
            ca.change_up(arg.col('signal1).data)
  index = np.arange(len(arg.col('some signal').data))
  sine = np.sin(arg.col('angle').data)

The API of the incoming :ref:`data type<datatypeapis>` can be used in the
calculator. For example you can use :ref:`tableapi` to get a list of a table's
column names::

  table_names = arg.column_names()

Note that a dependency on a column is only created when a string literal is
used, for example, ``arg.col('signal_name').data``. Iterating through a
table's columns, like np.array([arg.col(name) for name in arg.column_names()]),
does not. In the first expression, if 'signal_name' is missing, the node
will fail with an error. The second one will run even if there are no columns
in the input.
"""


def add_base_parameters(parameters):
    parameters.set_list(
        'calc_list', label='List of calculations',
        description='List of calculations.')

    parameters.set_string(
        'calc_attrs_dict',
        value='[]',
        description='Calculation attributes as json dict-list-string!')

    parameters.set_boolean(
        'copy_input', value=False, label='Copy input',
        description=('If enabled the incoming data will be copied to the '
                     'output before running the calculations. This requires '
                     'that the results will all have the same length. An '
                     'exception will be raised if the lengths of the outgoing '
                     'results differ.'))
    parameters.set_list(
        'fail_strategy', label='Action on calculation failure',
        list=FAILURE_STRATEGIES.keys(), value=[0],
        description='Decide how a failed calculation should be handled',
        editor=synode.Util.combo_editor())


def model_output_writer(input_files, calc_lines, output_files,
                        exception_handling, copy_input=False, attributes=None):

    attributes = attributes or {}
    calc_nodes = models.parse_nodes(calc_lines)
    graph = models.CalculationGraph(calc_nodes)
    calculation_order = graph.topological_sort(calc_nodes)
    calc_map = OrderedDict()

    for calc in graph.nodes():
        calc_map[calc.name] = calc

    calc_outputs = [calc for calc in calc_nodes if calc.enabled]
    calc_indices = dict(zip(calc_nodes, range(len(calc_nodes))))

    skip = exception_handling != FAILURE_STRATEGIES['Exception']

    for i, input_file in enumerate(input_files):

        try:
            output_file = output_files.create()
            if copy_input:
                if isinstance(input_file, table.File):
                    output_file.source(input_file)

            res = models.ResTable()
            models.execute_calcs(
                graph, calculation_order, input_file, res, skip)

            for calc in calc_outputs:
                name = calc.name

                if name in res:
                    output = res[name]
                    output_file.set_column_from_array(name, output)
                    col_attributes = attributes.get(calc_indices[calc], [])
                    col_attributes.append(
                        ('calculation',
                         models.display_calculation(str(calc))))

                    output_file.set_column_attributes(
                        models.display_calculation(name), dict(col_attributes))

            output_files.append(output_file)

        except Exception as e:
            if exception_handling == FAILURE_STRATEGIES['Exception']:
                if isinstance(input_files, list):
                    raise
                else:
                    raise exceptions.SyListIndexError(i, sys.exc_info())
            else:
                exceptions.sywarn('Error occurred in table number ' + str(i))


class SuperCalculator(synode.Node):
    author = ('Greger Cronquist <greger.cronquist@combine.se>, '
              'Magnus Sandén <magnus.sanden@combine.se>, '
              'Sara Gustafzelius <sara.gustafzelius@combine.se>, '
              'Benedikt Ziegler <benedikt.ziegler@combine.se>')
    description = 'Performs user-defined python calculations'
    copyright = '(c) 2016 Combine Control Systems AB'
    version = '3.0'
    icon = 'calculator.svg'
    tags = Tags(Tag.DataProcessing.Calculate)
    plugins = (sylib.calculator.plugins.ICalcPlugin, )

    parameters = synode.parameters()
    add_base_parameters(parameters)

    def _exec_parameter_view(self, node_context, is_single_input):
        input_group = node_context.input.group('port0')
        input_data = table.File()
        if input_group:
            input_data = input_group[0]

        show_copy_input = False

        for port in node_context.definition['ports']['inputs']:
            if port['name'] == 'port0':
                port_type = types.from_string(port['type'])
                if not is_single_input:
                    port_type = port_type[0]

                show_copy_input = types.match(
                    types.from_string(port_type, False),
                    types.from_string('table'))

        empty_input = False
        if not input_data.is_valid():
            empty_input = True
            if is_single_input:
                input_data = table.File()
            else:
                input_data = table.FileList()
        return calculator_gui.CalculatorWidget(
            input_data, node_context.parameters,
            preview_calculator=models.python_calculator,
            multiple_input=not is_single_input,
            empty_input=empty_input,
            show_copy_input=show_copy_input)

    @staticmethod
    def _update_calc(parameters, infiles, outfiles):
        calc_list = parameters['calc_list'].list
        exception_handling = parameters['fail_strategy'].value[0]
        copy_input = parameters['copy_input'].value

        calc_attrs_dict = dict(json.loads(
            parameters['calc_attrs_dict'].value or '[]'))

        model_output_writer(infiles, calc_list, outfiles, exception_handling,
                            copy_input, calc_attrs_dict)


class CalculatorGenericNode(SuperCalculator):
    __doc__ = GENERIC_DOC
    name = 'Calculator'
    nodeid = 'org.sysess.sympathy.data.table.calculatorgeneric'

    inputs = Ports([Port.Custom('<a>', 'Generic Input', name='port0',
                                n=(0, 1, 1))])
    outputs = Ports([Port.Table(
        'Table with results from the calculations.', name='port1')])

    def exec_parameter_view(self, node_context):
        return self._exec_parameter_view(node_context, True)

    def execute(self, node_context):
        input_group = node_context.input.group('port0')
        input_data = table.File()
        if input_group:
            input_data = input_group[0]

        out_list = table.FileList()
        self._update_calc(node_context.parameters,
                          [input_data], out_list)
        node_context.output['port1'].source(out_list[0])


class CalculatorGenericListNode(SuperCalculator):
    __doc__ = GENERIC_DOC
    name = 'Calculator List'
    nodeid = 'org.sysess.sympathy.data.table.calculatorgenericlist'
    inputs = Ports([Port.Custom('[<a>]', 'Generic Input', name='port0')])
    outputs = Ports([Port.Tables(
        'Tables with results from the calculations.', name='port1')])

    def exec_parameter_view(self, node_context):
        return self._exec_parameter_view(node_context, False)

    def execute(self, node_context):
        self._update_calc(node_context.parameters, node_context.input['port0'],
                          node_context.output['port1'])
