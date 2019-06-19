# Copyright (c) 2016, Combine Control Systems AB
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
import os
from sylib.table_importer_gui import TableImportWidgetMAT
from sylib.table_sources import ImporterMAT, TableSourceMAT
from sylib.matlab import matlab
from sympathy.api import node as synode
from sympathy.api import importers
from sympathy.api import qt as qt_compat

QtGui = qt_compat.import_module('QtGui')


class DataImportMAT(importers.TableDataImporterBase):
    """Importer for MAT files."""

    IMPORTER_NAME = "MAT"

    def __init__(self, fq_infilename, parameters):
        super(DataImportMAT, self).__init__(fq_infilename, parameters)
        if parameters is not None:
            self._init_parameters()

    def name(self):
        return self.IMPORTER_NAME

    def _init_parameters(self):
        parameters = self._parameters
        nbr_of_rows = 99999
        nbr_of_end_rows = 9999999

        # Init data start row spinbox
        if 'data_start_row' not in parameters:
            parameters.set_integer(
                'data_start_row', value=1,
                description='The first row where data is stored.',
                editor=synode.Util.bounded_spinbox_editor(
                    1, nbr_of_rows, 1))
        # Init data end row spinbox
        if 'data_end_row' not in parameters:
            parameters.set_integer(
                'data_end_row', value=0,
                description='The data rows.',
                editor=synode.Util.bounded_spinbox_editor(
                    0, nbr_of_end_rows, 1))

        if 'end_of_file' not in parameters:
            parameters.set_boolean(
                'end_of_file', value=True,
                description='Select all rows to the end of the file.')
        if 'read_selection' not in parameters:
            parameters.set_list(
                'read_selection', value=[0],
                plist=['Read to the end of file',
                       'Read specified number of rows',
                       'Read to specified number of rows from the end'],
                description='Select how to read the data',
                editor=synode.Util.combo_editor())

            # Move value of old parameter to new the format.
            if not parameters['end_of_file'].value:
                parameters['read_selection'].value = [2]

        if 'preview_start_row' not in parameters:
            parameters.set_integer(
                'preview_start_row', value=1, label='Preview start row',
                description='The first row where data will review from.',
                editor=synode.Util.bounded_spinbox_editor(
                    1, 500, 1))

        if 'no_preview_rows' not in parameters:
            parameters.set_integer(
                'no_preview_rows', value=20, label='Number of preview rows',
                description='The number of preview rows to show.',
                editor=synode.Util.bounded_spinbox_editor(1, 200, 1))

        if 'exceptions' not in parameters:
            parameters.set_list(
                'exceptions', label='How to handle failed import:',
                description='Select method to handle eventual errors',
                plist=['Raise Exceptions',
                       'Partially read file',
                       'Read file without delimiters'],
                value=[0], editor=synode.Util.combo_editor())

    def valid_for_file(self):
        """Return True if input file is a valid MAT file."""
        if self._fq_infilename is None:
            return False
        try:
            matlab.read_matfile_to_table(self._fq_infilename)
        except Exception as e:
            return False

        allowed_extensions = ['MAT', 'mat']
        extension = os.path.splitext(self._fq_infilename)[1][1:]

        return extension in allowed_extensions

    def parameter_view(self, parameters):
        valid_for_file = self.valid_for_file()
        return TableImportWidgetMAT(parameters, self._fq_infilename,
                                    valid_for_file)

    def import_data(self, out_datafile, parameters=None, progress=None):
        """Import MAT data from a file"""

        parameters = parameters
        data_row_offset = parameters['data_start_row'].value - 1
        read_selection = parameters['read_selection'].value[0]
        data_rows = parameters['data_end_row'].value
        exceptions = parameters['exceptions'].value[0]

        # Establish connection to mat datasource
        table_source = TableSourceMAT(self._fq_infilename)

        if read_selection == 0:
            nr_data_rows = -1
            data_end_rows = 0
        elif read_selection == 1:
            nr_data_rows = data_rows
            data_end_rows = 0
        elif read_selection == 2:
            nr_data_rows = -1
            data_end_rows = data_rows
        else:
            raise ValueError('Unknown Read Selection.')

        importer = ImporterMAT(table_source)

        try:
            if exceptions == 1:
                importer.set_partial_read(True)
            importer.import_mat(out_datafile, nr_data_rows, data_end_rows,
                                data_row_offset)
        except:
            if exceptions == 2:
                importer.import_mat(out_datafile, nr_data_rows, data_end_rows,
                                    data_row_offset, read_mat_full_rows=True)
            else:
                raise
