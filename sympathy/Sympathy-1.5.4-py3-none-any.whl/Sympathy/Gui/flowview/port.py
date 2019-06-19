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
import cgi
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
import PySide.QtSvg as QtSvg

from .types import ElementViewInterface, get_label
from .decoration import NodeStatusIconView
from . import theme
from .. import flow
from .. import user_commands
from sympathy.utils import uuid_generator


class Info(QtGui.QDialog):

    def __init__(self, flowio_model, parent=None, flags=0):
        super(Info, self).__init__(parent, flags)
        self._model = flowio_model
        self._init()

    def _init(self):
        def pre(x):
            return '<pre>{}</pre>'.format(cgi.escape(x, quote=True))

        self.setWindowTitle(u'Information: {}'.format(self._model.name))
        self._main_layout = QtGui.QVBoxLayout()
        layout = QtGui.QFormLayout()
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        layout.addRow('Name', get_label(self._model.name))
        namespace_uuid, item_uuid = uuid_generator.split_uuid(
            self._model.full_uuid)
        layout.addRow('Type', get_label(self._model.datatype.html))
        layout.addRow('Scheme', get_label(self._model.scheme))
        layout.addRow('Description', get_label(self._model.description))
        layout.addRow('Filename', get_label(
            os.path.basename(self._model.filename)))
        layout.addRow('Namespace UUID', get_label(pre(namespace_uuid)))
        layout.addRow('Port UUID', get_label(pre(item_uuid)))
        layout.addRow('Is connected', get_label(
            six.text_type(self._model.is_connected())))

        self._main_layout.addLayout(layout)
        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        self._main_layout.addWidget(button_box)
        self.setLayout(self._main_layout)


