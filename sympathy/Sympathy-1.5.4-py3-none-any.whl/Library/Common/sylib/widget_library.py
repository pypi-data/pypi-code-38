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
import six
from sympathy.api import qt as qt_compat
from sympathy.utils import search
QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')


def fuzzy_filter(text):
    """Method returns a regex generated with a fuzzy filter algoritm."""
    return search.fuzzy_pattern(text)


class FilterLineEdit(QtGui.QWidget):
    filter_changed = qt_compat.Signal()
    """Widget containing a lineedit connected to the creation of filter."""
    def __init__(self, start_exp='', parent=None):
        super(FilterLineEdit, self).__init__(parent)
        self._init_gui(start_exp)

    def _init_gui(self, start_exp):
        hlayout = QtGui.QHBoxLayout()
        hlayout.setContentsMargins(QtCore.QMargins())
        hlayout.setSpacing(10)

        filter_label = QtGui.QLabel('Filter:')
        self._filter_lineedit = QtGui.QLineEdit()
        self._filter_lineedit.setText(start_exp)

        hlayout.addWidget(filter_label)
        hlayout.addWidget(self._filter_lineedit)

        self._filter_lineedit.textChanged.connect(self._filter_changed)

        self.setLayout(hlayout)

    def filter(self):
        return self._filter

    def set_text(self, text):
        self._filter_lineedit.setText(text)

    def get_text(self):
        return self._filter_lineedit.text()

    def _filter_changed(self, text):
        """Method called when the text in the lineedit is changed."""
        self._filter = fuzzy_filter(text)
        self.filter_changed.emit()


class FilterListView(QtGui.QWidget):
    """
    Widget containing a listwiget and filter functionality. The filter
    is used for reduce of the number of items in the listview to make it
    easier for users to search the content.
    """

    def __init__(self, header='', parent=None):
        super(FilterListView, self).__init__(parent)
        self._init_gui(header)

    def _init_gui(self, header):
        vlayout = QtGui.QVBoxLayout()
        vlayout.setContentsMargins(QtCore.QMargins())

        if header:
            header_label = QtGui.QLabel(header)
            vlayout.addWidget(header_label)

        self._filter_widget = FilterLineEdit()
        vlayout.addWidget(self._filter_widget)

        self.list_widget = QtGui.QListWidget()
        self.list_widget.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.list_widget.setAlternatingRowColors(True)
        vlayout.addWidget(self.list_widget)

        self._filter_widget.filter_changed.connect(self._change_display)

        self.setLayout(vlayout)

    def add_item(self, item):
        self.list_widget.addItem(item)

    def add_items(self, items):
        self.list_widget.addItems(list(items))

    def clear(self):
        self.list_widget.clear()

    def _change_display(self):
        filter_ = self._filter_widget.filter()
        display = [row for row in six.moves.range(self.list_widget.count())
                   if search.matches(filter_,
                                     self.list_widget.item(row).text())]

        for row in six.moves.range(self.list_widget.count()):
            if row in display:
                self.list_widget.item(row).setHidden(False)
            else:
                self.list_widget.item(row).setHidden(True)
