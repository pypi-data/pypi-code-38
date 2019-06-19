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
import six
import os
import tempfile
import sys
import re

from sympathy.api import table
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, settings
from sympathy.api import exceptions

from sylib.old_calculator import calculator_model as models
from sylib.old_calculator import calculator_gui
from sylib.matlab import matlab
import sylib.calculator.plugins

FAILURE_STRATEGIES = OrderedDict([('Exception', 0), ('Skip calculation', 1)])
old_table_format = r'\${([^{}]+)}'
old_table_display = '${{{}}}'

TABLE_DOC = """
The Calculator nodes can perform calculation on Table(s). Accessing a column
can be done either by using the ${} notation (${signal}) or by the
:ref:`tableapi` (table.col('signal').data).

When the option *Put results in common outputs* is enabled (the default) each
input structure results in a single output table with all the new columns. This
means that all the calculated columns must be the same length. When disabled
each calculation instead generates a table with a single column. The length of
the outgoing list therefore depends on the number of incoming structures and
the number of operations that are applied to each structure. As an example, if
the incoming list consist of five tables and there are two calculations, the
number of tables in the outgoing list will be 5*2=10.

Note that the incoming columns don't propagate to the output table by default.
If the results of you calculations are of the same length as the input, and the
option *Put results in common outputs* is enabled you can use the node
:ref:`HJoin Tables` to add calculated results to the input table, or you can
simply use the option 'Copy input' to do this automatically.

Example calculations::

  New signal = ${Old signal} + 1
  area = ${width} * ${height}
  result = (${signal0} == 2) & ca.change_up(${signal1})
  index = np.arange(len(${some signal}))
  sine = np.sin(${angle})

The whole input table is available in the calculations as `table`. This allows
the entire :ref:`tableapi` to be used. For example you can get a list of a
table's column names::

  table_names = table.column_names()
"""


def add_same_length_res_parameter(parameters):
    parameters.set_boolean('same_length_res',
                           label='Put results in common outputs.',
                           value=True,
                           description=('Gather all the results generated '
                                        'from an incoming data into a '
                                        'common output table. This '
                                        'requires that the results all '
                                        'have the same length. An error '
                                        'will be given if the lengths of '
                                        'the outgoing results differ.'))


def add_base_parameters(parameters):
    parameters.set_list(
        'calc_list', label='List of calculations',
        description='List of calculations.')

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


def model_output_writer(infiles, calcs, outfiles, exception_handling,
                        same_length_res, copy_input=False):
    generic = False
    calc_list = []
    tmp_list = []
    for calc in calcs:
        name, calculation, enabled = models.parse_calc(calc)
        trimmed_name = models.trim_name(name)
        calc = calc.replace(name, trimmed_name, 1)
        tmp_list.append(models.format_calculation(calc, generic))
        calc_list.append(calc)

    calc_sorting, reverse_sorting = models.get_calculation_order(tmp_list)
    for i, infile in enumerate(infiles):
        try:
            if same_length_res:
                outfile = outfiles.create()
            if copy_input:
                outfile.source(infile)

            output_data = []
            enable = []
            for idx in calc_sorting:
                try:
                    output, enabled = models.python_calculator(
                        infile, calc_list[idx], dict(output_data), generic)
                    output_data.extend(output)
                    enable.append(enabled)
                except Exception:
                    if exception_handling == FAILURE_STRATEGIES['Exception']:
                        raise
                    enable.append(0)
                    output_data.append((None, None))

            for idx, calc_line in six.moves.zip(reverse_sorting, calc_list):
                calc_line = calc_line.split(models.ENABLED_SPLIT)[0].strip()
                name, calculation, enabled = models.parse_calc(calc_line)
                calc_line = calc_line.replace(
                    name, old_table_display.format(name), 1)
                if enable[idx] and len(output_data):
                    column, output = output_data[idx]
                    if not same_length_res:
                        outfile = outfiles.create()
                    outfile.set_column_from_array(column, output)
                    outfile.set_column_attributes(
                        column,
                        {'calculation': models.display_calculation(calc_line,
                         generic)})
                    if not same_length_res:
                        outfiles.append(outfile)

            if same_length_res:
                outfiles.append(outfile)
        except Exception:
            if isinstance(infiles, list):
                raise
            else:
                raise exceptions.SyListIndexError(i, sys.exc_info())
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

    def _exec_parameter_view(self, node_context, is_single_table):
        generic = False
        input_group = node_context.input.group('port0')
        input_data = table.File()
        if input_group:
            input_data = input_group[0]

        empty_input = False
        if not input_data.is_valid():
            empty_input = True
            if is_single_table:
                input_data = table.File()
            else:
                input_data = table.FileList()
        return calculator_gui.CalculatorWidget(
            input_data, node_context.parameters,
            backend='python', preview_calculator=models.python_calculator,
            generic=generic, multiple_input=not is_single_table,
            empty_input=empty_input)

    @staticmethod
    def _update_calc(parameters, infiles, outfiles, same_length_res):
        calc_list = parameters['calc_list'].list
        exception_handling = parameters['fail_strategy'].value[0]
        copy_input = parameters['copy_input'].value
        model_output_writer(infiles, calc_list, outfiles, exception_handling,
                            same_length_res, copy_input)


