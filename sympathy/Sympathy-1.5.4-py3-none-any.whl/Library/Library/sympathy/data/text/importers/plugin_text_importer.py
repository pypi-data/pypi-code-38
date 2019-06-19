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
import codecs
import os
from sympathy.api import importers
from sympathy.api import node as synode
from sympathy.api import qt as qt_compat
from sympathy.api import exceptions
import sylib.table_sources
QtGui = qt_compat.import_module('QtGui')


def all_equal(iterator):
    try:
        iterator = iter(iterator)
        first = next(iterator)
        return all(first == rest for rest in iterator)
    except StopIteration:
        return True


class DataImportText(importers.TextDataImporterBase):
    """Importer for Text files."""
    IMPORTER_NAME = "Text"

    def __init__(self, fq_infilename, parameters):
        super(DataImportText, self).__init__(fq_infilename, parameters)
        if parameters is not None:
            self._init_parameters()

    def _init_parameters(self):
        if 'source_coding' not in self._parameters:
            self._parameters.set_string(
                'source_coding',
                label='Encoding',
                editor=synode.Util.combo_editor(
                    options=list(
                        sylib.table_sources.CODEC_LANGS.keys())),
                value='UTF-8',
                description='Encoding used to decode file')

    def parameter_view(self, parameters):
        valid_for_file = self.valid_for_file()
        if not valid_for_file:
            return QtGui.QLabel(
                'File does not exist or cannot be read.')
        return parameters['source_coding'].gui()

    def import_data(self, out_datafile, parameters=None, progress=None):
        encoding = sylib.table_sources.CODEC_LANGS[
            parameters['source_coding'].value]

        if not self.valid_for_file():
            raise exceptions.SyDataError(
                'Importer: {} is not valid for: {}'.format(
                    self.display_name(), self._fq_infilename))
        with codecs.open(self._fq_infilename, 'r', encoding=encoding) as f:
            out_datafile.set(f.read())

    def valid_for_file(self):
        """Is fq_filename valid Text."""
        return self._fq_infilename is not None and (
            os.path.isfile(self._fq_infilename))

    def is_type(self):
        return False
