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
This node handles compression/decompression of some common archive formats.

The following formats are supported:
* ZIP
* GZIP
* TAR

The ZIP format can compress and store multiple files in a single archive.
All input files will be put into an archive with the configured name.

GZIP however only compresses one file at a time. The compressed file will have
the same name as the original file, but with the added extension .gz.
Therefore you cannot configure the name.

To create an archive with multiple files, using GZIP, you have to use two nodes
in succession. In the first one you will use TAR, which creates one file
of all the input files, much like the ZIP option, but this file is not yet
compressed. So in the second node you will use GZIP to compress the TAR
archive. This results in a file iwth the extension .tar.gz.

To decompress you then do the same in reverse. First decompress with GZIP then
extract all files with TAR.
"""
from sylib.export import base
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sylib.export import datasource as exportdatasource


class ExportDatasources(base.ExportMultiple, synode.Node):
    """Compress/decompress files that are pointed to by the Datasources"""

    name = 'Archive files'
    description = 'Compress/decompress Datasources'
    icon = 'export_datasource.svg'
    inputs = Ports([Port.Datasources(
        'Datasources to be exported', name='port0'),
                    Port.Datasources(
                        'External filenames',
                        name='port1', n=(0, 1, 0))])

    tags = Tags(Tag.Disk.File)
    plugins = (exportdatasource.DatasourceArchiveBase, )
    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C) 2013, 2017, Combine Control Systems AB'
    nodeid = 'org.sysess.sympathy.export.exportdatasources'
    version = '1.0'

    def update_parameters(self, old_params):
        archive_type = old_params['active_exporter'].value
        if archive_type == 'ZIP':
            old_params['active_exporter'].value = 'ZIP Extractor'
        elif archive_type == 'GZIP':
            old_params['active_exporter'].value = 'GZIP Extractor'

        parameter_dict = old_params.parameter_dict
        custom_data = parameter_dict['custom_exporter_data']

        for old_key, new_key in [('ZIP', 'ZIP Extractor'),
                                 ('GZIP', 'GZIP Extractor')]:
            group = custom_data.pop(old_key, None)
            if group is not None:
                custom_data[new_key] = group
