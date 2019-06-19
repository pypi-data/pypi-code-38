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

import numpy as np
from sympathy.api import table
from .viewerbase import ViewerBase
from .table_viewer import TableViewer
from sympathy.api import qt

QtCore = qt.QtCore
QtGui = qt.import_module('QtGui')


def create_table_from_datasource(ds):
    ds_path = np.array([ds.decode_path() or ''])
    ds_type = np.array([ds.decode_type() or ''])
    return table.File.from_recarray(
        np.rec.array((ds_path, ds_type), names=('path', 'type')))


class DatasourceViewer(ViewerBase):
    def __init__(self, datasource_data=None, console=None, parent=None):
        super(DatasourceViewer, self).__init__(parent)

        self._datasource = datasource_data
        self._viewer = None

        self._init_gui()
        try:
            self.update_data(self._datasource)
        except Exception:
            self._datasource.encode_path('')
            self.update_data(self._datasource)

    def datasource(self):
        return self._datasource

    def data(self):
        return self.datasource()

    def update_data(self, data):
        if data is not None:
            self._datasource = data
            self._viewer.update_data(
                create_table_from_datasource(data))

    def _init_gui(self):
        layout = QtGui.QVBoxLayout()
        self._viewer = TableViewer(plot=False)
        self._viewer.show_colors(False)
        layout.addWidget(self._viewer)
        self.setLayout(layout)
