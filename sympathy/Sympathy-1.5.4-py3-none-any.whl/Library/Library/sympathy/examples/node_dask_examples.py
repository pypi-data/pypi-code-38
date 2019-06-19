# coding=utf-8
# Copyright (c) 2018 Combine Control Systems AB
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

import os
import contextlib
import dask.array as da
import numpy as np

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.nodeconfig import settings
from sympathy.api.exceptions import sywarn


@contextlib.contextmanager
def prefix_paths(paths):
    old_path = new_path = os.environ.get('PATH')
    if old_path:
        paths = paths + [old_path]
    paths = [path for path in paths if path]
    new_path = os.pathsep.join(paths)
    os.environ['PATH'] = new_path
    try:
        yield
    finally:
        if old_path is None:
            del os.environ['PATH']
        else:
            os.environ['PATH'] = old_path


class DaskStack(synode.Node):
    """
    This example shows a basic version of *VJoin Table*, implemented using
    dask.
    It requires the same columns to be present, and of the same type, in all
    inputs.

    Dask nodes have biggest effect in locked subflows and lambdas where
    data between nodes is passed in memory.

    :Ref. nodes: :ref:`VJoin Table`

    """
    name = 'Dask stack example'
    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C)2018 Combine Control Systems AB'
    version = '1.0'
    icon = 'example.svg'
    description = 'Node example demonstrating stacking tables using dask.'
    nodeid = 'org.sysess.sympathy.examples.daskstack'
    tags = Tags(Tag.Development.Example)

    inputs = Ports(
        [Port.Custom('table', 'Input Table', name='input', n=(2, None))])
    outputs = Ports(
        [Port.Table('Output Table', name='output')])

    def execute(self, node_context):
        tis = node_context.input.group('input')
        to = node_context.output['output']

        for col in tis[0].column_names():
            to.set_column_from_array(col, da.concatenate(
                [ti.get_column_to_array(col, kind='dask') for ti in tis]))


class DaskTail(synode.Node):
    """
    This example shows a basic version of tail, implemented using dask.
    Tail produces a new table similar to *Slice data Table* with
    *1:* as the slice expression.


    Dask nodes have biggest effect in locked subflows and lambdas where
    data between nodes is passed in memory.

    :Ref. nodes: :ref:`Slice data Table`
    """

    name = 'Dask tail example'
    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C)2018 Combine Control Systems AB'
    version = '1.0'
    icon = 'example.svg'
    description = 'Node example demonstrating the tail of a table using dask.'
    nodeid = 'org.sysess.sympathy.examples.dasktail'
    tags = Tags(Tag.Development.Example)

    inputs = Ports(
        [Port.Table('Input Table', name='input')])
    outputs = Ports(
        [Port.Table('Output Table', name='output')])

    def execute(self, node_context):
        ti = node_context.input['input']
        to = node_context.output['output']

        for col in ti.column_names():
            to.set_column_from_array(
                col,
                ti.get_column_to_array(col, kind='dask')[1:])


class DaskMax(synode.Node):
    """
    This example shows a basic table version of column-wise *max*,
    implemented using dask.

    Dask nodes have biggest effect in locked subflows and lambdas where
    data between nodes is passed in memory.
    """

    name = 'Dask max example'
    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C)2018 Combine Control Systems AB'
    version = '1.0'
    icon = 'example.svg'
    description = 'Node example demonstrating column-wise max using dask.'
    nodeid = 'org.sysess.sympathy.examples.daskmax'
    tags = Tags(Tag.Development.Example)

    inputs = Ports(
        [Port.Table('Input Table', name='input')])
    outputs = Ports(
        [Port.Table('Output Table', name='output')])

    def execute(self, node_context):
        ti = node_context.input['input']
        to = node_context.output['output']

        for col in ti.column_names():
            to.set_column_from_array(
                col, np.array(
                    [ti.get_column_to_array(
                        col, kind='dask').max().compute()]))


class DaskVisualize(synode.Node):
    """
    This example shows how to visualize a dask column graph as a image file
    written to disk.

    Output file format is selected by typing the desired file extension.
    .svg and .png are supported.

    This example requires `Graphviz <https://www.graphviz.org>`__
    to be installed and configured. Additionally the
    `graphviz <https://pypi.org/project/graphviz>`__ python package is also
    required, it can be installed by running::

        python -m pip install graphviz

    in the python environment that is used to run Sympathy.

    """
    name = 'Dask visualize example'
    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C)2018 Combine Control Systems AB'
    version = '1.0'
    icon = 'example.svg'
    description = 'Node example demonstrating graph visualization using dask.'
    nodeid = 'org.sysess.sympathy.examples.daskvisualize'
    tags = Tags(Tag.Development.Example)

    inputs = Ports(
        [Port.Table('Input Table', name='input_table')])
    outputs = Ports(
        [Port.Datasource(
            'Output Datasource', name='output_datasource', n=(0, 1, 0))])

    parameters = synode.parameters()
    parameters.set_string(
        'column', label='Column',
        description='Column to visualize.',
        editor=synode.editors.combo_editor())

    parameters.set_string(
        'filename', label='Filename',
        editor=synode.editors.savename_editor(['Any files (*)']),
        description=('Manually enter a filename (use .svg extensions to get '
                     'vector graphics)'))

    def execute(self, node_context):
        gviz_path = settings()['Debug/graphviz_path']
        ti = node_context.input['input_table']
        column = node_context.parameters['column'].value
        filename = os.path.abspath(
            node_context.parameters['filename'].value)
        data = ti.get_column_to_array(column, kind='dask')

        with prefix_paths([gviz_path]):
            try:
                data.visualize(filename)
            except Exception:
                sywarn(
                    'Make sure that Graphviz is installed and configured in '
                    'Sympathy.')
                raise

        if node_context.output.group('output_datasource'):
            node_context.output['output_datasource'].encode_path(filename)

    def adjust_parameters(self, node_context):
        """
        This method is called before configure. In this example it fills one of
        the list of selectable columns with column names from the input table.
        """
        adjust(node_context.parameters['column'],
               node_context.input['input_table'])
