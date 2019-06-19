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
import logging
import copy
import PySide.QtCore as QtCore
import functools
from collections import OrderedDict, deque


core_logger = logging.getLogger('core')

global_vertex_id = 0
global_edge_id = 0


class GraphInterface(object):

    """GraphInterface"""

    def __init__(self):
        super(GraphInterface, self).__init__()

    def vertices(self):
        raise NotImplementedError('Not implemented for interface')

    def edges(self):
        raise NotImplementedError('Not implemented for interface')

    def edge(self, src, dst):
        raise NotImplementedError('Not implemented for interface')

    def add_vertex(self, ):
        raise NotImplementedError('Not implemented for interface')

    def remove_vertex(self, v):
        raise NotImplementedError('Not implemented for interface')

    def add_edge(self, src, dst):
        raise NotImplementedError('Not implemented for interface')

    def remove_edge(self, e):
        raise NotImplementedError('Not implemented for interface')

    def __str__(self):
        raise NotImplementedError('Not implemented for interface')

    def connect_(self, context):
        raise NotImplementedError('Not implemented for interface')


class Vertex(object):

    def __init__(self):
        super(Vertex, self).__init__()
        global global_vertex_id
        self._id = global_vertex_id
        global_vertex_id += 1
        self._edges = []

    def id(self):
        return self._id

    def add_edge(self, edge):
        self._edges.append(edge)

    def remove_edge(self, edge):
        if edge in self._edges:
            self._edges.remove(edge)

    def edges(self):
        return self._edges

    def inputs(self):
        return [e for e in self._edges if e.dst() == self]

    def outputs(self):
        return [e for e in self._edges if e.src() == self]


class Edge(object):

    def __init__(self, src, dst):
        super(Edge, self).__init__()
        global global_edge_id
        self._id = global_edge_id
        global_edge_id += 1
        self._src = src
        self._dst = dst

    def src(self):
        return self._src

    def dst(self):
        return self._dst

    def id(self):
        return self._id

    def __str__(self):
        return '"%s" -> "%s";' % (self._src.id(), self._dst.id())


class Graph(QtCore.QObject, GraphInterface):
    vertex_added = QtCore.Signal(Vertex)
    vertex_removed = QtCore.Signal(Vertex)
    edge_added = QtCore.Signal(Edge)
    edge_removed = QtCore.Signal(Edge)

    def __init__(self, parent=None):
        super(Graph, self).__init__(parent)
        self._vertices = []
        self._edges = []

    def edge(self, src, dst):
        for e in src.outputs():
            if e.dst() == dst:
                return e
        return None

    def vertices(self):
        return self._vertices

    def edges(self):
        return self._edges

    def add_edge(self, src, dst):
        if src not in self._vertices:
            import traceback
            core_logger.critical('SRC FAIL {}\n{}'.format(src, self._vertices))
            core_logger.critical(''.join(traceback.format_stack()))
        if dst not in self._vertices:
            import traceback
            core_logger.critical('DST FAIL {}\n{}'.format(dst, self._vertices))
            core_logger.critical(''.join(traceback.format_stack()))

        e = Edge(src, dst)
        src.add_edge(e)
        dst.add_edge(e)
        self._edges.append(e)
        self.edge_added.emit(e)
        return e

    def add_vertex(self):
        v = Vertex()
        self._vertices.append(v)
        self.vertex_added.emit(v)
        return v

    def remove_edge(self, edge):
        self.edge_removed.emit(edge)
        edge.src().remove_edge(edge)
        edge.dst().remove_edge(edge)
        if edge in self._edges:
            self._edges.remove(edge)

    def remove_vertex(self, vertex):
        self.vertex_removed.emit(vertex)
        edges = copy.copy(vertex.edges())
        for e in edges:
            self.remove_edge(e)
        if vertex in self._vertices:
            self._vertices.remove(vertex)

    def join(self, graph):
        self._vertices.extend(graph.vertices())
        self._edges.extend(graph.edges())

    def __str__(self):
        output = 'digraph hub {\nrankdir="LR";\n'

        for v in self._vertices:
            for e in v.outputs():
                output += '"%s" -> "%s";\n' % \
                    (v.id(), e.dst().id())
        output += '\n}\n'
        return output

    def connect_(self, context):
        self.vertex_added[Vertex].connect(
            functools.partial(context.invalidate_context))
        self.vertex_removed[Vertex].connect(
            functools.partial(context.invalidate_context))
        self.edge_added[Edge].connect(
            functools.partial(context.invalidate_context))
        self.edge_removed[Edge].connect(
            functools.partial(context.invalidate_context))


