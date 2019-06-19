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
Table is the internal data type in Sympathy for Data representing a
two-dimensional data set. A Table consists of an arbitrary number of
columns, where all columns have the equal number of elements. Each column
has an unique header and a defined data type - all elements in a column
are of the same data type. In a Table, the columns are not bound to have
same data type, columns with different data types can be mixed in a Table.
The supported data types for the columns are the same as for numpy arrays,
with exception for the object type, np.object. Optional, an column can also
be given additional attributes, like unit or description.

This node uses plugins. Each supported file format has its own plugin. The
plugins have their own configurations which are reached by choosing among the
importers in the configuration GUI. The documentation for each plugin is
obtained by clicking at listed file formats below.

The node has an auto configuration which uses a validity check in the plugins
to detect and choose the proper plugin for the considered datasource. When
the node is executed in the auto mode the default settings for the plugins
will be used.

"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import os
from sylib.importer import base
from sympathy.api import node as synode
from sympathy.api import importers
from sympathy.api.nodeconfig import Port, Ports


def _output_item_filename_hook(output_item, filename):
    if not output_item.name:
        output_item.name = os.path.splitext(
            os.path.basename(filename))[0]


class ImportTable(base.ImportSingle, synode.Node):
    """
    Import Datasource as Table.

    :Configuration: See description for specific plugin
    :Opposite node: :ref:`Export Tables`
    :Ref. nodes: :ref:`Tables`

    For instructions on how to add or write custom plugins, see
    :ref:`pluginwriting`.
    """
    author = "Alexander Busck <alexander.busck@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.0'
    name = 'Table'
    description = 'Data source as a table'
    nodeid = 'org.sysess.sympathy.data.table.importtable'
    icon = 'import_table.svg'
    outputs = Ports([Port.Table('Imported Table', name='port1')])
    plugins = (importers.TableDataImporterBase, )

    def _output_item_filename_hook(self, output_item, filename):
        _output_item_filename_hook(output_item, filename)


class ImportTables(base.ImportMulti, synode.Node):
    """
    Import Datasources as Tables.

    :Configuration: See description for specific plugin
    :Opposite node: :ref:`Export Tables`
    :Ref. nodes: :ref:`Table`

    For instructions on how to add or write custom plugins, see
    :ref:`pluginwriting`.
    """
    author = "Alexander Busck <alexander.busck@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.0'
    name = 'Tables'
    description = 'Import datasources as Tables.'
    nodeid = 'org.sysess.sympathy.data.table.importtablemultiple'
    icon = 'import_table.svg'
    outputs = Ports([Port.Tables('Imported Tables', name='port1')])
    plugins = (importers.TableDataImporterBase, )

    def _output_item_filename_hook(self, output_item, filename):
        _output_item_filename_hook(output_item, filename)
