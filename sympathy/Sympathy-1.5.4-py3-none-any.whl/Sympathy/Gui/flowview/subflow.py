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
import functools

import six
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
import PySide.QtSvg as QtSvg

from .basenode import BaseNodeView
from .flowinfo import show_info
from .decoration import NodeStatusIconView
from .. import flow
from .. import user_commands
from .. import common
from sympathy.utils.prim import uri_to_path


class SubflowIconView(QtSvg.QGraphicsSvgItem):
    def __init__(self, pos, width, icon, parent=None):
        self._icon = icon
        super(SubflowIconView, self).__init__(parent)
        self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
        self.setCachingEnabled(True)
        self.setZValue(4)
        self.setPos(*pos)
        self.set_width(width)
        self._renderer = QtSvg.QSvgRenderer(uri_to_path(icon),
                                            parent=self)
        self.set_icon()

    def set_width(self, width):
        self._width = width

    def set_icon(self, icon=None):
        if icon is not None and icon != self._icon:
            self._icon = icon
            self._renderer.load(uri_to_path(icon))

        self.setSharedRenderer(self._renderer)
        w = self.renderer().defaultSize().width()
        if w > 0:
            scale = self._width / float(w)
            self.setScale(scale)


class SubflowView(BaseNodeView):
    edit_subflow_requested = QtCore.Signal(flow.Flow)
    _status_text = None

    def __init__(self, model, parent=None):
        super(SubflowView, self).__init__(model, parent)
        self._port_label = None
        self._init()
        self._init_status_text()

    def _init(self):
        r = self.boundingRect().adjusted(
            self._border_width, self._border_width,
            -self._border_width, -self._border_width)
        self._outline.moveTo(r.left(), r.top() + (r.height() / 2.0))
        self._outline.cubicTo(
            r.left(), r.top(), r.left(), r.top(),
            r.left() + (r.width() / 2.0), r.top())
        self._outline.cubicTo(
            r.right(), r.top(), r.right(), r.top(), r.right(),
            r.top() + (r.height() / 2.0))
        self._outline.cubicTo(
            r.right(), r.bottom(), r.right(), r.bottom(),
            r.left() + (r.width() / 2.0), r.bottom())
        self._outline.cubicTo(
            r.left(), r.bottom(), r.left(), r.bottom(), r.left(),
            r.top() + (r.height() / 2.0))
        self._overrides_icon = NodeStatusIconView(parent=self)
        self._overrides_icon.setPos(self._bounding_rect.right() - 16,
                                    self._bounding_rect.top() + 4)
        self._update_overrides_icon()

        icon_pos = (self._bounding_rect.left() + 5,
                    self._bounding_rect.top() + 5)
        icon_width = self._bounding_rect.width() - 10

        if self._model.has_svg_icon:
            self._icon = SubflowIconView(
                icon_pos, icon_width, self._model.icon, parent=self)

        self._update_tooltip()
        self._signals.connect(self._model,
                              self._model.description_changed,
                              self._update_tooltip)
        self._signals.connect(self._model,
                              self._model.name_changed,
                              self._update_tooltip)
        self._signals.connect(self._model,
                              self.model.icon_changed,
                              self._update_icon)
        self._signals.connect(self._model,
                              self.model.overrides_changed,
                              self._update_overrides_icon)
        self._init_actions()
        self._init_context_menu()

    def _init_actions(self):
        self._expand_subflow = QtGui.QAction('Expand Subflow', self)
        self._settings_action = QtGui.QAction('Settings', self)
        self._unlink_subflow_action = QtGui.QAction('Unlink Subflow', self)

        self._lock_subflow = QtGui.QAction(
            'Locked (Single process in memory)', self)
        self._lock_subflow.setCheckable(True)
        self._unlock_subflow = QtGui.QAction(
            'Unlocked (Multi process on disk)', self)
        self._unlock_subflow.setCheckable(True)
        self._save_subflow_action = QtGui.QAction('Save Subflow', self)
        self._save_subflow_as_link_action = QtGui.QAction(
            'Save Subflow As Link...', self)
        self._wizard_mode_config_action = QtGui.QAction(
            'Configure using Wizard dialog', self)
        self._tabbed_mode_config_action = QtGui.QAction(
            'Configure using Tabbed dialog', self)
        self._wizard_mode_config_action.triggered.connect(
            self._model.configure_with_wizard)
        self._tabbed_mode_config_action.triggered.connect(
            self._model.configure_with_tabbed)
        for action in (self._wizard_mode_config_action,
                       self._tabbed_mode_config_action):
            action.setCheckable(True)
        self._save_subflow_action.triggered.connect(self._handle_save_subflow)
        self._save_subflow_as_link_action.triggered.connect(
            self._handle_save_subflow_as_link)
        self._unlink_subflow_action.triggered.connect(
            self._handle_unlink_subflow)

        self._lock_subflow.triggered.connect(self._handle_lock_subflow)
        self._unlock_subflow.triggered.connect(self._handle_unlock_subflow)
        self._settings_action.triggered.connect(self._model.settings)
        self._expand_subflow.triggered.connect(self._handle_expand_subflow)

    def _init_status_text(self):
        self._status_text = QtGui.QGraphicsTextItem(self._format_status_text(),
                                                    parent=self)
        self._status_font = QtGui.QFont()
        self._status_font.setPixelSize(10)
        self._status_text.setFont(self._status_font)

    def _init_context_menu(self):
        self._context_menu = QtGui.QMenu()
        self._context_menu.addAction(self._configure_action)
        self._custom_config_menu = self._context_menu.addMenu(
            'Custom Configure')
        self._custom_config_menu.addAction(
            self._tabbed_mode_config_action)
        self._custom_config_menu.addAction(
            self._wizard_mode_config_action)
        self._context_menu.addAction(self._execute_action)
        self._context_menu.addAction(self._profile_action)
        self._context_menu.addAction(self._reload_action)
        self._context_menu.addAction(self._abort_action)
        self._context_menu.addSeparator()
        self._context_menu.addAction(self._edit_node_action)
        self._context_menu.addAction(self._settings_action)
        self._context_menu.addAction(self._show_info_action)
        self._context_menu.addSeparator()
        self._context_menu.addAction(self._copy_action)
        self._context_menu.addAction(self._cut_action)
        self._context_menu.addAction(self._delete_action)
        self._context_menu.addSeparator()
        self._context_menu.addAction(
            self._create_subflow_from_selection_action)
        if self._model.class_name != 'Lambda':
            self._context_menu.addAction(self._expand_subflow)

        self._exec_conf_menu = self._context_menu.addMenu(
            'Execution mode')
        self._exec_conf_menu.addAction(self._lock_subflow)
        self._exec_conf_menu.addAction(self._unlock_subflow)

        if self._model.class_name != 'Lambda':
            self._context_menu.addSeparator()
            self._context_menu.addAction(self._save_subflow_action)
            self._context_menu.addAction(self._save_subflow_as_link_action)
            self._context_menu.addAction(self._unlink_subflow_action)
        self._context_menu.addSeparator()

    def contextMenuEvent(self, event):
        deletable = self._model.is_deletable()
        self._expand_subflow.setEnabled(deletable)

        is_wizard = self._model.is_configured_with_wizard
        self._wizard_mode_config_action.setEnabled(not is_wizard)
        self._wizard_mode_config_action.setChecked(is_wizard)
        self._tabbed_mode_config_action.setEnabled(is_wizard)
        self._tabbed_mode_config_action.setChecked(not is_wizard)

        self._lock_subflow.setChecked(self._model.is_locked())
        self._unlock_subflow.setChecked(not self._model.is_locked())
        self._lock_subflow.setEnabled(not self._model.is_locked())
        self._unlock_subflow.setEnabled(self._model.is_locked())
        self._unlink_subflow_action.setEnabled(self._model.is_linked)
        self._exec_conf_menu.setEnabled(self._model.can_lock())

        self._create_subflow_from_selection_action.setEnabled(deletable)
        self._delete_action.setEnabled(deletable)
        self._cut_action.setEnabled(deletable)
        self._configure_action.setEnabled(self._model.is_configurable())
        self._settings_action.setEnabled(self._model.is_configurable())
        self._execute_action.setEnabled(self._model.is_executable())
        self._profile_action.setEnabled(self._model.is_profileable())
        self._reload_action.setEnabled(self._model.is_reloadable())
        self._abort_action.setEnabled(self._model.is_abortable())
        self._edit_node_action.setEnabled(self._model.can_edit())

        input_ports = self._model.creatable_parent_flow_inputs()
        input_menu = None
        if input_ports:
            input_menu = self._context_menu.addMenu(
                'Show Input Port')

        output_ports = self._model.creatable_parent_flow_outputs()
        output_menu = None
        if output_ports:
            output_menu = self._context_menu.addMenu(
                'Show Output Port')

        action_funcs = {}
        menu_actions = {}

        for ports, menu, basefunc in [
                (input_ports, input_menu, self._create_input),
                (output_ports, output_menu, self._create_output)]:

            for port_ in ports:
                action = QtGui.QAction(
                    '{}[{}]'.format(port_.description, port_.index), self)
                func = functools.partial(basefunc, port_)
                action_funcs[action] = func
                action.triggered.connect(func)
                menu.addAction(action)
                menu_actions.setdefault(menu, set()).add(action)

        self._context_menu.exec_(event.screenPos())

        for action, func in action_funcs.items():
            action.triggered.disconnect(func)

        for menu, actions in menu_actions.items():
            for action in actions:
                menu.removeAction(action)

        for menu in [input_menu, output_menu]:
            if menu:
                self._context_menu.removeAction(menu.menuAction())

    def _create_input(self, port):
        cmd = user_commands.CreateParentInputPortCommand(port)
        self.model.flow.undo_stack().push(cmd)

    def _create_output(self, port):
        cmd = user_commands.CreateParentOutputPortCommand(port)
        self.model.flow.undo_stack().push(cmd)
        port.create_parent_port()

    @QtCore.Slot()
    def _show_info_requested(self):
        show_info(self._model)

    @QtCore.Slot()
    def _edit_node_requested(self):
        self.edit_subflow_requested.emit(self._model)

    @QtCore.Slot()
    def _node_help_requested(self):
        pass

    def _format_status_text(self):
        tot, finished = self._model.execution_status()
        return ('{}/{}'.format(finished, tot) if not self._model.is_atom()
                else '')

    @QtCore.Slot()
    def _node_state_changed(self):
        if self._status_text is not None:
            self._status_text.setPlainText(self._format_status_text())
        super(SubflowView, self)._node_state_changed()

    def _update_overrides_icon(self):
        if self._model.override_parameters:
            self._overrides_icon.set_icon_type('Overrides')
        else:
            self._overrides_icon.set_icon_type('None')

    def _update_icon(self):
        self._icon.set_icon(self._model.icon)

    def _tooltip(self):
        if self._model.is_broken_link():
            description = u'This subflow could not be found.'
        else:
            description = self._model.description.rstrip()
        if self._model.is_linked:
            name = self._model.source_display_name
        else:
            name = self._model.name

        return u'<b>{}</b>{}'.format(
            self._html_escape(name),
            '<br/>{}'.format(self._html_escape(description))
            if description else '')

    @QtCore.Slot()
    def _handle_lock_subflow(self):
        cmd = user_commands.EditSubflowLockStateCommand(self._model, True)
        self._model.undo_stack().push(cmd)

    @QtCore.Slot()
    def _handle_unlock_subflow(self):
        cmd = user_commands.EditSubflowLockStateCommand(self._model, False)
        self._model.undo_stack().push(cmd)

    @QtCore.Slot()
    def _handle_unlink_subflow(self):
        cmd = user_commands.UnlinkSubflowCommand(self._model)
        self._model.undo_stack().push(cmd)

    @QtCore.Slot()
    def _handle_expand_subflow(self):
        flow_ = self._model.flow
        cmd = user_commands.ExpandSubflowCommand(self._model)
        flow_.undo_stack().push(cmd)

    @QtCore.Slot()
    def _handle_save_subflow(self):
        filename = self._model.filename

        if not filename:
            try:
                common.persistent_save_flow_to_file(self._model)
            except common.SaveCancelled:
                return

    @QtCore.Slot()
    def _handle_save_subflow_as_link(self):
        old_filename = self._model.filename
        try:
            filename = common.persistent_save_flow_to_file(self._model)
        except common.SaveCancelled:
            return

        if old_filename != filename:
            cmd = user_commands.LinkSubflowCommand(
                self._model, filename)
            self._model.undo_stack().push(cmd)

    @QtCore.Slot(six.text_type)
    def _handle_label_edited(self, label):
        if self._model.link_label != label:
            cmd = user_commands.EditNodeLabelCommand(
                self._model, self._model.link_label, label)
            self._model.flow.undo_stack().push(cmd)
        else:
            self._label.set_label(self._model.display_name)
