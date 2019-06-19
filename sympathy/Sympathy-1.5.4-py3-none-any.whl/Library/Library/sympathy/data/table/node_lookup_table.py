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
The lookup node takes rows from a lookup table (upper port) in the order
defined by a control table (lower port).

In the gui you can define pairs of columns, one from the control table and one
from the lookup table. During the execution of the node, it will step through
the rows of the selected control columns and try to find a match among the rows
in the corresponding columns in the lookup table. If there is a match, that
entire row in the lookup table is copied to the output.

Since there is one row in the output for each row in the control table, the
output from this node should always be possible to :ref:`hjoin <Hjoin Table>`
with the control table. This is often a useful first step for using the output
from this node.

Rows not found lookup table
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The behavior when some rows in the control table can not be found in the lookup
table depends on the state of the two checkboxes below the table with column
pairs: *Require perfect match* and *Use zero-like value instead of
masks*. By default both boxes are unchecked which means that any rows that can
not be found in the lookup table are masked in the output.

If *Use zero-like values instead of masks* is checked, unmatched rows are
instead assigned appropriate zero-like values depending on the data type
of the columns.

Examples of zero-like values for different column types:

    :float: 0.0
    :integer: 0
    :bool: False
    :text: ""

This setting is mostly for backwards compatibility and is
therefore not recommended for new flows.

If *Require perfect match* is checked an exception will be raised if row can
not be matched. So with this setting all rows in the control table must be
matched if the node is to execute successfully. This can be useful to avoid
trickier errors in later nodes.

Using an event column
~~~~~~~~~~~~~~~~~~~~~
In the configuration GUI you can also choose to treat one of the defined column
pairs as event columns. The event columns will typically consist of dates or
times. But can actually be of any sortable data type. Only one event column
pair can be chosen at a time.

When an event column pair has been defined, the matching is performed in a
slightly different way. Each row in this control table will now be matched with
the last preceding event in the lookup table which also matches in all other
column pairs. This means that an entry in the event column of the control table
doesn't have to have an exact match in the lookup table for there to be a
match. It is enough that there is any preceding event.

"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags

from sylib.lookup_gui import LookupWidget
from sylib.lookup import apply_index_datacolumn_and_write_to_file


def _add_new_lookup_parameters(parameters):
    parameters.set_boolean(
        'nomasks', value=False,
        label='Use zero-like values instead of masks',
        description='When unchecked rows that can not be matched '
                    'will be masked. When checked such rows are instead '
                    'assigned 0, 0.0, False, "", etc. depending on the type '
                    'of the value column.')


class LookupDefinition(object):
    description = ("Take rows from the lookup table in the "
                   "order defined by the control table.")
    author = ("Alexander Busck <alexander.busck@combine.se>, "
              "Magnus Sanden <magnus.sanden@combine.se>")
    copyright = "(C)2013 Combine Control Systems AB"
    version = "1.0"
    icon = "lookup.svg"

    parameters = synode.parameters()
    parameters.set_list(
        'template_columns', label='Lookup columns', value=[],
        description=('A list storing columns in the lookup table '
                     'used for matching. At each index there is '
                     'a corresponding entry in lookupee_columns.'))
    parameters.set_list(
        'lookupee_columns', label='Control columns', value=[],
        description=('A list storing columns in the control table '
                     'used for matching. At each index there is '
                     'a corresponding entry in template_columns.'))
    parameters.set_integer(
        'event_column', label='Event column', value=-1,
        description='Stores the index of the column pair which is '
                    'to be matched as events, or -1 if no such column '
                    'pair has been selected.')
    parameters.set_boolean(
        'perfect_match', value=False, label='Require perfect match',
        description=("If checked, each row in the control table has "
                     "to match exactly one row in the lookup table."))
    _add_new_lookup_parameters(parameters)

    def update_parameters(self, old_params):
        if 'nomasks' not in old_params:
            _add_new_lookup_parameters(old_params)
            old_params['nomasks'].value = True


def get_files(node_context):
    try:
        lookup_file = node_context.input['lookup']
    except KeyError:
        lookup_file = None
    try:
        lookupee_file = node_context.input['lookupee']
    except KeyError:
        lookupee_file = None
    try:
        out_file = node_context.output['out']
    except KeyError:
        out_file = None
    return lookup_file, lookupee_file, out_file


class LookupTableNode(LookupDefinition, synode.Node):
    name = "Lookup Table"
    nodeid = "org.sysess.sympathy.data.table.lookuptable"
    tags = Tags(Tag.DataProcessing.TransformStructure)

    inputs = Ports([
        Port.Table("Lookup table", name="lookup"),
        Port.Table("Control table", name="lookupee")])
    outputs = Ports([
        Port.Table("Result table", name="out")])

    def exec_parameter_view(self, node_context):
        lookup_file, lookupee_file, out_file = get_files(node_context)
        return LookupWidget(
            node_context.parameters, lookup_file, lookupee_file, out_file)

    def execute(self, node_context):
        lookup_file, lookupee_file, out_file = get_files(node_context)

        apply_index_datacolumn_and_write_to_file(
            node_context.parameters, lookup_file, lookupee_file, out_file)
        out_file.set_attributes(lookup_file.get_attributes())


LookupTablesNode = node_helper.list_node_factory(
    LookupTableNode,
    ['lookupee'], ['out'],
    name="Lookup Tables",
    nodeid="org.sysess.sympathy.data.table.lookuptables")
