# This file is part of Sympathy for Data.
# Copyright (c) 2018 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
import datetime
import logging
import os
import six
import sys
import weakref
from collections import OrderedDict

from sympathy.platform import widget_library as sywidgets

from . import util
from . import flow
from . import common


core_logger = logging.getLogger('core')


def icon_path(icon):
    """Return icon path for icon"""
    return os.path.join(util.icon_path('actions'), icon)


class IndirectNode(object):
    """
    Workaround wrapper to make Lambda supported by
    QTreeWidgetItem.setData.
    """

    def __init__(self, node):
        if node is not None:
            self._node_ref = weakref.ref(node)
        else:
            self._node_ref = None

    @property
    def node(self):
        if self._node_ref is None:
            return None
        else:
            return self._node_ref()


class ErrorView(QtGui.QTreeWidget):
    """Shows errors and output"""

    goto_node_requested = QtCore.Signal(flow.Node)

    colors = OrderedDict([
        ('Exception', QtGui.QColor.fromRgb(128, 49, 55, 255)),
        ('Error', QtGui.QColor.fromRgb(128, 49, 55, 255)),
        ('Warnings', QtGui.QColor.fromRgb(253, 182, 0, 255)),
        ('Notice', QtGui.QColor.fromRgb(0, 100, 0, 255))])
    icons = {
        'Exception': util.icon_path('node_error.svg'),
        'Error': util.icon_path('node_error.svg'),
        'Warnings': util.icon_path('node_warning.svg'),
        'Notice': util.icon_path('node_executed.svg')}

    def __init__(self, app_core, parent=None):
        super(ErrorView, self).__init__(parent)
        self._app_core = app_core
        self.setHeaderLabels(['Node', 'Message'])
        self.setColumnWidth(0, 200)
        self.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self._font = QtGui.QFont('Courier')
        fm = QtGui.QFontMetrics(self._font)
        self._row_height = fm.lineSpacing() + 1

        self._goto_selected_action = QtGui.QAction('Go to Node', self)
        self._goto_selected_action.triggered.connect(self._handle_goto_node)
        self.addAction(self._goto_selected_action)
        icon = QtGui.QIcon(icon_path('edit-trash-symbolic.svg'))
        self._remove_selected = QtGui.QAction(icon, 'Remove selected', self)
        self._remove_selected.triggered.connect(self.clear_selected)
        self.addAction(self._remove_selected)
        self.clear_action = QtGui.QAction(icon, 'Clear All', self)
        self.clear_action.setToolTip('Clear the entire Messages log')
        self.clear_action.triggered.connect(self.clear)
        self.addAction(self.clear_action)
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

    def _handle_goto_node(self):
        selected_items = self.selectedItems()
        for item in selected_items:
            node = item.data(0, QtCore.Qt.UserRole).node
            if node:
                self.goto_node_requested.emit(node)

    def _get_item(self, parent, messages):
        # TODO: Editable on Mac to workaround a Qt bug that otherwise results
        # in non-working keyboard shortcuts for Copy and Select all actions.

        label = QtGui.QTextEdit(parent=self)
        label.setPlainText(messages[1])
        label.setReadOnly(sys.platform != 'darwin')
        label.setFont(self._font)
        label.setAutoFillBackground(True)
        label.setFrameStyle(QtGui.QFrame.NoFrame)
        text_interaction_flags = (QtCore.Qt.TextSelectableByMouse |
                                  QtCore.Qt.TextSelectableByKeyboard)
        if sys.platform == 'darwin':
            text_interaction_flags |= QtCore.Qt.TextEditable
        label.setTextInteractionFlags(text_interaction_flags)
        item = QtGui.QTreeWidgetItem(parent, [messages[0], ''])
        item.setFont(0, self._font)
        label.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        num_rows = messages[1].count('\n') + 4  # Because 4 is a magic number!
        label.setMinimumHeight(self._row_height * num_rows)
        item.setSizeHint(1, label.size())
        return item, label

    def clear_selected(self):
        selected_indices = self.selectedIndexes()
        model = self.model()
        for index in selected_indices:
            if index.column() > 0:
                continue
            model.removeRow(index.row())

    @QtCore.Slot(six.text_type, dict)
    def add_node_output_message(self, full_uuid, output):
        if not (output.stderr or output.stdout or output.has_exception()):
            return

        def cleanup(s):
            return s.replace('\n', ' ').replace('\r', ' ').replace(
                '\t', ' ').strip()

        try:
            node = self._app_core.get_flode(full_uuid)
            name = node.name
        except (KeyError, AttributeError, ValueError):
            node = None
            name = full_uuid
        name = cleanup(name)

        levels = {}
        if output.has_exception():
            key, details = common.format_output_exception(output)
            levels[key] = (cleanup(output.exception.string), details)
        stderr = output.stderr
        if stderr:
            levels['Warnings'] = (cleanup(stderr), output.stderr_details)
        stdout = output.stdout
        if stdout:
            levels['Notice'] = (cleanup(stdout), output.stdout_details)

        for key, (brief, details) in levels.items():
            parent = QtGui.QTreeWidgetItem(None, [name, brief])
            # parent.setFont(1, self._font)
            indirect_node = IndirectNode(node)
            parent.setIcon(0, QtGui.QIcon(self.icons[key]))
            parent.setForeground(0, QtGui.QBrush(self.colors[key]))
            parent.setData(0, QtCore.Qt.UserRole, indirect_node)
            parent.setData(0, QtCore.Qt.ToolTipRole, six.text_type(
                datetime.datetime.now().isoformat()))

            if details:
                child, label = self._get_item(
                    parent, [key, details.strip()])
                parent.addChild(child)
                self.setItemWidget(child, 1, label)
                child.setData(0, QtCore.Qt.UserRole, indirect_node)
            self.addTopLevelItem(parent)

        self.scrollToBottom()

    @QtCore.Slot(six.text_type)
    def add_output_message(self, message):
        item, label = self._get_item(None, ['GENERAL', message])
        self.addTopLevelItem(item)
        self.setItemWidget(label)

    @QtCore.Slot(six.text_type, six.text_type)
    def add_message(self, full_uuid, message):
        core_logger.warning('ETV got a message?!')


class ErrorWidget(QtGui.QWidget):
    """Shows the errors and outputs togheter with a toolbar."""

    goto_node_requested = QtCore.Signal(flow.Node)

    def __init__(self, app_core, parent=None):
        super(ErrorWidget, self).__init__(parent=parent)
        self._app_core = app_core
        self._init_gui()

    def _init_gui(self):
        layout = QtGui.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self._error_view = ErrorView(
            self._app_core, parent=self)
        self._error_view.goto_node_requested.connect(
            self.goto_node_requested)

        self._toolbar = sywidgets.SyBaseToolBar(parent=self)
        self._toolbar.setOrientation(QtCore.Qt.Vertical)
        self._toolbar.setIconSize(QtCore.QSize(16, 16))
        self._toolbar.addAction(self._error_view.clear_action)
        layout.addWidget(self._toolbar)
        layout.addWidget(self._error_view)
        self.setLayout(layout)

    @QtCore.Slot(six.text_type, dict)
    def add_node_output_message(self, full_uuid, output):
        self._error_view.add_node_output_message(full_uuid, output)

    @QtCore.Slot(six.text_type)
    def add_output_message(self, message):
        self._error_view.add_output_message(message)

    @QtCore.Slot(six.text_type, six.text_type)
    def add_message(self, full_uuid, message):
        self._error_view.add_message(full_uuid, message)
