# Copyright (c) 2013, Combine Control Systems AB
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
These two nodes takes the structure of an ADAF or ADAFs (Type, System, Raster,
and Parameter) and outputs it to a Table or Tables.
"""
import numpy as np

from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags


class ADAFStructureTable(synode.Node):
    """Creates Table from the structure of the ADAF."""

    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C) 2013 Combine Control Systems AB'
    version = '1.0'
    icon = 'adaf2adafs.svg'

    name = 'ADAF structure to Table'
    description = 'Creates Table from the structure of the ADAF.'
    nodeid = 'org.sysess.sympathy.data.adaf.adafstructuretable'
    tags = Tags(Tag.DataProcessing.Index)

    inputs = Ports([Port.ADAF('Input ADAF', name='port1')])
    outputs = Ports([Port.Table('ADAF structure as Table', name='port1')])

    @staticmethod
    def run(input_file, output_file):
        def adaf_iterator(adaf_file):
            yield ('Metadata', '', '', adaf_file.meta.keys())
            yield ('Result', '', '', adaf_file.res.keys())
            for system_key, system_value in adaf_file.sys.items():
                for raster_key, raster_value in system_value.items():
                    yield ('Timeseries', system_key, raster_key,
                           raster_value.keys())

        type_column = []
        system_column = []
        raster_column = []
        parameter_column = []
        index_column = []

        output_info = [('Type', type_column),
                       ('System', system_column),
                       ('Raster', raster_column),
                       ('Parameter', parameter_column),
                       ('Index', index_column)]

        for i, (type_key, system_key, raster_key,
                parameter_keys) in enumerate(adaf_iterator(input_file)):

            number_of_keys = len(parameter_keys)
            type_column.extend([type_key] * number_of_keys)
            system_column.extend([system_key] * number_of_keys)
            raster_column.extend([raster_key] * number_of_keys)
            parameter_column.extend(parameter_keys)
            index_column.extend([i] * number_of_keys)

        for name, column in output_info:
            output_file.set_column_from_array(name, np.array(column))

    def execute(self, node_context):
        input_file = node_context.input[0]
        output_file = node_context.output[0]
        self.run(input_file, output_file)


ADAFsStructureTables = node_helper.list_node_factory(
    ADAFStructureTable,
    ['port1'], ['port1'],
    name='ADAFs structure to Tables',
    nodeid='org.sysess.sympathy.data.adaf.adafsstructuretables')
