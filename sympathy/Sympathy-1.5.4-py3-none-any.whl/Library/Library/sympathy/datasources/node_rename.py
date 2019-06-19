# Copyright (c) 2018, Combine Control Systems AB
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
import re

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import qt as qt_compat
QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')


class RenameDatasource(synode.Node):
    """
    Create Datasources with paths to data sources.

    :Ref. nodes: :ref:`Datasource`
    """

    author = "Mathias Broxvall <mathias.broxvall@combine.se>"
    copyright = "(C) 2018 Combine Control Systems AB"
    version = '1.1'
    icon = 'datasource_rename.svg'
    tags = Tags(Tag.DataProcessing.TransformData)
    name = 'Rename datasource with regexp'
    description = ('Applies a regular expression to modify '
                   'the PATH of a datasource.')
    nodeid = 'org.sysess.sympathy.datasources.rename'

    inputs = Ports([Port.Datasource('Datasource input', name='input')])
    outputs = Ports([Port.Datasource('Datasource output', name='output')])

    parameters = synode.parameters()

    parameters = synode.parameters()
    parameters.set_string(
        'search', label='Search',
        description=(
            'Part of path to replace using a regular expression. '
            'Use "$" for end of name and "^" for the beginning.'))
    parameters.set_string(
        'replace', label='Replace',
        description=(
            'Text to replace the matched parts with. Use eg. "\\1" to '
            'substitute the first matched (paranthesis) group. '))

    def execute(self, node_context):
        search = node_context.parameters['search'].value
        replace = node_context.parameters['replace'].value

        input = node_context.input['input']
        output = node_context.output['output']

        path = input.decode_path()
        typename = input.decode_type()
        path = re.sub(search, replace, path)
        output.encode({'path': path, 'type': typename})
