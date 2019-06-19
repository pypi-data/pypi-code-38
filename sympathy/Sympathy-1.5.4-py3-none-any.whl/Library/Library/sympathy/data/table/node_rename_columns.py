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
The columns in :ref:`Tables` are renamed by the nodes in this category. The
renamed columns, together with not modified ones, are then located in the
outgoing Tables.

The two nodes in the category provide different approaches to specify the
input to the renaming process. One of the nodes uses an additional incoming
Table as a dictionary while the other provides the possibility to specify
regular expressions for search and replace. For more detailed information about
the configuration of the nodes can be found in the documentation of the
specific node.
"""
import re
import collections

from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api import table
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust


def rename_tables(input_file, output_file, dictionary, source,
                  destination):
    # Create a translations dictionary from a single source name to (possibly)
    # many destination names.
    translations = collections.defaultdict(list)
    reverse = {}  # Map from destination to source

    for (src, dst) in zip(dictionary.get_column_to_array(source),
                          dictionary.get_column_to_array(destination)):
        if src not in input_file:
            continue
        if dst in reverse:
            translations[reverse[dst]].remove(dst)
        reverse[dst] = src
        translations[src].append(dst)

    for column in input_file.column_names():
        if column in translations:
            new_column_names = translations[column]
            for new_column_name in new_column_names:
                output_file.update_column(
                    new_column_name, input_file, column)
        elif column not in reverse:
            output_file.update_column(
                column, input_file, column)


def rename_regex(input_file, output_file, src_expr, dst_expr):
    new_names = set()
    for column in input_file.column_names():
        match = re.search(src_expr, column)
        if match:
            new_name = re.sub(src_expr, dst_expr, column)
            new_names.add(new_name)
            output_file.update_column(new_name, input_file, column)
        elif column in new_names:
            # This name has already been taken by some renamed column. Renamed
            # columns have priority over non-renamed columns.
            continue
        else:
            output_file.update_column(column, input_file)


class RenameTableColumnsTables(synode.Node):
    """
    Rename columns in Tables by using an additional Table as a dictionary.

    The dictionary Table must include one column with keywords and another
    column with replacements. When the node is executed all column names in the
    input Tables are checked against keyword column in the ditionary Table. If
    a match is found the corresponding name in the replacement column will
    replace the original column name.  For the case with no match the column
    names are left unchanged.

    If a name appears more than once in the keywords column of the dictionary
    Table, that column will be renamed to each of the replacement names.
    Esentially copying the single input column to several columns in the
    output.

    If a name appears more than once in the replacements column the last one
    that is also present in the data table will be used. Also note that renamed
    columns always take precedence over non-renamed ones.

    :Ref. nodes: :ref:`Rename columns in Tables`
    """

    name = 'Rename columns in Tables with Table'
    author = 'Greger Cronquist <greger.cronquist@combine.se>'
    copyright = '(c) 2013 Combine Control Systems AB'
    version = '1.0'
    nodeid = 'org.sysess.sympathy.data.table.renametablecolumnstable'
    icon = 'rename_columns.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    inputs = Ports([
        Port.Table('Dictionary', name='dictionary'),
        Port.Tables('Input Tables', name='tables')])
    outputs = Ports([
        Port.Tables('Tables with renamed columns', name='tables')])

    parameters = synode.parameters()
    parameters.set_list('source', label='Keyword column',
                        description='Name of column containing old names',
                        editor=synode.Util.combo_editor(
                            edit=True, filter=True))
    parameters.set_list('destination', label='Replacement column',
                        description='Name of column containing new names',
                        editor=synode.Util.combo_editor(
                            edit=True, filter=True))

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['source'],
               node_context.input['dictionary'])
        adjust(node_context.parameters['destination'],
               node_context.input['dictionary'])

    def execute(self, node_context):
        try:
            source = node_context.parameters['source'].selected
            destination = node_context.parameters['destination'].selected
        except Exception:
            source = []
            destination = []

        input_files = node_context.input['tables']
        output_files = node_context.output['tables']
        for input_file in input_files:
            output_file = table.File()
            output_file.set_name(input_file.get_name())
            dictionary = node_context.input['dictionary']
            rename_tables(input_file, output_file, dictionary,
                          source, destination)
            output_file.set_table_attributes(input_file.get_table_attributes())
            output_files.append(output_file)


class RenameTableOperation(node_helper.TableOperation):
    """
    Rename columns in Table(s) using a regular expression.

    Group references may be used in the replacement expression.

    If several columns match the search expression resulting in the same column
    name, the last of the matching columns will be copied to the output and the
    other columns will be removed. Note that renamed columns (i.e. any columns
    that match the search expression) always take precedence over non-renamed
    ones.

    :Ref. nodes: :ref:`Rename columns in Tables with Table`
    """

    author = 'Greger Cronquist <greger.cronquist@combine.se>'
    copyright = '(c) 2013 Combine Control Systems AB'
    version = '1.0'

    name = 'Rename columns in Tables'
    description = 'Rename the Table columns by using regular expressions.'
    nodeid = 'org.sysess.sympathy.data.table.renametablecolumns'
    icon = 'rename_columns.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    inputs = ['Input']
    outputs = ['Output']

    @staticmethod
    def get_parameters(parameter_root):
        parameter_root.set_string(
            'src_expr', label='Search expression', value='',
            description=('Specify the regular expression which will be '
                         'replaced'))
        parameter_root.set_string(
            'dst_expr', label='Replacement expression', value='',
            description='Specify the regular expression for replacement')

    def execute_table(self, in_table, out_table, parameter_root):
        src_expr = parameter_root['src_expr'].value
        dst_expr = parameter_root['dst_expr'].value

        rename_regex(in_table['Input'], out_table['Output'], src_expr,
                     dst_expr)
        out_table['Output'].set_table_attributes(
            in_table['Input'].get_table_attributes())
        out_table['Output'].set_name(in_table['Input'].get_name())


RenameSingleTableColumns = node_helper.table_node_factory(
    'RenameSingleTableColumns', RenameTableOperation,
    'Rename columns in Table',
    'org.sysess.sympathy.data.table.renamesingletablecolumns')


RenameTableColumns = node_helper.tables_node_factory(
    'RenameTableColumns', RenameTableOperation,
    'Rename columns in Tables',
    'org.sysess.sympathy.data.table.renametablecolumns')
