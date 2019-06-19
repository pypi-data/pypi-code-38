# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
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
import sys

from sympathy.api import qt as qt_compat
from sympathy.api.exceptions import SyUserCodeError

from . import util
QtGui = qt_compat.import_module('QtGui')  # noqa


class SortWidget(QtGui.QWidget):

    def __init__(self, input_list, node_context, parent=None):
        super(SortWidget, self).__init__(parent)
        self._node_context = node_context
        self._input_list = input_list
        self._parameters = node_context.parameters
        self._init_gui()

    def _init_gui(self):
        vlayout = QtGui.QVBoxLayout()
        compare_label = QtGui.QLabel('Compare function for sorting:')

        self._compare_text = self._parameters['sort_function'].gui()
        reverse_gui = self._node_context.parameters['reverse'].gui()

        self._preview_button = QtGui.QPushButton("Preview sorting")
        self._preview_table = QtGui.QTableWidget()

        compare_vlayout = QtGui.QVBoxLayout()
        compare_vlayout.addWidget(reverse_gui)
        compare_vlayout.addWidget(compare_label)
        compare_vlayout.addWidget(self._compare_text)

        preview_vlayout = QtGui.QVBoxLayout()
        preview_vlayout.addWidget(self._preview_button)
        preview_vlayout.addWidget(self._preview_table)

        sorting_hlayout = QtGui.QHBoxLayout()
        sorting_hlayout.addLayout(compare_vlayout)
        sorting_hlayout.addLayout(preview_vlayout)

        vlayout.addLayout(sorting_hlayout)

        self.setLayout(vlayout)
        self._preview_button.clicked.connect(self._preview_update)

    def _preview_update(self):
        try:
            self._preview_table.clear()

            sort_ind = sorted_list(
                self._parameters['sort_function'].value,
                self._input_list,
                reverse=self._node_context.parameters['reverse'].value,
                enum=True)

            self._preview_table.setRowCount(2)
            self._preview_table.setColumnCount(len(sort_ind))
            self._preview_table.setVerticalHeaderLabels(
                ['Previous indices', 'Sorted indices'])
            self._preview_table.setHorizontalHeaderLabels(
                [' '] * len(sort_ind))
            for ind, new_ind in enumerate(sort_ind):
                self._preview_table.setItem(0, ind, QtGui.QTableWidgetItem(
                    str(ind)))
                self._preview_table.setItem(1, ind, QtGui.QTableWidgetItem(
                    str(new_ind)))
            self._preview_table.resizeColumnsToContents()
        except:
            self._preview_table.clear()
            self._preview_table.setRowCount(1)
            self._preview_table.setColumnCount(1)
            self._preview_table.setItem(
                0, 0, QtGui.QTableWidgetItem(
                    'Sorting function not valid'))


def sorted_list(sort_function_str, input_list, enum=False, reverse=False):
    if len(input_list) == 0:
        return []

    try:
        key_func = util.base_eval(sort_function_str)

        if enum:
            enumerated = sorted(
                enumerate(input_list),
                key=lambda item: key_func(item[1]),
                reverse=reverse)
            return [x for x, y in enumerated]
        else:
            return sorted(
                input_list,
                key=key_func,
                reverse=reverse)
    except Exception:
        raise SyUserCodeError(sys.exc_info(), 'Error executing sort function.')