class CalculatorTableNode(SuperCalculator):
    __doc__ = TABLE_DOC
    name = 'Calculator Table'
    nodeid = 'org.sysess.sympathy.data.table.calculatortable'

    inputs = Ports([Port.Table('Input Table', name='port0')])
    outputs = Ports([Port.Table(
        'Table with results from the calculations.', name='port1')])

    def exec_parameter_view(self, node_context):
        return self._exec_parameter_view(node_context, True)

    def execute(self, node_context):
        out_list = table.FileList()
        self._update_calc(node_context.parameters,
                          [node_context.input['port0']], out_list,
                          True)
        node_context.output['port1'].update(out_list[0])


class CalculatorNode(SuperCalculator):
    __doc__ = TABLE_DOC
    name = 'Calculator Tables'
    nodeid = 'org.sysess.sympathy.data.table.calculator'

    inputs = Ports([Port.Tables('Input Tables', name='port0')])
    outputs = Ports([Port.Tables(
        'Tables with results from the calculations.', name='port1')])

    parameters = synode.parameters()
    add_base_parameters(parameters)
    add_same_length_res_parameter(parameters)

    def update_parameters(self, old_params):
        # Old nodes without the same_length_res option work the same way as if
        # they had the option, set to False.
        if 'same_length_res' not in old_params:
            add_same_length_res_parameter(old_params)
            old_params['same_length_res'].value = False

    def exec_parameter_view(self, node_context):
        return self._exec_parameter_view(node_context, False)

    def execute(self, node_context):
        self._update_calc(node_context.parameters, node_context.input['port0'],
                          node_context.output['port1'],
                          node_context.parameters['same_length_res'].value)


def mat_model_output_writer(
    infiles, calc_list, outfiles, exception_handling, same_length_res,
        copy_input=False):

    column_names = {'arg': infiles[0].column_names(), 'res': []}
    in_filenames = []
    out_filenames = []

    for in_table in infiles:
        in_matlab_name = matlab.allocate_mat_file()
        out_matlab_name = matlab.allocate_mat_file()
        in_filenames.append(in_matlab_name)
        out_filenames.append(out_matlab_name)
        matlab.write_table_to_matfile(in_table, in_matlab_name)
    try:
        matlab_code = generate_matlab_script(
            in_filenames, out_filenames, column_names, calc_list)
        _execute_matlab(matlab_code)
    except Exception:
        if exception_handling == FAILURE_STRATEGIES['Exception']:
            raise

    if len(column_names):
        write_to_file(
            out_filenames, outfiles, calc_list, infiles,
            same_length_res, copy_input)


