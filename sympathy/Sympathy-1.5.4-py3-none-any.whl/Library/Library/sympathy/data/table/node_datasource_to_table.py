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
In the standard library there exist two nodes which exports data from
:ref:`Datasource` to :ref:`Table`. The outgoing :ref:`Table` will consist
of a single column with filepaths. The length of the column will be equal
to the incoming number of datasources.

In the configuration GUI it is possible to select if one wants to convert
the paths in the Datasources to absolute filepaths.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import os.path
import numpy as np
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sylib import datasource_conversion as dc


class SuperNode(synode.Node):
    author = "Magnus Sanden <magnus.sanden@combine.se>"
    copyright = "(c) 2013, 2017, Combine Control Systems AB"
    version = "1.1"
    icon = "dsrc2table.svg"
    tags = Tags(Tag.DataProcessing.Convert)

    outputs = Ports(
        [Port.Table("Table with a single column with a filepath", name="out")])

    parameters = synode.parameters()
    parameters = dc.topflow_param(parameters)
    parameters = dc.subflow_param(parameters)
    controllers = (
        synode.controller(
            when=synode.field('relpath', state='checked'),
            action=(
                synode.field('subpath', state='disabled'),
            ),
        ),
        synode.controller(
            when=synode.field('subpath', state='checked'),
            action=(
                synode.field('relpath', state='disabled'),
            ),
        ),
    )


class DsrcToTable(SuperNode):
    """Export of data from Datasource to Table.

    :Ref. nodes: :ref:`Datasources to Table`
    """

    name = "Datasource to Table"
    description = ("Convert a single data source into a table containing that "
                   "filename.")
    nodeid = "org.sysess.sympathy.data.table.dsrctotable"

    inputs = Ports(
        [Port.Datasource("Datasource with filepaths", name="in")])

    def execute(self, node_context):
        flow_path = dc.flow_path(node_context.parameters['subpath'])

        filepath = []
        if node_context.input['in'].decode_path() is not None:
            filepath = [_format_path(
                node_context.input['in'].decode_path(),
                node_context.parameters['relpath'].value,
                flow_path)]
        node_context.output['out'].set_column_from_array(
            'filepaths', np.array(filepath, dtype='U'))


class DsrcsToTable(SuperNode):
    """Export of data from Datasources to Tables.

    :Ref. nodes: :ref:`Datasource to Table`
    """

    name = "Datasources to Table"
    description = "Converts a list of data sources into a table of filenames."
    nodeid = "org.sysess.sympathy.data.table.dsrcstotable"

    inputs = Ports(
        [Port.Datasources("Datasources with filepaths", name="in")])

    def execute(self, node_context):
        flow_path = dc.flow_path(node_context.parameters['subpath'])

        filepaths = []
        for infile in node_context.input['in']:
            filepath = _format_path(
                infile.decode_path(),
                node_context.parameters['relpath'].value,
                flow_path)
            filepaths.append(filepath)
        node_context.output['out'].set_column_from_array(
            'filepaths', np.array(filepaths, dtype='U'))


def _format_path(path, relpath, flow_path):
    if flow_path:
        return os.path.relpath(path, flow_path)
    elif relpath:
        return os.path.relpath(path)
    return os.path.abspath(path)
