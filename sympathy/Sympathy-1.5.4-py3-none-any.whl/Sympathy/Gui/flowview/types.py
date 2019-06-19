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

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

from .. import signals
from .. import user_commands
from .. import flow
from . import theme
from . import grid


class ElementViewInterface(object):
    """An interface for all views of flow elements."""

    def __init__(self, model):
        self._model = model
        self._signals = signals.SignalHandler()

    @property
    def model(self):
        """flow.* model corresponding to the view."""
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    def remove(self):
        """Remove the view from the scene."""
        self._signals.disconnect_all(self._model)


class MovableElementViewInterface(QtGui.QGraphicsObject, ElementViewInterface):
    """Interface for all views of flow elements that can be independently moved
    around.
    """

    cut_requested = QtCore.Signal(ElementViewInterface)
    copy_requested = QtCore.Signal(ElementViewInterface)
    delete_requested = QtCore.Signal(ElementViewInterface)
    mouse_pressed = QtCore.Signal()
    mouse_released = QtCore.Signal()

    def __init__(self, model, parent=None):
        QtGui.QGraphicsObject.__init__(self, parent)
        ElementViewInterface.__init__(self, model)
        self.__init()
        self.__init_actions()
        self._init_move_state_machine()

    def __init(self):
        self._old_position = QtCore.QPointF()
        size = self._model.size
        self._bounding_rect = QtCore.QRectF(0, 0, size.width(), size.height())
        self.set_position(self._model.position)

        self._outline = QtGui.QPainterPath()
        self._selection_layer = SelectionLayer(
            outline=self._outline, parent=self)
        self._selection_layer.setVisible(False)

        self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)

        self._signals.connect(
            self._model,
            self._model.position_changed[QtCore.QPointF],
            self.set_position)

    def __init_actions(self):
        self._copy_action = QtGui.QAction('Copy', self)
        self._cut_action = QtGui.QAction('Cut', self)
        self._delete_action = QtGui.QAction('Delete', self)
        self._show_info_action = QtGui.QAction('Properties', self)
        self._copy_action.triggered.connect(self._copy_requested)
        self._cut_action.triggered.connect(self._cut_requested)
        self._delete_action.triggered.connect(self._delete_requested)
        self._show_info_action.triggered.connect(self._show_info_requested)

    def _init_move_state_machine(self):
        self._move_state_machine = QtCore.QStateMachine(self)
        self._state_nonmoving = QtCore.QState(self._move_state_machine)
        self._state_moving = QtCore.QState(self._move_state_machine)
        self._state_nonmoving.addTransition(
            self.mouse_pressed, self._state_moving)
        self._state_moving.addTransition(
            self.mouse_released, self._state_nonmoving)
        self._move_state_machine.setInitialState(self._state_nonmoving)
        self._move_state_machine.start()

        self._state_moving.entered.connect(self._start_move)
        self._state_moving.exited.connect(self._finish_move)

    def _copy_requested(self):
        self.copy_requested.emit(self)

    def _cut_requested(self):
        self.cut_requested.emit(self)

    def _delete_requested(self):
        self.delete_requested.emit(self)

    def position(self):
        return self.pos()

    @QtCore.Slot(QtCore.QPointF)
    def set_position(self, pos):
        self.setPos(pos)

    @QtCore.Slot()
    def _start_move(self):
        if len(self.scene().selectedItems()) > 1 and self.isSelected():
            for item in self.scene().selectedItems():
                if isinstance(item, MovableElementViewInterface):
                    item.start_move_individual()
        else:
            self.start_move_individual()

    @QtCore.Slot()
    def _finish_move(self):
        if self._old_position == self.position():
            return

        if len(self.scene().selectedItems()) > 1:
            undo_stack = self._model.flow.undo_stack()
            undo_stack.beginMacro('Moving group')
            for item in self.scene().selectedItems():
                if isinstance(item, MovableElementViewInterface):
                    item.finish_move_individual()
            undo_stack.endMacro()
        else:
            self.finish_move_individual()

    def _set_bounding_rect(self, rect):
        self.prepareGeometryChange()
        self._selection_layer.set_bounding_rect(rect)
        self._bounding_rect = rect

    def boundingRect(self):
        return self._bounding_rect

    def start_move_individual(self):
        self._old_position = self.position()

    def finish_move_individual(self):
        cmd = user_commands.MoveElementCommand(
            self._model, self._old_position, self.position())
        self._model.flow.undo_stack().push(cmd)

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemSelectedChange:
            self._selection_layer.setVisible(value)
        elif change == QtGui.QGraphicsItem.ItemPositionChange:
            return grid.instance().snap_to_grid(value)
        elif (change == QtGui.QGraphicsItem.ItemPositionHasChanged and
                value != self.position()):
            cmd = user_commands.MoveElementCommand(
                self._model, self._model.position, value)
            self._model.flow.undo_stack().push(cmd)
            return value
        return super(MovableElementViewInterface, self).itemChange(
            change, value)

    def set_this_z(self):
        """Implement in subclass if ordering is wanted (when moving objects).
        It shall set z for itself and its subelements (like ports) so that
        they are on top of everything when dragged.
        """
        pass

    def set_other_z(self):
        """Implement in subclass if ordering is wanted (when moving objects).
        It shall set z for itself and its subelements so that it is on top
        of everything when selected, except the item which the cursor is on.
        """
        pass

    def reset_z(self):
        """Implement in subclass if ordering is wanted (when moving objects).
        It shall set z for itself and its subelements to its default value.
        """
        pass

    def _set_selected_z(self):
        self._reset_all_z()
        for item in self.scene().selectedItems():
            if isinstance(item, MovableElementViewInterface):
                item.set_other_z()

    def _reset_all_z(self):
        for item in self.scene().items():
            if isinstance(item, MovableElementViewInterface):
                item.reset_z()

    def mousePressEvent(self, event):
        self._reset_all_z()
        self._set_selected_z()
        self.set_this_z()
        self.mouse_pressed.emit()
        super(MovableElementViewInterface, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.mouse_released.emit()
        super(MovableElementViewInterface, self).mouseReleaseEvent(event)

    @QtCore.Slot()
    def _show_info_requested(self):
        raise NotImplementedError('Not implemented for interface')


class SelectionLayer(QtGui.QGraphicsItem):
    """The blue layer that is painted on top of items when they are
    selected.
    """

    def __init__(self, outline, parent=None):
        super(SelectionLayer, self).__init__(parent=parent)

        self._outline = outline
        self.setZValue(10)
        self.prepareGeometryChange()
        self._bounding_rect = parent.boundingRect()

        border_width = 3.0
        border_color = theme.instance().selection_color
        self._pen = QtGui.QPen(border_color, border_width)
        brush_color = QtGui.QColor(theme.instance().selection_color)
        brush_color.setAlpha(100)
        self._brush = QtGui.QBrush(brush_color)

    def set_outline(self, outline):
        self._outline = outline

    def set_bounding_rect(self, rect):
        self.prepareGeometryChange()
        self._bounding_rect = rect

    def boundingRect(self):
        return self._bounding_rect

    def paint(self, painter, options, widget=None):
        painter.save()
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawPath(self._outline)
        painter.restore()


def filter_nodes(element_list):
    """Helper for finding ElementViewInterface's whose models are nodes."""
    return [
        element for element in element_list
        if element.model.type in flow.Type.node_types]


def filter_nodes_to_model(element_list):
    return [
        element.model for element in element_list
        if element.model.type in flow.Type.main_types]


def filter_elements_to_model(element_list):
    return [
        element.model for element in element_list
        if element.model.type in (
            flow.Type.Node, flow.Type.FlowInput, flow.Type.FlowOutput,
            flow.Type.Flow, flow.Type.Connection)]


def filter_element_views(element_list):
    """Helper for finding GraphicItems's that are ElementViewInterface's."""
    return [element for element in element_list
            if isinstance(element, ElementViewInterface)]


def filter_element_views_to_model(element_list):
    return [
        element.model for element in element_list
        if isinstance(element, ElementViewInterface)]


def get_label(text):
    label = QtGui.QLabel(text)
    label.setTextInteractionFlags(
        QtCore.Qt.TextSelectableByMouse | QtCore.Qt.TextSelectableByKeyboard)
    return label
