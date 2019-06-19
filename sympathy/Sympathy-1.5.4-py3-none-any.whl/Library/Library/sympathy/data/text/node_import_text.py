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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from sylib.importer import base
from sympathy.api import node as synode
from sympathy.api import importers
from sympathy.api.nodeconfig import Port, Ports


class ImportText(base.ImportSingle, synode.Node):
    """
    Import data as a Text.

    :Opposite node: :ref:`Export Texts`
    :Ref. nodes: :ref:`Texts`

    For instructions on how to add or write custom plugins, see
    :ref:`pluginwriting`.
    """

    author = "Erik der Hagopian <erik.hagopian@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.0'
    name = 'Text'
    description = 'Data source as text'
    nodeid = 'org.sysess.sympathy.data.text.importtext'
    icon = 'import_text.svg'
    outputs = Ports([Port.Text('Imported Text', name='port1')])
    plugins = (importers.TextDataImporterBase, )


class ImportTexts(base.ImportMulti, synode.Node):
    """
    Import data as Texts.

    :Opposite node: :ref:`Export Texts`
    :Ref. nodes: :ref:`Text`

    For instructions on how to add or write custom plugins, see
    :ref:`pluginwriting`.
    """
    author = "Erik der Hagopian <erik.hagopian@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.0'
    name = 'Texts'
    description = 'Data source as Texts'
    nodeid = 'org.sysess.sympathy.data.text.importtexts'
    icon = 'import_text.svg'
    outputs = Ports([Port.Texts('Imported Texts', name='port1')])
    plugins = (importers.TextDataImporterBase, )