def generate_matlab_script(input_filenames, output_filenames,
                           old_col_names, calc_list, extra_globals=None):
    """Generates the script to be run in Matlab based on GUI calculations."""
    if extra_globals is None:
        extra_globals = dict([])
    old_col_names['res'].extend(list(extra_globals.keys()))
    full_path = os.path.realpath(__file__)
    dir_path = os.path.split(full_path)[0]
    matlib = os.path.abspath(os.path.join(
        dir_path, './../../../../../Sympathy/Matlab'))

    m_script = "try\n"
    for in_file, out_file in zip(input_filenames, output_filenames):
        m_script += (
            "infilename = '{0}';\n" +
            "outfilename = '{1}';\n" +
            "addpath('{2}');\n" +
            "in = load(infilename);\n").format(in_file, out_file, matlib)

        m_script += (
            "out = struct;\n" +
            "out.table_attr = in.table_attr;\n" +
            "out.col_attr = {};\n" +
            "out.col_attr_values = {};\n")
        index = 1
        col_names = []
        func_calls = []
        outputs = []
        enable = []
        for calc_text in calc_list:
            var_name, calc, enabled = (
                models.get_varname_and_calc_and_enabled(calc_text))
            col_name, func_call, output = models.line_parser(
                var_name, calc, old_col_names)
            enable.append(enabled)
            if len(col_name) and len(func_call) and len(output):
                col_names.append(col_name)
                func_calls.append(func_call[0])
                outputs.append(output[0])

        array = '(' + "".join(["'{}', ".format(val)
                               for val in outputs])[:-2] + ')'
        m_string = "outputs = char{};\n".format(array)
        m_script += m_string
        for old_name, func, col_name in zip(col_names, func_calls, outputs):
            for i, name in enumerate(old_name):
                m_script += (
                    "i = strmatch('{1}',in.names);\n"
                    "if length(i) > 1;\n" +
                    "for j = 1:length(i);\n" +
                    "if size(j) == size('{1}');\n" +
                    "i = j;\n"
                    "continue;\n"
                    "end;\n" +
                    "end;\n" +
                    "end;\n" +
                    "if length(in.col_attr);\n" +
                    "try\n" +
                    "string = cellstr(in.col_attr(i));\n" +
                    "out.col_attr({2}) = string;\n" +
                    "string = cellstr(in.col_attr_values(i));\n" +
                    "out.col_attr_values({2}) = " +
                    "string;\n" +
                    "catch err\n" +
                    "out.col_attr({2}) = in.col_attr(i) ;\n" +
                    "out.col_attr_values({2}) = in.col_attr_values(i);\n" +
                    "end;\n" +
                    "end;\n" +
                    "{0} = in.col(i, :);\n").format(
                        old_name[name], name, index)

            m_script += "output = calc(\'{0}\');\n".format(func)
            m_script += ("out.col({0}, :) = output;\n"
                         "out.names({0}, :) = outputs({0}, :);\n"
                         ).format(index)
            index += 1

        if not zip(col_names, func_calls, outputs):
            for func, col_name in zip(func_calls, outputs):
                m_script += "output = calc('int32({0})');\n".format(func)
                m_script += ("out.col({0}, :) = output;\n"
                             "out.names({0}, :) = outputs({0}, :);\n"
                             ).format(index)
            index += 1
        m_script += ("% Write everything to file \n" +
                     "save(outfilename, '-struct', 'out'); \n")
    m_script += (
        'quit;\n' +
        'catch err \n' +
        'err \n' +
        'quit;\n' +
        'end\n')
    return m_script


def write_to_file(mat_files, outfiles, calc_list, infiles,
                  same_length_res, copy_input):
    calc_sorting, reverse_sorting = models.get_calculation_order(calc_list)
    for i, (mat_file, infile) in enumerate(zip(mat_files, infiles)):
        mat_table = matlab.read_matfile_to_table(mat_file)
        try:

            names = mat_table.column_names()
            if same_length_res:
                outfile = outfiles.create()
            if copy_input:
                outfile.source(infile)

            for idx, calc_line, column in six.moves.zip(
                    reverse_sorting, calc_list, names):
                calc_line = calc_line.split(
                    models.ENABLED_SPLIT)[0].strip()
                output = mat_table.get_column_to_array(column)
                if not same_length_res:
                    outfile = outfiles.create()
                outfile.set_column_from_array(column, output)
                outfile.set_column_attributes(
                    column, {'calculation': calc_line})
                if not same_length_res:
                    outfiles.append(outfile)

            if same_length_res:
                outfiles.append(outfile)
        except Exception:
            raise exceptions.SyListIndexError(i, sys.exc_info())


