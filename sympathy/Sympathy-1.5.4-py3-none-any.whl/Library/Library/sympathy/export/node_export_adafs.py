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
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports
from sylib.export import common
from sylib.export import adaf as exportadaf
from sylib.export import base


class ExportADAFs(base.ExportMultiple, synode.Node):
    __doc__ = common.COMMON_DOC + """

Export of ADAFs to the following file formats are supported:
    - SyData
    - MDF

For export of ADAF to file there exist a number of strategies that
can be used to extract filenames from information stored in the ADAFs. If no
strategy is selected one has to declare the base of the filename.

The following strategies exist:
    - **Source identifier as name**
        Use the source identifier in the ADAFs as filenames.
    - **Column with name**
        Specify a column in the metadata container where the first element
        is the filename.

:Opposite nodes: :ref:`ADAFs`
:Ref. nodes: :ref:`Export Tables`
"""
    name = 'Export ADAFs'
    description = 'Export ADAFs'
    icon = 'adaf_export.svg'
    plugins = (exportadaf.TabbedADAFDataExporterBase, )
    author = 'Alexander Busck <alexander.busck@combine.se>'
    copyright = '(c) 2013 Combine Control Systems AB'
    nodeid = 'org.sysess.sympathy.export.exportadafs'
    version = '0.1'

    inputs = Ports([Port.ADAFs('Input ADAFs', name='port0'),
                    Port.Datasources(
                        'External filenames',
                        name='port1', n=(0, 1, 0))])
    parameters = base.base_params()
