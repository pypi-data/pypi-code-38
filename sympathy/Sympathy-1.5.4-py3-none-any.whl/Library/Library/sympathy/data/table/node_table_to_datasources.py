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
Convert a table with file paths to a list of data sources. The list will
contain one element for each row of the incoming table.

In the configuration GUI it is possible to select the column that contains the
file paths.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import os.path
from sympathy.api import node as synode
from sympathy.api import datasource as dsrc
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import sywarn
from sylib import datasource_conversion as dc


class SuperNode(synode.Node):
    author = 'Greger Cronquist <greger.cronquist@combine.se>'
    copyright = '(c) 2013, 2017 Combine Control Systems AB'
    version = '1.1'
    icon = 'table2dsrc.svg'

    outputs = Ports([Port.Datasources('Datasources')])

    parameters = synode.parameters()
    parameters.set_list(
        'files', label='File names',
        description='Column containing the filenames',
        editor=synode.Util.combo_editor(edit=True))
    parameters = dc.subflow_param(parameters)

    def verify_parameters(self, node_context):
        return node_context.parameters['files'].selected is not None

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['files'], node_context.input[0])


class TableToDsrc(SuperNode):
    """
    Export of data from Table to Datasources.

    :Ref. nodes: :ref:`Datasources to table`
    """

    name = 'Table to Datasources'
    description = ('Convert a table with file paths into a list of data '
                   'sources pointing to those files.')
    nodeid = 'org.sysess.sympathy.data.table.tabletodsrcs'
    tags = Tags(Tag.DataProcessing.Convert)

    inputs = Ports([Port.Table('Table containing a column of filepaths.')])

    def execute(self, node_context):
        filenames_col = node_context.parameters['files'].selected
        create_datasources(
            filenames_col, node_context.input[0], node_context.output[0],
            dc.flow_path(node_context.parameters['subpath']))


class TablesToDsrc(SuperNode):
    """
    Export of data from Table to Datasources.

    :Ref. nodes: :ref:`Datasources to table`
    """

    name = 'Tables to Datasources'
    description = ('Convert a list of tables with file paths into a list of '
                   'data sources pointing to those files.')
    nodeid = 'org.sysess.sympathy.data.table.tablestodsrcs'
    tags = Tags(Tag.DataProcessing.Convert)

    inputs = Ports([Port.Tables('Tables containing a column of filepaths.')])

    def execute(self, node_context):
        flow_path = dc.flow_path(node_context.parameters['subpath'])
        filenames_col = node_context.parameters['files'].selected
        for infile in node_context.input[0]:
            create_datasources(
                filenames_col, infile, node_context.output[0], flow_path)


def create_datasources(filenames_col, infile, outfile_list, flow_path):
    if filenames_col in infile:
        filenames = infile.get_column_to_array(filenames_col)
    else:
        sywarn('The selected column does not seem to exist. '
               'Assuming empty input.')
        filenames = []
    for f in filenames:
        outfile = dsrc.File()
        outfile.encode_path(_format_path(f, flow_path))
        outfile_list.append(outfile)


def _format_path(path, flow_path):
    if flow_path:
        return os.path.abspath(os.path.join(flow_path, path))
    else:
        return os.path.abspath(path)