class DocumentGraph(GraphInterface):

    def __init__(self, parent=None):
        super(DocumentGraph, self).__init__()
        self._g = Graph(parent)
        self._entry_vertex = self._g.add_vertex()
        self._exit_vertex = self._g.add_vertex()

    def entry(self):
        return self._entry_vertex

    def exit(self):
        return self._exit_vertex

    def vertices(self):
        return self._g.vertices()

    def edges(self):
        return self._g.edges()

    def edge(self, src, dst):
        return self._g.edge(src, dst)

    def add_vertex(self):
        v = self._g.add_vertex()
        self._g.add_edge(self._entry_vertex, v)
        self._g.add_edge(v, self._exit_vertex)
        return v

    def remove_vertex(self, v):
        edges = copy.copy(v.edges())
        for e in edges:
            self.remove_edge(e)
        self._g.remove_vertex(v)

    def add_edge(self, src, dst):
        self._remove_entry_edge(dst)
        self._remove_exit_edge(src)
        return self._g.add_edge(src, dst)

    def remove_edge(self, e):
        src = e.src()
        dst = e.dst()
        self._g.remove_edge(e)
        if not src == self._entry_vertex or dst == self._exit_vertex:
            if len(src.outputs()) == 0:
                self._add_exit_edge(src)
            if len(dst.inputs()) == 0:
                self._add_entry_edge(dst)

    def __str__(self):
        return self._g.__str__()

    def connect_(self, context):
        self._g.connect_(context)

    def _add_entry_edge(self, v):
        self._g.add_edge(self._entry_vertex, v)

    def _add_exit_edge(self, v):
        self._g.add_edge(v, self._exit_vertex)

    def _remove_entry_edge(self, v):
        edge_entry_to_v = self._g.edge(self._entry_vertex, v)
        if edge_entry_to_v:
            self._g.remove_edge(edge_entry_to_v)
            return True
        else:
            return False

    def _remove_exit_edge(self, v):
        edge_v_to_exit = self._g.edge(v, self._exit_vertex)
        if edge_v_to_exit:
            self._g.remove_edge(edge_v_to_exit)
            return True
        else:
            return False


class GraphContext(QtCore.QObject):

    def __init__(self, graph_interface):
        """ g is a GraphInterface """
        super(GraphContext, self).__init__()
        self._g = graph_interface
        self._valid = False
        self._g.connect_(self)

    def g(self):
        return self._g

    def valid(self):
        return self._valid

    def set_valid(self):
        self._valid = True

    @QtCore.Slot()
    def invalidate_context(self):
        self._valid = False
        return self._valid


class DepthFirstSearchContext(GraphContext):

    """docstring for DepthFirstSearchContext"""

    def __init__(self, graph_interface):
        super(DepthFirstSearchContext, self).__init__(graph_interface)
        self.discovery_time = OrderedDict()
        self.finish_time = OrderedDict()

    def __str__(self):
        out = ['{}: {}/{}'.format(
               v.id(), self.discovery_time[v], self.finish_time[v])
               for v in self._g.vertices() if v in self.discovery_time]
        return '\n'.join(out)


class TopologicalSortContext(GraphContext):

    def __init__(self, graph_interface):
        super(TopologicalSortContext, self).__init__(graph_interface)
        self.dependency_group = OrderedDict()

    def __str__(self):
        return '\n'.join(['{}: {}'.format(v.id(), self.dependency_group[v])
                          for v in self.dependency_group.keys()])


class DocumentContext(GraphContext):

    def __init__(self, graph_interface):
        super(DocumentContext, self).__init__(graph_interface)
        self.vertex_uuid_map = {}
        self.uuid_vertex_map = {}
        self.edge_uuid_map = {}
        self.uuid_edge_map = {}
        self.vertex_nodegroupid_map = {}
        self.nodegroupid_vertices_map = {}
        self.nodegroup_counter = 0

    def __str__(self):
        return '\n'.join(
            ['{}: {}'.format(v.id(), self.vertex_uuid_map[v])
             for v in self.vertex_uuid_map])


class GraphAlgorithm(object):

    """docstring for GraphAlgorithm"""

    def __init__(self):
        super(GraphAlgorithm, self).__init__()


