# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
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
import os
import six
import functools
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

from . import flowview
from . import flow


class FlowWindow(QtGui.QMainWindow):
    new_signal = QtCore.Signal()
    open_signal = QtCore.Signal()
    save_signal = QtCore.Signal()
    save_as_signal = QtCore.Signal()
    close_signal = QtCore.Signal()
    close_tree_signal = QtCore.Signal(flow.Flow)
    execute_signal = QtCore.Signal()
    profile_signal = QtCore.Signal()
    stop_signal = QtCore.Signal()
    reload_signal = QtCore.Signal()
    copy_signal = QtCore.Signal()
    cut_signal = QtCore.Signal()
    delete_signal = QtCore.Signal()
    paste_signal = QtCore.Signal()
    zoom_in_signal = QtCore.Signal()
    zoom_out_signal = QtCore.Signal()
    zoom_restore_signal = QtCore.Signal()
    zoom_fit_all_signal = QtCore.Signal()
    zoom_fit_selection_signal = QtCore.Signal()
    edit_subflow_requested = QtCore.Signal(flow.Flow)
    select_all_signal = QtCore.Signal()
    redo_signal = QtCore.Signal()
    undo_signal = QtCore.Signal()
    help_requested = QtCore.Signal(six.text_type)
    insert_node_signal = QtCore.Signal()
    toggle_insert_text_field_signal = QtCore.Signal(bool)
    inserting_text_field_signal = QtCore.Signal(bool)
    moving_signal = QtCore.Signal(bool)

    def __init__(self, flow_, gui_manager, app_core, parent=None):
        super(FlowWindow, self).__init__(parent, QtCore.Qt.Window)
        self._flow = flow_
        self._gui_manager = gui_manager
        self._app_core = app_core

        self._flow_view = flowview.FlowView(
            self._flow, self._app_core, parent=self)
        self._flow_view.edit_subflow_requested[flow.Flow].connect(
            self.edit_subflow_requested)
        self._flow_view.help_requested[six.text_type].connect(
            self.help_requested)

        self._flow.before_remove.connect(self._before_remove)
        self.setCentralWidget(self._flow_view)

        self._init_flow_signals()
        self._init_dock_widgets()

        self._redo_action = (
            self._flow_view.model.undo_stack().createRedoAction(
                self._flow_view.model, "&Redo"))
        self._redo_action.setShortcut(QtGui.QKeySequence.Redo)
        self._undo_action = (
            self._flow_view.model.undo_stack().createUndoAction(
                self._flow_view.model, "&Undo"))
        self._undo_action.setShortcut(QtGui.QKeySequence.Undo)

        self._cut_action = self._new_action(
            'Cu&t', QtGui.QKeySequence.Cut)
        self._cut_action.triggered.connect(self._flow_view.handle_cut)
        self._copy_action = self._new_action(
            '&Copy', QtGui.QKeySequence.Copy)
        self._copy_action.triggered.connect(self._flow_view.handle_copy)
        self._paste_action = self._new_action(
            '&Paste', QtGui.QKeySequence.Paste)
        self._paste_action.triggered.connect(
            self._flow_view.handle_paste_at_cursor)
        self._delete_action = self._new_action(
            '&Delete', QtGui.QKeySequence.Delete)
        self._delete_action.triggered.connect(self._flow_view.handle_delete)

        self._select_all_action = self._new_action(
            'Select &All',
            QtGui.QKeySequence.SelectAll)
        self._select_all_action.triggered.connect(self._flow_view.select_all),

    def _new_action(
            self, text, shortcut,
            shortcut_ctx=QtCore.Qt.WidgetWithChildrenShortcut):
        action = QtGui.QAction(text, self)
        action.setShortcut(shortcut)
        action.setShortcutContext(shortcut_ctx)
        self.addAction(action)
        return action

    def _init_flow_signals(self):
        self.zoom_in_signal.connect(self._flow_view.zoom_in)
        self.zoom_out_signal.connect(self._flow_view.zoom_out)
        self.zoom_restore_signal.connect(self._flow_view.zoom_restore)
        self.zoom_fit_all_signal.connect(self._flow_view.zoom_fit_all)
        self.zoom_fit_selection_signal.connect(
            self._flow_view.zoom_fit_selection)
        self.copy_signal.connect(self._flow_view.handle_copy)
        self.cut_signal.connect(self._flow_view.handle_cut)
        self.delete_signal.connect(self._flow_view.handle_delete)
        self.paste_signal.connect(self._flow_view.handle_paste_at_cursor)
        self.select_all_signal.connect(self._flow_view.select_all)
        self.stop_signal.connect(self._flow_view.handle_stop)
        self.reload_signal.connect(self._flow_view.handle_reload)
        self.execute_signal.connect(self._flow_view.handle_execute_all)

        self.execute_signal.connect(self._flow.execute_all_nodes)
        self.profile_signal.connect(self._flow.profile_all_nodes)

        self.insert_node_signal.connect(
            self._flow_view.insert_node_via_popup)
        self.toggle_insert_text_field_signal.connect(
            self._flow_view.toggle_insert_text_field)
        self._flow_view.state_changed.connect(
            lambda: self.inserting_text_field_signal.emit(
                self._flow_view.is_inserting_text_field))
        self._flow_view.state_changed.connect(
            lambda: self.moving_signal.emit(self._flow_view.is_moving))
        self.open_signal.connect(self._handle_open_flow)
        self.save_signal.connect(
            functools.partial(self._gui_manager.save_flow, self._flow))
        self.save_as_signal.connect(
            functools.partial(self._gui_manager.save_as_flow, self._flow))

        self.close_signal.connect(self.close_flow)

    def _init_dock_widgets(self):
        self._undo_dock_widget = QtGui.QDockWidget('Undo stack', parent=self)
        self._undo_dock_widget.hide()
        self._undo_dock_widget.setFeatures(
            QtGui.QDockWidget.DockWidgetClosable |
            QtGui.QDockWidget.DockWidgetMovable)
        self.addDockWidget(
            QtCore.Qt.RightDockWidgetArea, self._undo_dock_widget)
        self._init_undo_dock()
        self._toggle_dock_widget_action = (
            self._undo_dock_widget.toggleViewAction())
        self._toggle_dock_widget_action.setText("&Undo stack")

    @QtCore.Slot()
    def _init_undo_dock(self):
        self._undo_view = QtGui.QUndoView(self._flow.undo_stack(),
                                          parent=self._undo_dock_widget)
        self._undo_dock_widget.setWidget(self._undo_view)

    def _handle_zoom_to_node(self, node):
        self._flow_view._handle_zoom_to_node(node)

    @QtCore.Slot()
    def _handle_open_flow(self):
        flow_filename = self._flow.root_or_linked_flow_filename
        if flow_filename:
            default_directory = os.path.dirname(flow_filename)
        else:
            default_directory = ''
        self._gui_manager.open_flow(default_directory)

    @QtCore.Slot()
    def close_flow(self):
        return self._gui_manager.close_tree(self._flow, False)

    def _before_remove(self):
        return self._gui_manager.close_tree(self._flow, True)

    def close_flow_view(self):
        self._flow_view.close()

    def flow(self):
        return self._flow

    def name(self):
        return self._flow.display_name

    def filename(self):
        return self._flow.filename

    def edit_menu_actions(self):
        return [self._undo_action, self._redo_action, None,
                self._select_all_action, None, self._cut_action,
                self._copy_action, self._paste_action, self._delete_action,
                None]

    def view_menu_actions(self):
        return [self._toggle_dock_widget_action]

    def preferences_updated(self):
        self._flow_view.preferences_updated()
