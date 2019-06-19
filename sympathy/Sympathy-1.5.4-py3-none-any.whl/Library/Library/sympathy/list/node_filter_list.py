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
from __future__ import (
    print_function, division, unicode_literals, absolute_import)
import numpy as np
import six

from sylib import util
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.nodeconfig import join_doc


COMMON_DOC = """
Filter nodes with Table input takes a table on the upper port and use it to
filter the list on the lower port. The table must contain a single column which
should be at least as long as the list on the lower port. Lets call it the
filter-column. Now for each item in the incoming list the corresponding index
of the filter-column is inspected. If it is True (or is considered True in
Python, e.g. any non-zero integer or a non-empty string) the item is included
in the filtered list. And vice versa, if the value in the filter-column is
False (or is considered False in Python, e.g. 0 or an empty string) the
corresponding item is not included in the filtered list. """


COMMON_PRED_DOC = """
Filter nodes with predicate takes a configurable predicate function
(a function that returns True or False) from the configuration and uses it to
decide which inputs to include in the output.

The function is applied for each input element in the list and for each element
where the function returned True the element is also included in the output.

Examples with port type == [table] and item type == table:

    Propagate tables with at least 10 rows to output::

        lambda item: item.number_of_rows() >= 10

    Propagate only non-empty tables::

        lambda item: not item.is_empty()

The name of the argument is not important.

See https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions for
a description of lambda functions. Have a look at the :ref:`Data type
APIs<datatypeapis>` to see what methods and attributes are available on the
data type that you are working with.
"""


COMMON_PART_PRED_DOC = """
Partition nodes with predicate takes a configurable predicate function
(a function that returns True or False) from the configuration and uses it to
decide how to partition the output.

The function is applied for each input element in the list. If it returns
True, then the element is written to the first output, otherwise it is
written to the second output.

Examples with port type == [table] and item type == table:

    Remove tables with less than 10 rows::

        lambda item: item.number_of_rows() > 10

    Remove empty tables::

        lambda item: not item.is_empty()

The name of the argument is not important.

See https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions for
a description of lambda functions. Have a look at the :ref:`Data type
APIs<datatypeapis>` to see what methods and attributes are available on the
data type that you are working with.
"""


class FilterListTable(synode.Node):
    __doc__ = join_doc(
        COMMON_DOC,
        """
    Filter a list using an incoming table.
    """)

    name = "Filter List with Table"
    nodeid = "org.sysess.sympathy.list.filterlisttable"
    description = "Filter a list using an incoming table."
    icon = "filter_list.svg"
    author = "Magnus Sanden <magnus.sanden@combine.se>"
    copyright = "(c) 2016 Combine Control Systems AB"
    version = '1.0'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)

    inputs = Ports([Port.Table('Filter', name="filter"),
                    Port.Custom('[<a>]', 'List of items', name='in')])
    outputs = Ports(
        [Port.Custom('[<a>]', 'Filtered list of items', name='out')])

    parameters = synode.parameters()
    parameters.set_list(
        'filter', label='Filter column',
        description='Select the column which holds the filter',
        value=[],
        editor=synode.Util.combo_editor(edit=True, filter=True))

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['filter'], node_context.input['filter'])

    def execute(self, node_context):
        filterfile = node_context.input['filter']
        if filterfile.number_of_rows() == 0:
            node_context.output['out'].source(node_context.input['in'])
            return
        columns = filterfile.column_names()
        try:
            index = synode.parameters(
                node_context.parameters)['filter'].value[0]
            column = columns[index]
        except IndexError:
            column = columns[0]
        filter_values = filterfile.get_column_to_array(column)
        infiles = node_context.input['in']
        outfiles = node_context.output['out']

        for filter_value, infile in six.moves.zip(filter_values, infiles):
            if filter_value:
                outfiles.append(infile)


def predicate_function(node_context):
    predicate_str = node_context.parameters['predicate'].value
    return util.base_eval(predicate_str)


