# Copyright (c) 2015, Combine Control Systems AB
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

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

from sylib.report import models


class SelectReportPages(QtGui.QWidget):
    def __init__(self, model, parameter_root, parent=None):
        super(SelectReportPages, self).__init__(parent)

        self.parameter_root = parameter_root

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QtGui.QLabel('Select Pages'))

        if model is not None:
            pages = model.find_all_nodes_with_class(models.Page)
        else:
            pages = []
        icons = []
        for page in pages:
            base64_png = page.thumbnail
            if base64_png is None:
                icons.append(QtGui.QIcon())
                continue
            byte_array = QtCore.QByteArray.fromBase64(
                QtCore.QByteArray(base64_png))
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(byte_array)
            icon = QtGui.QIcon(pixmap)
            icons.append(icon)

        self.data_model = {
            'pages': pages,
            'icons': icons
        }

        self.table_view = PageItemTableView()
        layout.addWidget(self.table_view)

        item_model = PageItemModel(self.data_model)
        self.table_view.setModel(item_model)
        self.table_view.resizeRowsToContents()

        # We are storing tuples with values (uuid, label)
        initially_selected_uuids = []
        for v in parameter_root['selected_pages'].list:
            try:
                initially_selected_uuids.append(v[0])
            except TypeError:
                # For backward compatibility where the value was a list of
                # row numbers.
                if v < len(pages):
                    initially_selected_uuids.append(pages[v].uuid)
        initially_selected_uuids = list(set(initially_selected_uuids))
        current_uuids = [p.uuid for p in pages]
        selected_rows = [current_uuids.index(x)
                         for x in initially_selected_uuids
                         if x in current_uuids]
        for row in selected_rows:
            self.table_view.selectRow(row)

        # Listen to changes. Store reference to selection model to avoid
        # segfault in PySide.
        self.selection_model = self.table_view.selectionModel()
        self.selection_model.selectionChanged.connect(
            self.handle_selection_changed)

    def handle_selection_changed(self, selected, deselected):
        uuid_list = []
        for index in self.selection_model.selectedIndexes():
            page = self.data_model['pages'][index.row()]
            uuid_list.append((page.uuid, page.label))
        self.parameter_root['selected_pages'].list = uuid_list


class PageItemTableView(QtGui.QTableView):
    def __init__(self, parent=None):
        super(PageItemTableView, self).__init__(parent)
        self.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)
        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setVisible(True)
        self.setShowGrid(False)
        self.setGridStyle(QtCore.Qt.NoPen)
        self.setIconSize(QtCore.QSize(64, 64))
        self.setSelectionMode(
            QtGui.QAbstractItemView.MultiSelection)

    def setModel(self, item_model):
        super(PageItemTableView, self).setModel(item_model)


class PageItemModel(QtCore.QAbstractTableModel):
    def __init__(self, data_model, parent=None):
        super(PageItemModel, self).__init__(parent)

        self.data_model = data_model

    def rowCount(self, parent_index=QtCore.QModelIndex()):
        return len(self.data_model['pages'])

    def columnCount(self, parent_index=QtCore.QModelIndex()):
        return 1

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                if section == 0:
                    return 'Page'
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return '{}'.format(section + 1)
        return None

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return self.data_model['pages'][index.row()].label
        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                icon = self.data_model['icons'][index.row()]
                return icon
        return None

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
