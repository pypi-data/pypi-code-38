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
Similar to the function selector, :ref:`F(x)`, one can with this
node apply non-general functions/scripts to the content of Tables.
The difference is that this node uses Matlab as scripting engine
instead of Python. Another difference is that the Python file coming in to
the function selector includes one or many selectable functions, which is
not the case for this node. Here, the Matlab file only consists of a single
written script.

In the Matlab script one reaches the table data in the Table with the arg
variable
::

    in_data = arg

and sets the output in the res variable:
::

    res = out_data

A small example of how to access the input and output data:
::

    names = arg.column_names();
    price = names(1, :);
    price_value = arg.get_column_to_array(price);

    out_table = Table();
    out_table = out_table.set_column_from_array(...
        'MAX_PRICE',  max(price_value), [[], []]);
    out_table = out_table.set_column_from_array(...
        'MIN_PRICE',  min(price_value), [[], []]);
    out_table = out_table.set_table_attributes([]);
    res = out_table;


Some executable examples are located in Sympathy/Matlab/Examples.

See :ref:`Matlab API<matlabapi>` for all functions that can be used on the
input/output table(s).
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import os
import six

from sylib.matlab import matlab
from sympathy.api import node as synode
from sympathy.api.exceptions import NoDataError
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags


class SuperNode(synode.Node):
    author = "Sara Gustafzelius <sara.gustafzelius@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.0'
    description = 'Execute Matlab code'
    icon = 'matlab_fx.svg'
    tags = Tags(Tag.DataProcessing.Calculate)

    def run(self, input_table, output_table, input_script):
        """
        Creates temporary .mat files, writes input data to .mat files,
        runs the matlab script and then reads the output data from .mat file
        and writes it to output.
        """
        script = os.path.abspath(six.text_type(input_script.decode_path()))
        in_tmp_file_name = matlab.allocate_mat_file()
        out_tmp_file_name = matlab.allocate_mat_file()

        matlab.write_table_to_matfile(input_table, in_tmp_file_name)
        run_matlab_script(in_tmp_file_name, out_tmp_file_name, script)
        mat_table = matlab.read_matfile_to_table(out_tmp_file_name)
        self.add_output(mat_table, output_table)


class MatlabTables(SuperNode):
    name = 'Matlab Tables'
    nodeid = 'org.sysess.sympathy.data.table.matlabtables'
    inputs = Ports([Port.Datasource('M-file (.m)', name='port2',
                                    requiresdata=True),
                    Port.Tables('Input Tables', name='port0')])
    outputs = Ports([Port.Tables(
        'Tables with MATLAB script applied', name='port1')])

    def execute(self, node_context):
        input_tables = node_context.input['port0']
        output_tables = node_context.output['port1']
        input_script = node_context.input['port2']
        if input_tables is None:
            raise NoDataError(
                "Can't run calculation when empty input data is connected")

        for input_table in input_tables:
            self.run(input_table, output_tables, input_script)

    def add_output(self, mat_table, output_tables):
        output_tables.append(mat_table)


class MatlabTable(SuperNode):
    author = ("Alexander Busck <alexander.busck@combine.se>, "
              "Sara Gustafzelius <sara.gustafzelius@combine.se>")
    name = 'Matlab Table'
    nodeid = 'org.sysess.sympathy.data.table.matlabtable'

    inputs = Ports([Port.Datasource('M-file (.m)', name='port2',
                                    requiresdata=True),
                    Port.Table('Input Table', name='port0')])
    outputs = Ports([Port.Table(
        'Table with MATLAB script applied', name='port1')])

    def execute(self, node_context):
        input_table = node_context.input['port0']
        output_table = node_context.output['port1']
        input_script = node_context.input['port2']
        if input_table is None:
            raise NoDataError(
                "Can't run calculation when empty input data is connected")

        self.run(input_table, output_table, input_script)

    def add_output(self, mat_table, output_table):
        output_table.update(mat_table)


def run_matlab_script(infile, outfile, script):
    code = (
        "cd('{}');"
        "try "
        "arg = Table();"
        "res = Table();"
        "arg = arg.from_file('{}');"
        "run('{}');"
        "res.to_file('{}');"
        "quit;"
        "catch err "
        "quit;"
        "end;").format(os.path.dirname(script), infile, script, outfile)
    matlab.execute_matlab(code)
