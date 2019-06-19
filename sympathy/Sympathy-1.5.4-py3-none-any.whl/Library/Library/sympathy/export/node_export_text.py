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

from sympathy.api import exporters
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sylib.export import common
from sylib.export import base


class ExportTexts(base.ExportMultiple, synode.Node):
    __doc__ = common.COMMON_DOC + """

Export of Texts to the following file formats are supported:
    - Text

:Opposite node: :ref:`Texts`
"""
    name = 'Export Texts'
    description = 'Export Texts'
    icon = 'export_text.svg'
    tags = Tags(Tag.Output.Export)
    plugins = (exporters.TextDataExporterBase, )
    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C) 2013 Combine Control Systems AB'
    nodeid = 'org.sysess.sympathy.export.exportexts'
    version = '0.1'

    inputs = Ports([Port.Texts('Texts to be exported', name='port0'),
                    Port.Datasources(
                        'External filenames',
                        name='port1', n=(0, 1, 0))])

    parameters = base.base_params()
