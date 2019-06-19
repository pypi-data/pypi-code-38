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
import PySide.QtCore as QtCore
from .types import ElementInterface, Type
import math


def connection_direction(source, destination):
    if source.type == Type.InputPort and destination.type == Type.OutputPort:
        return destination, source
    else:
        return source, destination


class RoutePoint(ElementInterface):

    _type = Type.RoutePoint

    def __init__(self, conn, position, **kwargs):
        self._conn = conn
        super(RoutePoint, self).__init__(**kwargs)
        self._flow = conn.flow
        self._size = QtCore.QSizeF(10, 10)
        self._position = position
        self.index = None

    def is_deletable(self):
        return True

    def add(self, flow=None, emit=True):
        if flow is not None:
            self._flow = flow
        self._conn.add_route_point(self)
        self._flow.add_route_point(self, emit)
        self.index = None

    def remove(self, emit=True):
        self.index = self._conn.route_points.index(self)
        self._conn.remove_route_point(self)
        self._flow.remove_route_point(self, emit)


class Connection(ElementInterface):
    start_position_changed = QtCore.Signal(QtCore.QPointF)
    end_position_changed = QtCore.Signal(QtCore.QPointF)
    route_point_added = QtCore.Signal(RoutePoint)
    route_point_removed = QtCore.Signal(RoutePoint)

    _type = Type.Connection

    def __init__(self, src, dst, flow, uuid=None, parent=None,
                 route_points=None):
        if parent is None:
            parent = flow
        super(Connection, self).__init__(parent)
        self._flow = flow
        self.uuid = uuid
        self._source = src
        self._destination = dst
        src.position_changed[QtCore.QPointF].connect(
            self.start_position_changed)
        dst.position_changed[QtCore.QPointF].connect(
            self.end_position_changed)
        self._position = QtCore.QPointF(
            (src.position.x() + dst.position.x()) / 2.0,
            (src.position.y() + dst.position.y()) / 2.0)
        self._route_points = []
        for r in route_points or []:
            route_point = RoutePoint(self, r)
            self._route_points.append(route_point)
        self._name = u'Connection from {} to {}'.format(src.node.name,
                                                        dst.node.name)

    @property
    def route_points(self):
        return list(self._route_points)

    def create_route_point(self, pos, src_pos, dst_pos):
        # TODO(erik): src_pos and dst_pos via the model,
        # currently, it only has relative coordinates.

        def dist(p):
            return math.sqrt(p.x() ** 2 + p.y() ** 2)

        points = [r.position for r in self._route_points]
        res = RoutePoint(self, pos)

        if not points:
            self._route_points = [res]
        else:
            # Insert split where it yields the shortest total connection.
            points_ext = [src_pos] + points + [dst_pos]
            idx = 0
            dmin = float('inf')

            for i in range(len(points) + 1):
                points_tmp = list(points_ext)
                points_tmp.insert(i + 1, pos)
                piter = iter(points_tmp)
                prev = next(piter)
                d = 0

                for curr in piter:
                    d += dist(curr - prev)
                    prev = curr

                if d < dmin:
                    idx = i
                    dmin = d

            self._route_points.insert(idx, res)
        self.route_point_added.emit(res)
        self._flow.add_route_point(res)
        return res

    def remove_route_point(self, route_point):
        route_point.index = self._route_points.index(route_point)
        self._route_points.remove(route_point)
        self.route_point_removed.emit(route_point)

    def add_route_point(self, route_point):
        if route_point.index is None:
            self._route_points.append(route_point)
        else:
            self._route_points.insert(route_point.index, route_point)
        self.route_point_added.emit(route_point)

    @property
    def source(self):
        """Returns the source port for the connection."""
        return self._source

    @property
    def destination(self):
        """Returns the destination port for the connection."""
        return self._destination

    def add(self, flow=None, emit=True):
        if flow is not None:
            self._flow = flow
        self._flow.add_connection(self, emit)

    def remove(self, emit=True):
        self._flow.remove_connection(self, emit)

    def to_copy_dict(self):
        connection_dict = self.to_dict()
        connection_dict['namespace_uuid'] = self.namespace_uuid()
        return connection_dict

    def to_dict(self, execute=False):
        if execute:
            return {
                'uuid': self.full_uuid,
                'source': {
                    'node': self._source.node.full_uuid,
                    'port': self._source.full_uuid},
                'destination': {
                    'node': self._destination.node.full_uuid,
                    'port': self._destination.full_uuid}}
        else:
            source_node_uuid = self._source.node.uuid
            dest_node_uuid = self._destination.node.uuid
            if (self._source.node.type in (Type.FlowInput, Type.FlowOutput) and
                    self._source.node.is_linked):
                source_node_uuid = self._source.node.source_uuid
            if (self._destination.node.type in
                    (Type.FlowInput, Type.FlowOutput) and
                    self._destination.node.is_linked):
                dest_node_uuid = self._destination.node.source_uuid

            ctype = str(self._destination.datatype)

            return {
                'uuid': self.uuid,
                'type': ctype,
                'source': {
                    'node': source_node_uuid,
                    'port': self._source.uuid},
                'destination': {
                    'node': dest_node_uuid,
                    'port': self._destination.uuid},
                'route': [{'x': r.position.x(), 'y': r.position.y()}
                          for r in self._route_points]}

    def filename(self):
        """Filename of the data associated with the source port."""
        return self.source.filename

    def is_deletable(self):
        return True

    def __hash__(self):
        return hash((self._source.uuid, self._destination.uuid))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self == other