class TopologicalSort(GraphAlgorithm):

    """docstring for TopologicalSort"""

    def __init__(self):
        super(TopologicalSort, self).__init__()

    def sort_from_vertex(self, start, ts_context):
        dfs_context = DepthFirstSearchContext(ts_context.g())
        dfs = DepthFirstSearch()
        dfs.search(start, dfs_context)
        self.sort_from_dfs(dfs_context, ts_context)

    def sort_from_dfs(self, dfs_context, ts_context):
        time = OrderedDict((v, 0) for v in ts_context.g().vertices())

        for v, finish_time in sorted(dfs_context.finish_time.items(),
                                     key=lambda x: x[1], reverse=True):
            if v.inputs():
                time[v] = max([time[e.src()] for e in v.inputs()]) + 1
        ts_context.set_valid()
        ts_context.dependency_group = time


class DepthFirstSearch(GraphAlgorithm):

    """docstring for DepthFirstSearch"""

    def __init__(self):
        super(DepthFirstSearch, self).__init__()

    def search(self, start, c):
        """
        start - Vertex,
        c - DepthFirstSearchContext
        """
        visited = {v: False for v in c.g().vertices()}
        dfs_time = 0
        for v in c.g().vertices():
            visited[v] = False

        visited, dfs_time, c = self._dfs_postorder(start, visited, dfs_time, c)
        c.set_valid()

    def _dfs_postorder(self, u, visited, dfs_time, c):
        """"
        u - Vertex,
        visited - [Vertex]:bool,
        dfs_time - int,
        c - DepthFirstSearchContext
        """
        visited[u] = True
        c.discovery_time[u] = dfs_time
        dfs_time += 1
        for e in u.outputs():
            v = e.dst()
            if not visited[v]:
                visited, dfs_time, c = (
                    self._dfs_postorder(v, visited, dfs_time, c))

        c.finish_time[u] = dfs_time
        dfs_time += 1
        return visited, dfs_time, c


class CycleDetectionAlgorithm(GraphAlgorithm):

    """docstring for CycleDetectionAlgorithm"""

    def __init__(self):
        super(CycleDetectionAlgorithm, self).__init__()

    def find_cycle(self, src, dst, graph_interface):
        visited = {v: False for v in graph_interface.vertices()}
        cycle_found = False
        cycle_found = self._find_cycle(src, dst, visited, cycle_found)
        return cycle_found

    def _find_cycle(self, src, dst, visited, cycle_found):
        visited[src] = True
        for e in src.inputs():
            v = e.src()
            if v == dst:
                cycle_found = True
                return cycle_found
            if not visited[v]:
                cycle_found = self._find_cycle(v, dst, visited, cycle_found)
            if cycle_found:
                return cycle_found
        return cycle_found


class IncomingVerticesRecursivelyAlgorithm(GraphAlgorithm):

    """docstring for IncomingVerticesRecursivelyAlgorithm"""

    def __init__(self):
        super(IncomingVerticesRecursivelyAlgorithm, self).__init__()

    def find_incoming_vertices(self, v, vertices, graph_interface):
        visited = {u: False for u in graph_interface.vertices()}
        self._find_incoming_vertices(v, visited, vertices)

    def _find_incoming_vertices(self, v, visited, vertices):
        visited[v] = True
        for e in v.inputs():
            u = e.src()
            if not visited[u]:
                vertices.append(u)
                self._find_incoming_vertices(u, visited, vertices)


def traverse(graph, vertex, visitor, direct='<->', ctx=None):
    """
    Traverse graph in the direction given by direct.
    Direction can be <-, ->, or <-> (both directions).

    Visitor is a FlowGraphVisitor which visits edges between flow elements.
    Visited can contain a set of edges already visited. Edges are visited
    only once.

    None is returned. Data storage is handled by the visitor.
    """

    if ctx is None:
        ctx = traverse_ctx()
    visited_vert = ctx

    visited_vert.add(graph.entry())
    visited_vert.add(graph.exit())

    stack = deque([vertex])

    while stack:
        v = stack.popleft()

        if v not in visited_vert:
            visited_vert.add(v)

            if direct in ['<-', '<->']:
                for e in v.inputs():
                    i = e.src()
                    done = visitor(i, v, '<-')
                    if not done:
                        stack.append(i)

            if direct in ['->', '<->']:
                for e in v.outputs():
                    o = e.dst()
                    done = visitor(v, o, '->')
                    if not done:
                        stack.append(o)


def traverse_ctx():
    return set()


def to_graph_mapping(nodes, edges, graph_factory=DocumentGraph, parent=None):
    graph = graph_factory(parent=parent)
    mapping = {}

    for node in nodes:
        mapping[node] = graph.add_vertex()
    for edge in edges:
        src = mapping[edge[0]]
        dst = mapping[edge[1]]
        if src != dst:
            graph.add_edge(src, dst)
    return graph, mapping