class PortView(QtGui.QGraphicsObject, ElementViewInterface):
    """An input or output port"""

    highlight_on = QtCore.Signal()
    highlight_off = QtCore.Signal()
    connection_start_requested = QtCore.Signal(object)
    connection_end_requested = QtCore.Signal(object)
    position_changed = QtCore.Signal(QtCore.QPointF)
    open_add_context_requested = QtCore.Signal(QtGui.QGraphicsSceneMouseEvent)

    def __init__(self, model, parent=None):
        QtGui.QGraphicsObject.__init__(self, parent)
        ElementViewInterface.__init__(self, model)
        size = self._model.size
        self._bounding_rect = QtCore.QRectF(0, 0, size.width(), size.height())
        self._port_symbol = None
        self._highlight = False
        self.renderer = QtSvg.QSvgRenderer(parent=self)
        self._init()
        self._init_state_machine()
        self._init_actions()
        self._init_signalling()
        self._init_context_menu()

    def _init(self):
        self.set_position(self._model.position)
        self.setAcceptHoverEvents(True)
        self.setTransformOriginPoint(self.boundingRect().center())
        self.setGraphicsEffect(None)

        self._port_viewer_icon = NodeStatusIconView(parent=self)
        self._update_port_viewer_icon_position()
        self._port_viewer_icon.setScale(0.7)
        self._port_viewer_icon.setZValue(3)
        self.set_port_viewer_icon(self._model.port_viewer_open)

        self._outline = QtGui.QPainterPath()
        self._outline.addEllipse(self.boundingRect())
        self._node_color = theme.instance().midlight_color
        self._border_color = theme.instance().mid_color
        self._border_width = 1.0
        self._brush = QtGui.QBrush(self._node_color)
        self._pen = QtGui.QPen(self._border_color, self._border_width)
        self._set_port_type(self._model.datatype)
        # Make sure that all signals have done what they should
        # before trying to build the tooltip.
        QtCore.QTimer.singleShot(0, self._update_tool_tip)

    def _delete(self):
        if self._model.node.type == flow.Type.Flow:
            if self._model.type == flow.Type.InputPort:
                cmd = user_commands.DeleteParentInputPortCommand(self._model)
            elif self._model.type == flow.Type.OutputPort:
                cmd = user_commands.DeleteParentOutputPortCommand(self._model)
            else:
                assert False, 'Unknown port type of: {}.'.format(self._model)
        else:
            if self._model.type == flow.Type.InputPort:
                cmd = user_commands.DeleteInputPortCommand(self._model)
            elif self._model.type == flow.Type.OutputPort:
                cmd = user_commands.DeleteOutputPortCommand(self._model)
            else:
                assert False, 'Unknown port type of: {}.'.format(self._model)

        self._model.flow.undo_stack().push(cmd)

    def _create(self):
        if self._model.type == flow.Type.InputPort:
            cmd = user_commands.DuplicateInputPortCommand(self._model)
        elif self._model.type == flow.Type.OutputPort:
            cmd = user_commands.DuplicateOutputPortCommand(self._model)
        else:
            assert False, 'Unknown port type of: {}.'.format(self._model)
        self._model.flow.undo_stack().push(cmd)

    def _init_actions(self):
        self._copy_file_to_clipboard_action = QtGui.QAction(
            'Copy File Path To Clipboard', self)
        self._copy_file_to_clipboard_action.triggered.connect(
            self._copy_file_to_clipboard)

        self._show_info_action = QtGui.QAction('Properties', self)
        self._open_file_path_action = QtGui.QAction('Open File Path', self)
        self._open_file_path_action.triggered.connect(self._open_file_path)

        self._create_port_action = QtGui.QAction('Duplicate Port', self)
        self._delete_port_action = QtGui.QAction('Delete Port', self)
        self._create_port_action.triggered.connect(self._create)
        self._delete_port_action.triggered.connect(self._delete)
        self._show_info_action.triggered.connect(self._show_info_requested)

    def _init_context_menu(self):
        self._context_menu = QtGui.QMenu()
        self._context_menu.addAction(self._copy_file_to_clipboard_action)
        self._context_menu.addAction(self._open_file_path_action)
        self._context_menu.addAction(self._create_port_action)
        self._context_menu.addAction(self._delete_port_action)
        self._context_menu.addAction(self._show_info_action)

    def _set_port_type(self, datatype):
        if self._port_symbol is not None and self.scene() is not None:
            self.scene().removeItem(self._port_symbol)
            self._port_symbol.deleteLater()
        self.prepareGeometryChange()
        self.renderer.load(QtCore.QByteArray(datatype.icon))
        self._port_symbol = QtSvg.QGraphicsSvgItem(self)
        self._port_symbol.setSharedRenderer(self.renderer)

        s = self._model.size
        r = self._port_symbol.boundingRect()
        scale = s.height() / r.height()

        if self.model.type == flow.Type.InputPort:
            self._bounding_rect.setX(- r.width() * scale + s.width())
            self._bounding_rect.setWidth(r.width() * scale)
        else:
            self._bounding_rect.setWidth(r.width() * scale)

        self._port_symbol.scale(scale, scale)
        if self.model.type == flow.Type.InputPort:
            self._port_symbol.setX(- r.width() * scale + s.width())
        self._update_port_viewer_icon_position()

    def _init_signalling(self):

        self._signals.connect(
            self._model,
            self._model.position_changed[QtCore.QPointF],
            self.set_position)

        self._signals.connect(
            self._model,
            self._model.datatype_changed,
            self._handle_datatype_changed)

        self._signals.connect(
            self._model,
            self._model.description_changed,
            self._update_tool_tip)

        self._signals.connect(
            self._model,
            self._model.viewer_changed,
            self._handle_viewer_changed)

    def _init_state_machine(self):
        # We use a state machine for highlighting the port when the mouse
        # passes over
        self._state_machine = QtCore.QStateMachine()
        self._normal_state = QtCore.QState(self._state_machine)
        self._highlighted_state = QtCore.QState(self._state_machine)

        # The Normal to Highlighted state transition
        self._normal_to_highlight = self._normal_state.addTransition(
            self.highlight_on, self._highlighted_state)

        self._anim_highlight_scale = QtCore.QPropertyAnimation(self, b'scale')
        self._anim_highlight_scale.setDuration(125)
        self._curve_scale = QtCore.QEasingCurve(QtCore.QEasingCurve.OutBack)
        self._curve_scale.setOvershoot(4.0)
        self._anim_highlight_scale.setEasingCurve(self._curve_scale)
        self._anim_highlight_scale.setEndValue(1.5)
        self._normal_to_highlight.addAnimation(self._anim_highlight_scale)

        # The Highlighted back to Normal state transition
        self._highlight_to_normal = self._highlighted_state.addTransition(
            self.highlight_off, self._normal_state)
        self._anim_normal_scale = QtCore.QPropertyAnimation(self, b'scale')
        self._anim_normal_scale.setDuration(125)
        self._anim_normal_scale.setEasingCurve(self._curve_scale)
        self._anim_normal_scale.setEndValue(1.0)
        self._highlight_to_normal.addAnimation(self._anim_normal_scale)

        self._state_machine.setInitialState(self._normal_state)
        self._state_machine.start()

    def boundingRect(self):
        return self._bounding_rect

    def paint(self, painter, options, widget=None):
        pass

    def set_port_viewer_icon(self, state):
        if state:
            self._port_viewer_icon.set_icon_type('Open')
        else:
            self._port_viewer_icon.set_icon_type('None')
        self.update()

    def set_this_z(self):
        self.setZValue(6)

    def set_other_z(self):
        self.setZValue(5)

    def reset_z(self):
        self.setZValue(3)

    def _update_port_viewer_icon_position(self):
        self._port_viewer_icon.setPos(self._bounding_rect.left(),
                                      self._bounding_rect.top() - 8)

    @QtCore.Slot()
    def _show_info_requested(self):
        dialog = Info(self._model)
        dialog.exec_()

    @QtCore.Slot()
    def _handle_datatype_changed(self):
        self._set_port_type(self._model.datatype)
        self._update_tool_tip()
        self.notify_position_changed()

    @QtCore.Slot(bool)
    def _handle_viewer_changed(self, state):
        self.set_port_viewer_icon(state)

    @QtCore.Slot()
    def _copy_file_to_clipboard(self):
        self._mime_data = QtCore.QMimeData()
        self._mime_data.setText(self._model.filename)
        QtGui.QApplication.clipboard().setMimeData(self._mime_data)

    @QtCore.Slot()
    def _open_file_path(self):
        QtGui.QDesktopServices.openUrl(
            'file:///' + os.path.dirname(self._model.filename))

    @QtCore.Slot(QtCore.QPointF)
    def set_position(self, position):
        self.setPos(position)
        self.notify_position_changed()

    def connection_position(self):
        offset = 2 if not self._highlight else 4.5
        r = self.sceneBoundingRect()
        w = self.renderer.viewBox().width() * 0.625 + offset
        x = (r.left() + w if self.model.type == flow.Type.OutputPort
             else r.right() - w)
        p = r.center()
        p.setX(x)
        return p

    def notify_position_changed(self):
        self.position_changed.emit(self.connection_position())

    @QtCore.Slot()
    def _update_tool_tip(self):
        self.setToolTip('<b>%s</b><br/><i>%s</i><br/>File: %s' % (
            self._model.description, self._model.datatype.html,
            os.path.basename(self._model.filename)))

    def hoverEnterEvent(self, event):
        self.prepareGeometryChange()
        self.highlight_on.emit()
        self._highlight = True

    def hoverLeaveEvent(self, event):
        self.prepareGeometryChange()
        self.highlight_off.emit()
        self._highlight = False

    def mouseMoveEvent(self, event):
        if not self.scene() and not self.scene().parent():
            return super(PortView, self).mouseMoveEvent(event)

        flowview = self.scene().parent()
        transient_connection = flowview._transient_connection
        if transient_connection:
            port_view = None
            valid_port = False
            item = self.scene().itemAt(event.scenePos())
            if item is not None and isinstance(item.parentItem(), PortView):
                port_view = item.parentItem()
                valid_port = self._model.flow.connection_is_allowed(
                    *flow.connection_direction(self._model, port_view.model))
            transient_connection.set_valid_connection(
                valid_port, port=port_view)
        super(PortView, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            event.ignore()
            return
        if (self.model.type == flow.Type.InputPort and
                self.model.is_connected()):
            # Do nothing
            event.accept()
            return

        event.accept()
        self.setCursor(QtCore.Qt.CrossCursor)
        self.connection_start_requested.emit(self)

    def mouseReleaseEvent(self, event):
        self.setCursor(QtCore.Qt.ArrowCursor)
        port_view = self.scene().itemAt(event.scenePos())
        if ((port_view is None or
             not isinstance(port_view.parentItem(), PortView))):
            event.accept()
            self.open_add_context_requested.emit(event)
        elif not port_view:
            self.connection_end_requested.emit(None)
            event.ignore()
        else:
            if isinstance(port_view.parentItem(), PortView):
                port_view = port_view.parentItem()
            if (isinstance(port_view, PortView) and
                    self._model.flow.connection_is_allowed(
                        *flow.connection_direction(
                            self._model, port_view.model))):

                self.connection_end_requested.emit(port_view)
                event.accept()
            else:
                self.connection_end_requested.emit(None)
                event.ignore()

    def mouseDoubleClickEvent(self, event):
        port = self._model
        if port.type == flow.Type.OutputPort:
            try:
                port.node.port_viewer(port)
            except AttributeError:
                pass

    def contextMenuEvent(self, event):
        self._create_port_action.setEnabled(self._model.can_create())
        self._delete_port_action.setEnabled(self._model.can_delete())
        self._context_menu.exec_(event.screenPos())

    def highlight(self, active):
        self._highlight = active
        if active:
            self.highlight_on.emit()
        else:
            self.highlight_off.emit()
