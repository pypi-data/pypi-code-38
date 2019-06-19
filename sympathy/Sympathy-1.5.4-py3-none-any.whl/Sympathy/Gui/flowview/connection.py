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
import cgi
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
import functools
from .types import ElementViewInterface, MovableElementViewInterface, get_label
from . import theme
from sympathy.utils import uuid_generator
from .. import user_commands
from .. import settings


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
        layout.addRow('Namespace UUID', get_label(pre(namespace_uuid)))
        layout.addRow('Connection UUID', get_label(pre(item_uuid)))

        self._main_layout.addLayout(layout)
        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        self._main_layout.addWidget(button_box)
        self.setLayout(self._main_layout)


def _points_path(points):
    """"
    Create new connection path with the given points, assuming that there
    are exactly exactly two.
    """
    shape = settings.instance()['Gui/flow_connection_shape']
    iter_points = iter(points)
    start_pos = next(iter_points)
    path = QtGui.QPainterPath()
    path.moveTo(start_pos)

    for end_pos in iter_points:
        if shape == 'Line':
            path.lineTo(end_pos)
        else:
            dx = end_pos.x() - start_pos.x()
            path.cubicTo(start_pos + QtCore.QPointF(dx / 2.0, 0),
                         end_pos + QtCore.QPointF(-dx / 2.0, 0),
                         end_pos)
            start_pos = end_pos
    return path


class TransientConnectionView(QtCore.QObject, QtGui.QGraphicsPathItem):
    """A dangling connection as it is being made."""

    _normal_alpha = 80
    _valid_alpha = 230

    def __init__(self, anchor, parent=None):
        QtCore.QObject.__init__(self, parent)
        QtGui.QGraphicsPathItem.__init__(self)
        base_color = QtGui.QColor(theme.instance().darker_color)
        self._color = QtGui.QColor(base_color)
        self._color.setAlpha(self._normal_alpha)
        self._color_valid = QtGui.QColor(base_color)
        self._color_valid.setAlpha(self._valid_alpha)
        self._points = [anchor, anchor]
        self._init()

    def _init(self):
        # self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
        self._path = _points_path(self._points)
        self.setPath(self._path)

        self._set_pen(self._color)
        self.setZValue(1)
        self.setBoundingRegionGranularity(1.0)
        self.setGraphicsEffect(None)

    def _set_pen(self, color):
        self.setPen(QtGui.QPen(
            QtGui.QBrush(color), ConnectionView.width,
            QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))

    def set_valid_connection(self, state=False, port=None):
        if state:
            self._set_pen(self._color_valid)
            if port is not None:
                self.set_end_position(port.connection_position())
        else:
            self._set_pen(self._color)

    @QtCore.Slot(QtCore.QPointF)
    def set_start_position(self, position):
        self._points[0] = position
        self._path = _points_path(self._points)
        self.setPath(self._path)

    @QtCore.Slot(QtCore.QPointF)
    def set_end_position(self, position):
        self._points[1] = position
        self._path = _points_path(self._points)
        self.setPath(self._path)

    def paint(self, painter, option, widget=None):
        painter.save()
        painter.setPen(self.pen())
        painter.drawPath(self.path())
        painter.restore()


