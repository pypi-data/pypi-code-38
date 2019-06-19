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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import warnings

# Ignore a warning from numpy>=1.14 when importing h5py<=2.7.1:
with warnings.catch_warnings():
    warnings.simplefilter('ignore', FutureWarning)
    import h5py

from sympathy.api import importers
from sympathy.api import adaf
from sympathy.api import qt as qt_compat
QtGui = qt_compat.import_module('QtGui')


class ImportWidget(QtGui.QWidget):

    def __init__(self, parameters, fq_infilename):
        super(ImportWidget, self).__init__()
        self._filename = fq_infilename
        self._parameters = parameters
        self._init_gui()

    def _init_gui(self):
        vlayout = QtGui.QVBoxLayout()
        vlayout.addWidget(self._parameters['import_links'].gui())
        self.setLayout(vlayout)


class DataImporterADAF(importers.ADAFDataImporterBase):
    """Importer for an ADAF file. This is a special class and does
    not have a valid import_data method."""
    IMPORTER_NAME = "ADAF"
    DISPLAY_NAME = "SyData"

    def __init__(self, fq_infilename, parameters):
        super(DataImporterADAF, self).__init__(fq_infilename, parameters)
        if parameters is not None:
            self._init_parameters()

    def valid_for_file(self):
        if h5py.is_hdf5(self._fq_infilename):
            with h5py.File(self._fq_infilename, 'r') as f:
                if {'meta', 'root'}.difference(f.keys()) != set():
                    return False
                if not ('sys' in f or 'tb' in f):
                    return False

            if not adaf.is_adaf('hdf5', self._fq_infilename):
                return False
            return True

        return False

    def is_type(self):
        return True

    def import_data(self, out_datafile, parameters=None, progress=None):
        raise AssertionError("Something went terribly wrong.")

    def _init_parameters(self):
        parameters = self._parameters

        # Init headers checkbox
        if 'import_links' not in parameters:
            parameters.set_boolean(
                'import_links', value=False,
                label='Import with links to source file',
                description=(
                    'Import with links to source file, this file and '
                    'any files that it may link to  must not be moved '
                    'while the flow is opened.'))

    def parameter_view(self, parameters):
        return ImportWidget(parameters, self._fq_infilename)

    @property
    def import_links(self):
        return self._parameters['import_links'].value