def _execute_matlab(script):
    """Run the m-script in MATLAB"""
    with tempfile.NamedTemporaryFile(
            prefix='node_matlab_calculator_', suffix='.m', delete=False,
            dir=settings()['session_folder']) as script_file:
        script_file.write(six.binary_type(script.encode('utf8')))
        script_file.flush()

    matlab.execute_matlab("run('{0}'); quit;".format(script_file.name))


class MatlabCalculator(SuperCalculator):
    """With this node one can apply simple operations on the content
    of Tables. The node has the same structure as the :ref:`Calculator`
    node with the difference that Matlab is used as scripting engine instead
    of Python, and that intermediary calculations can not be used.
    """

    name = 'Matlab Calculator'
    description = 'Performs user-defined Matlab calculations'
    author = ("Greger Cronquist <greger.cronquist@combine.se, "
              "Sara Gustafzelius <sara.gustafzelius@combine.se>")
    nodeid = 'org.sysess.sympathy.matlab.matlabcalculator'
    version = '1.0'
    icon = 'matlab_calculator.svg'
    plugins = (sylib.calculator.plugins.MatlabCalcPlugin, )

    inputs = Ports([Port.Tables('Input Table', name='port0')])
    outputs = Ports([Port.Tables(
        'Table applied with MATLAB functions', name='port1')])

    def exec_parameter_view(self, node_context):
        input_data = node_context.input['port0']
        if not input_data.is_valid():
            input_data = table.FileList()
        return calculator_gui.CalculatorWidget(
            input_data, node_context.parameters, backend='matlab')

    def update_parameters(self, old_params):
        # Old nodes without the same_length_res option work the same way as if
        # they had the option, set to False.
        if 'same_length_res' not in old_params:
            add_same_length_res_parameter(self.parameters)
            old_params['same_length_res'] = self.parameters['same_length_res']
            old_params['same_length_res'].value = False
        old_calcs = old_params['calc_list'].list
        calcs = []
        names = []
        for calc in old_calcs:
            ekv = calc.split("=", 1)
            name = re.findall(old_table_format, ekv[0])
            if name:
                names.append(name[0])

        for calc in old_calcs:
            var_names = re.findall(models.var_string, calc)
            post_names = re.findall(models.var_string +
                                    models.table_format_regex, calc)

            for i in range(0, len(post_names)):
                var = var_names[i].replace('table', 'arg')
                calc = calc.replace(
                    models.formatted_table.format(var_names[i], post_names[i]),
                    models.formatted_table.format(var, post_names[i]))

            ekv = calc.split("=", 1)
            left_side = ekv[0]
            right_side = ekv[1]
            columns = re.findall(old_table_format, right_side)
            name = re.findall(old_table_format, left_side)
            if name:
                left_side = name[0]
            for col in columns:
                var = "arg"
                if col in names and col != left_side:
                    var = "res"
                right_side = right_side.replace(
                    old_table_display.format(col),
                    models.formatted_table.format(var, col))

            calcs.append(left_side.strip() + " = " + right_side.strip())
        old_params['calc_list'].list = calcs

    def execute(self, node_context):
        calc_list = node_context.parameters['calc_list'].list
        if (not len(calc_list) or not len(node_context.input['port0']) or not
                models.parse_calc(calc_list[0])[1].strip()):
            return
        mat_model_output_writer(
            node_context.input['port0'],
            calc_list,
            node_context.output['port1'],
            node_context.parameters['fail_strategy'].value[0],
            node_context.parameters['same_length_res'].value,
            node_context.parameters['copy_input'].value)
