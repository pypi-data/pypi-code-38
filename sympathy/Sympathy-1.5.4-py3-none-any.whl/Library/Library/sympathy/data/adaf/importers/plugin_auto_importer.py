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
import inspect
from PySide.QtGui import QLabel

from sympathy.api import importers
from sympathy.api.exceptions import SyDataError


def hasarg(func, arg):
    return arg in inspect.getargspec(func).args


class DataImportAuto(importers.ADAFDataImporterBase):
    """Auto importer."""
    IMPORTER_NAME = "Auto"

    def __init__(self, fq_infilename, parameters):
        self.__importer_class = None
        super(DataImportAuto, self).__init__(fq_infilename, parameters)

    def _importer_class(self):
        if self._fq_infilename is not None:
            if self.__importer_class is None:
                self.__importer_class = (
                    importers.plugin_for_file(
                        importers.ADAFDataImporterBase,
                        self._fq_infilename))
        return self.__importer_class

    def valid_for_file(self):
        """Never valid when sniffing."""
        return False

    def is_type(self):
        importer_class = self._importer_class()

        if importer_class is None:
            raise SyDataError(
                "No importer could automatically be found for this file.")
        importer = importer_class(self._fq_infilename, None)
        return importer.is_type()

    def parameter_view(self, parameters):
        importer_class = self._importer_class()

        if importer_class is None:
            text = "No importer could automatically be found for this file."
        else:
            text = "This file will be imported using the {} importer.".format(
                importer_class.display_name())
        return QLabel(text)

    def import_data(self, out_datafile, parameters=None, progress=None,
                    manage_input=None):
        """Sniff all available importers."""
        importer_class = self._importer_class()

        if importer_class is None:
            raise SyDataError(
                "No importer could automatically be found for this file.")
        importer = importer_class(self._fq_infilename, parameters)

        if hasarg(importer.import_data, 'manage_input'):
            importer.import_data(out_datafile, parameters, progress,
                                 manage_input)
        else:
            importer.import_data(out_datafile, parameters, progress)
