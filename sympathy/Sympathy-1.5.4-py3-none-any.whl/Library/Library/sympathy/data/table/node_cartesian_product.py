# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Combine Control Systems AB nor the
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
Cartesian product of a number of tables create a new table
containing all combinations of rows of the inputs. This output have
one column for each unique column in the input tables. For example two
tables with A and B columns of length N and M each create a new table
of length N * M and containing A + B columns. It is an error to have
duplicate column names.
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import SyDataError

import numpy as np

class CartesianProductTable(synode.Node):
    """
    Cartesian product of two or more Tables into a single Table.
    """
    name = 'Cartesian Product Table'
    description = 'Cartesian product of two or more Tables into a single Table.'
    nodeid = 'se.combine.sympathy.data.table.cartesian_product_table'
    author = "Mathias Broxvall <mathias.broxvall@combine.se>"
    copyright = "(C) 2017 Combine Control Systems AB"
    version = '1.0'
    icon = 'cartesian_product.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    parameters = {}
    parameter_root = synode.parameters(parameters)

    inputs = Ports([Port.Custom('table','Input Tables', name='in', n=(2, None)),])
    outputs = Ports([Port.Table(
        'Table with cartesian product of inputs', name='out')])

    def execute(self, node_context):
        """Execute"""
        inputs = node_context.input.group('in')
        output = node_context.output['out']
        lens = [len(i.cols()[0].data) for i in inputs]

        for i in range(len(list(inputs))):
            left = int(np.product(lens[:i]))
            right = int(np.product(lens[i+1:]))
            for column in inputs[i].cols():
                data = [val for val in column.data for _ in range(right)] * left
                output.set_column_from_array(column.name, np.array(data))

class CartesianProductTables(synode.Node):
    """
    Cartesian product a list of two or more Tables into a single Table.
    """
    name = 'Cartesian Product Tables'
    description = 'Cartesian product of a list  two or more Tables into a single Table.'
    nodeid = 'se.combine.sympathy.data.table.cartesian_product_tables'
    author = "Mathias Broxvall <mathias.broxvall@combine.se>"
    copyright = "(C) 2017 Combine Control Systems AB"
    version = '1.0'
    icon = 'cartesian_product.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    parameters = {}
    parameter_root = synode.parameters(parameters)

    inputs = Ports([Port.Custom('[table]','List of input tables', name='in')])
    outputs = Ports([Port.Table(
        'Table with cartesian product of inputs', name='out')])

    def execute(self, node_context):
        """Execute"""
        inputs = node_context.input['in']
        output = node_context.output['out']
        lens = [len(i.cols()[0].data) for i in inputs]

        for i in range(len(list(inputs))):
            left = int(np.product(lens[:i]))
            right = int(np.product(lens[i+1:]))
            for column in inputs[i].cols():
                data = [val for val in column.data for _ in range(right)] * left
                output.set_column_from_array(column.name, np.array(data))