class FilterListPredicate(synode.Node):
    __doc__ = join_doc(
        COMMON_PRED_DOC,
        """
    Filter a list using a predicate.
    """)

    name = 'Filter List Predicate'
    nodeid = 'org.sysess.sympathy.list.filterlistpredicate'
    description = 'Filter a list using configured item based predicate.'
    icon = 'filter_list.svg'
    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C) 2015 Combine Control Systems AB'
    version = '1.0'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)

    inputs = Ports([
        Port.Custom('[<a>]', 'List', name='list')])

    outputs = Ports([
        Port.Table('Index', name='index'),
        Port.Custom('[<a>]', 'List', name='list')])

    parameters = synode.parameters()
    parameters.set_string(
        'predicate',
        label='Predicate filter function',
        value='lambda item: True  # Identity filter',
        editor=synode.Util.code_editor(),
        description='Filter function')

    def verify_parameters(self, node_context):
        try:
            predicate_function(node_context)
        except:
            return False
        return True

    def execute(self, node_context):
        infiles = node_context.input['list']
        outfiles = node_context.output['list']
        index = node_context.output['index']
        predicate_fn = predicate_function(node_context)

        index_data = []

        for i, infile in enumerate(infiles):
            self.set_progress(i * 100 / len(infiles))

            if predicate_fn(infile):
                outfiles.append(infile)
                index_data.append(True)
            else:
                index_data.append(False)

        index.set_column_from_array('filter', np.array(index_data))


class PartitionListPredicate(synode.Node):
    __doc__ = join_doc(
        COMMON_PART_PRED_DOC,
        """
    Partition a list using a predicate.
    """)

    name = 'Partition List Predicate'
    nodeid = 'org.sysess.sympathy.list.partitionlistpredicate'
    description = 'Partition a list using configured item based predicate.'
    icon = 'partition_list.svg'
    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C) 2015 Combine Control Systems AB'
    version = '1.0'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)

    inputs = Ports([
        Port.Custom('[<a>]', 'List', name='list')])

    outputs = Ports([
        Port.Custom('[<a>]', 'List of items where predicate returned true',
                    name='list_true'),
        Port.Custom('[<a>]', 'List of items where predicate returned false',
                    name='list_false')])

    parameters = synode.parameters()

    parameters.set_string(
        'predicate',
        label='Predicate partition function',
        value='lambda item: True  # Identity partition',
        editor=synode.Util.code_editor(),
        description='Partition function')

    def verify_parameters(self, node_context):
        try:
            predicate_function(node_context)
        except:
            return False
        return True

    def execute(self, node_context):
        infiles = node_context.input['list']
        truefiles = node_context.output['list_true']
        falsefiles = node_context.output['list_false']
        predicate_fn = predicate_function(node_context)

        for i, infile in enumerate(infiles):
            self.set_progress(i * 100 / len(infiles))

            if predicate_fn(infile):
                truefiles.append(infile)
            else:
                falsefiles.append(infile)


class ConditionalPropagate(synode.Node):
    """
    Conditional propagate takes a configurable predicate
    function (a function that returns True or False) from the configuration and
    uses it to decide which input to return to the output.

    The function is applied to the input data for the node. So for example if
    the input port is connected to a table port the argument of the lambda will
    be a :class:`table.File<tableapi>`. Have a look at the :ref:`Data type
    APIs<datatypeapis>` to see what methods and attributes are available on the
    data type that you are working with.

    If the lambda function returns True, the data from the first port is
    written to the output, otherwise the data from the second port is written
    to the output.
    """

    name = 'Conditional Propagate'
    nodeid = 'org.sysess.sympathy.list.eitherwithdatapredicate'
    description = 'Uses a condition to propagate either one of the two inputs.'
    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C) 2015 Combine Control Systems AB'
    version = '1.0'
    tags = Tags(Tag.Generic.Control)
    icon = 'either.svg'

    inputs = Ports([
        Port.Custom('<a>', 'First, returned if predicate held true',
                    name='true'),
        Port.Custom('<a>', 'Second, returned if predicate did not hold true',
                    name='false'),
        Port.Custom('<b>', 'Data for the predicate comparison',
                    name='data')])

    outputs = Ports([Port.Custom(
        '<a>',
        'Output, First if the predicate holds true otherwise Second',
        name='output')])
    parameters = synode.parameters()

    parameters.set_string(
        'predicate',
        label='Condition',
        value='lambda arg: True  # Identity predicate',
        editor=synode.Util.code_editor(),
        description='Either predicate function')

    def verify_parameters(self, node_context):
        try:
            predicate_function(node_context)
        except:
            return False
        return True

    def execute(self, node_context):
        truefile = node_context.input['true']
        falsefile = node_context.input['false']
        datafile = node_context.input['data']
        outputfile = node_context.output['output']
        predicate_fn = predicate_function(node_context)

        if predicate_fn(datafile):
            outputfile.source(truefile)
        else:
            outputfile.source(falsefile)
