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

from sylib.export import table as exporttable
from sylib.matlab import matlab
from sympathy.api import qt as qt_compat

QtGui = qt_compat.import_module('QtGui')


class DataExportMATWidget(QtGui.QWidget):
    filename_changed = qt_compat.Signal()

    def __init__(self, parameter_root, *args, **kwargs):
        super(DataExportMATWidget, self).__init__(*args, **kwargs)
        self._parameter_root = parameter_root
        self._init_gui()

    def _init_gui(self):
        vlayout = QtGui.QVBoxLayout()
        table_names_gui = self._parameter_root['table_names'].gui()
        table_names_gui.valueChanged.connect(self._filename_changed)
        vlayout.addWidget(table_names_gui)
        vlayout.addWidget(self._parameter_root['header'].gui())
        self.setLayout(vlayout)

    def _filename_changed(self):
        self.filename_changed.emit()


class DataExportMAT(exporttable.TableDataExporterBase):
    """Exporter for MAT files."""

    EXPORTER_NAME = "MAT"
    FILENAME_EXTENSION = "mat"

    def __init__(self, parameters):
        super(DataExportMAT, self).__init__(parameters)
        if 'table_names' not in parameters:
            parameters.set_boolean(
                'table_names', label='Use table names as filenames',
                description='Use table names as filenames')
        if 'header' not in parameters:
            parameters.set_boolean(
                'header', value=True, label='Export header',
                description='Export column names')

    def parameter_view(self, node_context_input):
        return DataExportMATWidget(self._parameters)

    def export_data(self, in_sytable, fq_outfilename, progress=None):
        """Export Table to MAT."""
        header = self._parameters['header'].value
        matlab.write_table_to_matfile(in_sytable, fq_outfilename, header)