class ConnectionView(QtCore.QObject,
                     QtGui.QGraphicsPathItem,
                     ElementViewInterface):
    """A connection between two ports"""

    delete_requested = QtCore.Signal(ElementViewInterface)
    width = 5.0

    def __init__(self, model, start_pos, end_pos, parent=None):
        QtCore.QObject.__init__(self, parent)
        QtGui.QGraphicsPathItem.__init__(self)
        ElementViewInterface.__init__(self, model)
        self._scene = parent
        self._stroker = QtGui.QPainterPathStroker()
        self._stroker.setWidth(self.width)
        self._stroker.setCapStyle(QtCore.Qt.RoundCap)
        self._unselected_color = theme.instance().darker_color
        self._selected_color = theme.instance().selection_color
        self._color = self._unselected_color
        self._points = [start_pos, end_pos]
        self._init()
        self._init_actions()
        self._init_signalling()
        self._init_context_menu()

    def _init(self):
        # self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
        self._path = self._points_path()
        self.setPath(self._path)
        self._unselected_brush = QtGui.QBrush(self._unselected_color)
        self._unselected_pen = QtGui.QPen(
            self._unselected_brush, 0,
            QtCore.Qt.SolidLine, QtCore.Qt.RoundCap)
        self._selected_brush = QtGui.QBrush(self._selected_color)
        self._selected_pen = QtGui.QPen(
            self._selected_brush, 0,
            QtCore.Qt.SolidLine, QtCore.Qt.RoundCap)

        self.setBrush(self._unselected_brush)
        self.setPen(self._unselected_pen)
        self.setZValue(1)
        self.setBoundingRegionGranularity(1.0)
        self.setGraphicsEffect(None)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)

    def _init_actions(self):
        self._delete_action = QtGui.QAction('Delete', self)
        self._show_info_action = QtGui.QAction('Properties', self)
        self._create_route_point_action = QtGui.QAction(
            'Create route point', self)
        self._show_info_action.triggered.connect(self._show_info_requested)
        self._create_route_point_action.triggered.connect(
            self._create_route_point)

    def _init_signalling(self):
        self._signals.connect(
            self._model,
            self._model.route_point_added,
            self._handle_route_point_added)

        self._signals.connect(
            self._model,
            self._model.route_point_removed,
            self._handle_route_point_removed)

        for r in self.model.route_points:
            self._signals.connect(
                r,
                r.position_changed,
                self._handle_route_point_position_changed)

    def _init_context_menu(self):
        self._context_menu = QtGui.QMenu()
        self._context_menu.addAction(self._show_info_action)
        self._context_menu.addAction(self._delete_action)
        self._context_menu.addAction(self._create_route_point_action)

    @QtCore.Slot()
    def _show_info_requested(self):
        dialog = Info(self._model)
        dialog.exec_()

    def _create_route_point(self):
        p_src, p_dst = self._points
        cmd = user_commands.CreateRoutePoint(self._model.flow, self._model,
                                             self._context_pos, p_src, p_dst)
        self._model.flow.undo_stack().push(cmd)

    def _update_points(self, route_point):
        p_src, p_dst = self._points
        self._path = self._points_path()
        self.setPath(self._path)

    def _handle_route_point_added(self, route_point):
        self._update_points(route_point)
        self._signals.connect(
            route_point,
            route_point.position_changed,
            self._handle_route_point_position_changed)

    def _handle_route_point_removed(self, route_point):
        self._signals.disconnect_all(route_point)
        self._update_points(route_point)

    def _handle_route_point_position_changed(self, pos):
        self._path = self._points_path()
        self.setPath(self._path)

    def _points_path(self):
        self.prepareGeometryChange()
        res = _points_path(
            [self._points[0]] +
            [r.position for r in self._model.route_points] +
            [self._points[1]])
        return self._stroker.createStroke(res)

    @QtCore.Slot(QtCore.QPointF)
    def set_start_position(self, position):
        self._points[0] = position
        self._path = self._points_path()
        self.setPath(self._path)

    @QtCore.Slot(QtCore.QPointF)
    def set_end_position(self, position):
        self._points[1] = position
        self._path = self._points_path()
        self.setPath(self._path)

    @QtCore.Slot()
    def selection_changed(self):
        if self.isSelected():
            self.setPen(self._selected_pen)
            self.setBrush(self._selected_brush)
        else:
            self.setPen(self._unselected_pen)
            self.setBrush(self._unselected_brush)

    def paint(self, painter, option, widget=None):
        painter.save()
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawPath(self.path())
        painter.restore()

    def contextMenuEvent(self, event):
        pos = event.screenPos()
        try:
            self._context_pos = self._scene.mapToScene(
                self._scene.mapFromGlobal(pos))
            self._scene.mapToScene(self._scene.mapFromGlobal(pos))
            self._context_menu.exec_(pos)
        finally:
            self._context_pos = None


class RoutePointView(MovableElementViewInterface):

    delete_requested = QtCore.Signal(ElementViewInterface)
    _border_width = 2.0

    def __init__(self, model, parent=None):
        MovableElementViewInterface.__init__(self, model, parent)
        self._context_menu = QtGui.QMenu()
        self._delete_action = QtGui.QAction('Delete', self)
        self._context_menu.addAction(self._delete_action)
        self._node_color = theme.instance().midlight_color
        self._brush = QtGui.QBrush(self._node_color)
        self._border_color = theme.instance().mid_color
        self._pen = QtGui.QPen(self._border_color, self._border_width)

        r = self.boundingRect().adjusted(
            self._border_width, self._border_width,
            -self._border_width, -self._border_width)
        self.boundingRect().moveTo(
            -(self._model.size.width() / 2),
            -(self._model.size.height() / 2))

        r.moveTo(-(self._model.size.width() / 2 - self._border_width),
                 -(self._model.size.height() / 2 - self._border_width))
        self._outline.addRoundedRect(r, 1.4, 1.4)
        self.setZValue(2)

        self._delete_action.triggered.connect(
            functools.partial(self.delete_requested.emit, self))

    def paint(self, painter, options, widget=None):
        painter.save()
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawPath(self._outline)
        painter.restore()

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionHasChanged:
            self._model.position = value

        return super(RoutePointView, self).itemChange(change, value)

    def contextMenuEvent(self, event):
        pos = event.screenPos()
        self._context_menu.exec_(pos)
