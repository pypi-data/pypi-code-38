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
import os
from sylib.xl_utils import is_xlsx, is_xls
from sylib.table_importer_gui import TableImportWidgetXLS
from sylib.table_sources import ImporterXLS
from sympathy.api import node as synode
from sympathy.api import importers
from sympathy.api import qt as qt_compat

QtGui = qt_compat.import_module('QtGui')


class DataImportXLS(importers.TableDataImporterBase):
    """Importer for Excel files."""

    IMPORTER_NAME = 'XLS'
    PARAMETER_VIEW = TableImportWidgetXLS

    def __init__(self, fq_infilename, parameters):
        super(DataImportXLS, self).__init__(fq_infilename, parameters)
        if parameters is not None:
            self._init_parameters()

    def _init_parameters(self):
        parameter_root = self._parameters
        nbr_of_rows = 99999
        nbr_of_end_rows = 9999999

        try:
            parameter_root['worksheet_name']
        except KeyError:
            parameter_root.set_list(
                'worksheet_name', label='Select worksheet',
                description='The worksheet to import from.',
                editor=synode.Util.combo_editor())
        # Init header start row spinbox
        try:
            parameter_root['header_row']
        except KeyError:
            parameter_root.set_integer(
                'header_row', value=1,
                description='The row where the headers are located.',
                editor=synode.Util.bounded_spinbox_editor(
                    1, nbr_of_rows, 1))
        # Init unit row spinbox
        try:
            parameter_root['unit_row']
        except KeyError:
            parameter_root.set_integer(
                'unit_row', value=1,
                description='The row where the units are located.',
                editor=synode.Util.bounded_spinbox_editor(
                    1, nbr_of_rows, 1))
        # Init description row spinbox
        try:
            parameter_root['description_row']
        except KeyError:
            parameter_root.set_integer(
                'description_row', value=1,
                description='The row where the descriptions are located.',
                editor=synode.Util.bounded_spinbox_editor(
                    1, nbr_of_rows, 1))
        # Init data start row spinbox
        try:
            parameter_root['data_start_row']
        except KeyError:
            parameter_root.set_integer(
                'data_start_row', value=2,
                description='The first row where data is stored.',
                editor=synode.Util.bounded_spinbox_editor(
                    1, nbr_of_rows, 1))
        # Init data end row spinbox
        try:
            parameter_root['data_end_row']
        except KeyError:
            parameter_root.set_integer(
                'data_end_row', value=0, description='The last data row.',
                editor=synode.Util.bounded_spinbox_editor(
                    0, nbr_of_end_rows, 1))
        # Init headers checkbox
        try:
            parameter_root['headers']
        except KeyError:
            parameter_root.set_boolean(
                'headers', value=True,
                description='File has headers.')
        # Init units checkbox
        try:
            parameter_root['units']
        except KeyError:
            parameter_root.set_boolean(
                'units', value=False,
                description='File has headers.')
        # Init descriptions checkbox
        try:
            parameter_root['descriptions']
        except KeyError:
            parameter_root.set_boolean(
                'descriptions', value=False,
                description='File has headers.')
        # Init transposed checkbox
        try:
            parameter_root['transposed']
        except KeyError:
            parameter_root.set_boolean(
                'transposed', value=False, label='Transpose input',
                description='Transpose the data.')
        try:
            parameter_root['end_of_file']
        except KeyError:
            parameter_root.set_boolean(
                'end_of_file', value=True,
                description='Select all rows to the end of the file.')

        try:
            parameter_root['read_selection']
        except KeyError:
            parameter_root.set_list(
                'read_selection', value=[0],
                plist=['Read to the end of file',
                       'Read specified number of rows',
                       'Read to specified number of rows from the end'],
                description='Select how to read the data',
                editor=synode.Util.combo_editor())

            # Move value of old parameter to new the format.
            if not parameter_root['end_of_file'].value:
                parameter_root['read_selection'].value = [2]

        try:
            parameter_root['preview_start_row']
        except KeyError:
            parameter_root.set_integer(
                'preview_start_row', value=1, label='Preview start row',
                description='The first row where data will review from.',
                editor=synode.Util.bounded_spinbox_editor(1, 200, 1))
        try:
            parameter_root['no_preview_rows']
        except KeyError:
            parameter_root.set_integer(
                'no_preview_rows', value=20, label='Number of preview rows',
                description='The number of preview rows to show.',
                editor=synode.Util.bounded_spinbox_editor(1, 200, 1))

    def name(self):
        return self.IMPORTER_NAME

    def valid_for_file(self):
        if self._fq_infilename is None or not os.path.isfile(
                self._fq_infilename):
            return False

        return is_xlsx(self._fq_infilename) or is_xls(self._fq_infilename)

    def parameter_view(self, parameters):
        valid_for_file = self.valid_for_file()
        return TableImportWidgetXLS(
            parameters, self._fq_infilename, valid_for_file)

    def import_data(self, out_datafile, parameters=None, progress=None):
        parameter_root = parameters

        headers_bool = parameter_root['headers'].value
        headers_row_offset = parameter_root['header_row'].value - 1
        units_bool = parameter_root['units'].value
        units_row_offset = parameter_root['unit_row'].value - 1
        descs_bool = parameter_root['descriptions'].value
        descs_row_offset = parameter_root['description_row'].value - 1
        data_start_row = parameter_root['data_start_row'].value - 1
        read_selection = parameter_root['read_selection'].value[0]
        transposed = parameter_root['transposed'].value
        sheet_name = parameter_root['worksheet_name'].selected

        if not headers_bool:
            headers_row_offset = -1
        if not units_bool:
            units_row_offset = -1
        if not descs_bool:
            descs_row_offset = -1

        if read_selection == 0:
            data_end_row = 0
        elif read_selection == 1:
            data_end_row = parameter_root['data_end_row'].value
        elif read_selection == 2:
            data_end_row = - parameter_root['data_end_row'].value
        else:
            raise ValueError('Unknown Read Selection.')

        importer = ImporterXLS(self._fq_infilename)
        importer.import_xls(out_datafile, sheet_name, data_start_row,
                            data_end_row, transposed,
                            headers_row_offset=headers_row_offset,
                            units_row_offset=units_row_offset,
                            descriptions_row_offset=descs_row_offset)
