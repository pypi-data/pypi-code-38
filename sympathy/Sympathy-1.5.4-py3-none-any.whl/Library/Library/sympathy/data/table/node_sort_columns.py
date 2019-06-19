# -*- coding: utf-8 -*-
# Copyright (c) 2015, 2017 Combine Control Systems AB
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
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import re
from sympathy.api import node
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags


def combined_key(string):
    """
    Alphanumeric key function.
    It computes the sorting key from string using the string and integer parts
    separately.
    """
    def to_int(string):
        try:
            return int(string)
        except ValueError:
            return string
    return [to_int(part) for part in re.split('([0-9]+)', string)]


class SortColumnsInTable(node.Node):
    """
    Sort the columns in incoming table alphabetically. Output table will have
    the same columns with the same data but ordered differently.
    """

    name = 'Sort columns in Table'
    author = 'Magnus Sandén <magnus.sanden@combine.se>'
    copyright = '(c) 2015, 2017 Combine Control Systems AB'
    version = '1.0'
    icon = 'sort_table_cols.svg'
    description = "Sort the columns in incoming table alphabeticaly."
    nodeid = 'org.sysess.sympathy.data.table.sortcolumns'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    inputs = Ports([
        Port.Table('Table with columns in unsorted order', name='input')])
    outputs = Ports([
        Port.Table('Table with columns in sorted order', name='output')])

    parameters = node.parameters()
    parameters.set_list(
        'sort_order', label='Sort order',
        list=['Ascending', 'Descending'], value=[0],
        description='Sort order',
        editor=node.Util.combo_editor())

    def execute(self, node_context):
        input_table = node_context.input['input']
        output_table = node_context.output['output']
        kwargs = {'reverse': node_context.parameters['sort_order'].selected ==
                  'Descending'}
        columns = sorted(
            input_table.column_names(), key=combined_key, **kwargs)

        for column in columns:
            output_table.set_column_from_array(
                column, input_table.get_column_to_array(column))
        output_table.set_attributes(input_table.get_attributes())
        output_table.set_name(input_table.get_name())
