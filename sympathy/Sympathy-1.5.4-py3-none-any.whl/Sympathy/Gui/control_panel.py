# This file is part of Sympathy for Data.
# Copyright (c) 2017 Combine Control Systems AB
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

from PySide import QtCore, QtGui
import os
from . import util
from . import signals


def icon_path(icon):
    return os.path.join(util.icon_path('actions'), icon)


class ControlPanel(QtGui.QToolBar):
    new_signal = QtCore.Signal()
    open_signal = QtCore.Signal()

    def __init__(self, parent):
        super(ControlPanel, self).__init__('Control Panel', parent=parent)
        self._actions = []
        self._separators = []
        self._flow_signals = signals.SignalHandler()
        self._progress_signals = signals.SignalHandler()

        self._new_action = self._add_action(
            '&New Flow', self.new_signal,
            icon_path('document-new-symbolic.svg'), append=False)
        self._open_action = self._add_action(
            '&Open', self.open_signal, icon_path('document-open-symbolic.svg'),
            append=False)
        self._save_action = self._add_action(
            '&Save', None, icon_path('document-save-symbolic.svg'),
            QtGui.QKeySequence.Save)
        self._save_as_action = self._add_action(
            'Save &As...', None,
            icon_path('document-save-as-symbolic.svg'),
            QtGui.QKeySequence.SaveAs)

        self._add_toolbar_separator()

        self._execute_action = self._add_action(
            '&Execute flow', None,
            icon_path('media-playback-start-symbolic.svg'),
            QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_R))
        self._profile_action = self._add_action(
            '&Profile flow', None,
            icon_path('media-playback-pstart-symbolic.svg'),
            QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_P),
            add=False)
        self._stop_action = self._add_action(
            '&Stop', None,
            icon_path('media-playback-stop-symbolic.svg'))
        self._reload_action = self._add_action(
            '&Reload', None,
            icon_path('view-refresh-symbolic.svg'),
            QtGui.QKeySequence(
                int(QtCore.Qt.CTRL) + int(QtCore.Qt.ALT) +
                int(QtCore.Qt.Key_R)))

        self._add_toolbar_separator()

        self._cut_action = self._add_action(
            'Cu&t', None, icon_path('edit-cut-symbolic.svg'))
        self._copy_action = self._add_action(
            '&Copy', None, icon_path('edit-copy-symbolic.svg'))
        # self._paste_action = self._add_action(
        #     '&Paste', None, icon_path('edit-paste-symbolic.svg'))
        self._delete_action = self._add_action(
            '&Delete', None,
            icon_path('edit-trash-symbolic.svg'))

        self._add_toolbar_separator()

        self._insert_node_action = self._add_action(
            'Insert Node', None,
            icon_path('insert-node-symbolic.svg'),
            QtGui.QKeySequence(
                int(QtCore.Qt.CTRL) + int(QtCore.Qt.SHIFT) +
                int(QtCore.Qt.Key_N)))
        self._insert_text_field_action = self._add_action(
            'Insert Text Field', None,
            icon_path('insert-text-symbolic.svg'))
        self._insert_text_field_action.setCheckable(True)

        self._add_toolbar_spacer()

        self._progress_status = QtGui.QLabel()
        self._progress_status_action = QtGui.QWidgetAction(self)

        policy = self._progress_status.sizePolicy()
        policy.setHorizontalPolicy(QtGui.QSizePolicy.Minimum)
        self._progress_status.setSizePolicy(policy)
        self._progress_status_action.setDefaultWidget(self._progress_status)
        self.addAction(self._progress_status_action)
        self._progress_status_action.setVisible(False)

        self._progress_action = QtGui.QWidgetAction(self)
        self._progress_bar = QtGui.QProgressBar()
        policy = self._progress_bar.sizePolicy()
        policy.setHorizontalPolicy(QtGui.QSizePolicy.Minimum)
        self._progress_bar.setSizePolicy(policy)
        self._progress_action.setDefaultWidget(self._progress_bar)
        self.addAction(self._progress_action)
        self._progress_action.setVisible(False)
        self._add_toolbar_separator()

        self._zoom_in_action = self._add_action(
            'Zoom &In', None, icon_path('zoom-in-symbolic.svg'),
            QtGui.QKeySequence.ZoomIn)
        self._zoom_out_action = self._add_action(
            'Zoom &Out', None, icon_path(
                'zoom-out-symbolic.svg'),
            QtGui.QKeySequence.ZoomOut)
        self._zoom_restore_action = self._add_action(
            'Zoom &Restore', None,
            icon_path('zoom-original-symbolic.svg'),
            QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_0))
        self._zoom_fit_all_action = self._add_action(
            'Zoom Fit &All', None,
            icon_path('zoom-fit-best-symbolic.svg'),
            QtGui.QKeySequence(
                int(QtCore.Qt.CTRL) + int(QtCore.Qt.SHIFT) +
                int(QtCore.Qt.Key_2)))
        self._zoom_fit_selection_action = self._add_action(
            'Zoom To &Selection', None,
            icon_path('zoom-fit-selection-symbolic.svg'),
            QtGui.QKeySequence(
                int(QtCore.Qt.CTRL) + int(QtCore.Qt.SHIFT) +
                int(QtCore.Qt.Key_1)))

        # Not in the toolbar:
        self._close_action = QtGui.QAction('Close', self)
        self._close_action.setIcon(
            QtGui.QIcon(icon_path('window-close-symbolic.svg')))
        self._close_action.setShortcut(QtGui.QKeySequence.Close)

        self.setIconSize(QtCore.QSize(16, 16))
        self._toggle_control_panel_action = self.toggleViewAction()
        self._toggle_control_panel_action.setText("&Control Panel")

    def _add_action(self, name, signal=None, icon=None, shortcut=None,
                    append=True, add=True):
        action = QtGui.QAction(name, self)
        if signal is not None:
            action.triggered.connect(signal)
        if icon:
            action.setIcon(QtGui.QIcon(icon))
        if shortcut:
            action.setShortcut(shortcut)
        if add:
            self.addAction(action)
        if append:
            self._actions.append(action)
        return action

    def _add_toolbar_separator(self, append=True):
        action = self.addSeparator()
        if append:
            self._separators.append(action)

    def _add_toolbar_spacer(self):
        spacer = QtGui.QWidget(parent=self)
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding,
                             QtGui.QSizePolicy.Expanding)
        self.addWidget(spacer)

    def file_menu_actions(self):
        return [self._save_action, self._save_as_action, self._close_action]

    def edit_menu_actions(self):
        return [self._insert_node_action,
                self._insert_text_field_action]

    def control_menu_actions(self):
        return [self._execute_action, self._profile_action, self._stop_action,
                self._reload_action]

    def view_menu_actions(self):
        return [self._toggle_control_panel_action,
                None,
                self._zoom_in_action,
                self._zoom_out_action, self._zoom_restore_action,
                self._zoom_fit_all_action, self._zoom_fit_selection_action]

    def set_current_flow(self, flow_window):
        self._flow_signals.disconnect_all()

        has_flow = flow_window is not None
        for action in self._actions + self._separators:
            action.setVisible(has_flow)

        if not has_flow:
            return

        for action, handler in [
                (self._save_action, flow_window.save_signal),
                (self._save_as_action, flow_window.save_as_signal),
                (self._close_action, flow_window.close_signal),

                # (self._select_all_action, flow_window.select_all_signal),
                (self._cut_action, flow_window.cut_signal),
                (self._copy_action, flow_window.copy_signal),
                # (self._paste_action, flow_window.paste_signal),
                (self._delete_action, flow_window.delete_signal),
                (self._insert_node_action, flow_window.insert_node_signal),

                (self._execute_action, flow_window.execute_signal),
                (self._profile_action, flow_window.profile_signal),
                (self._stop_action, flow_window.stop_signal),
                (self._reload_action, flow_window.reload_signal),

                (self._zoom_in_action, flow_window.zoom_in_signal),
                (self._zoom_out_action, flow_window.zoom_out_signal),
                (self._zoom_fit_all_action, flow_window.zoom_fit_all_signal),
                (self._zoom_fit_selection_action,
                 flow_window.zoom_fit_selection_signal),
                (self._zoom_restore_action, flow_window.zoom_restore_signal)]:

            self._flow_signals.connect(
                flow_window, action.triggered, handler)

        # Needs to be connected using toggled.
        # For some reason, disconnecting when using triggered does not work.

        self._flow_signals.connect_reference(
            flow_window, [
                (self._insert_text_field_action.toggled,
                 flow_window.toggle_insert_text_field_signal),
                (flow_window.inserting_text_field_signal,
                 self._insert_text_field_action.setChecked),
                (flow_window.moving_signal,
                 self._insert_text_field_action.setDisabled)])

    def set_current_progress_object(self, progress_object):
        self._progress_signals.disconnect_all()
        self._progress_action.setVisible(True)
        self._progress_status_action.setVisible(True)
        self._progress_bar.setToolTip(progress_object.desc)
        self._progress_status.setToolTip(progress_object.desc)
        self._progress_bar.setValue(0)
        self._progress_status.setText(progress_object.name)

        self._progress_signals.connect(
            progress_object, progress_object.progress,
            self._progress_bar.setValue)
        self._progress_signals.connect(
            progress_object, progress_object.done, self._progress_object_done)

        progress_object.done.connect(self._progress_object_done)

    def _progress_object_done(self, status):
        self._progress_signals.disconnect_all()
        self._progress_action.setVisible(False)
        self._progress_status_action.setVisible(False)
        self._progress_bar.setToolTip('')
        self._progress_status.setToolTip('')
        self._progress_bar.reset()
        self._progress_status.setText('')
