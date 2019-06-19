# This file is part of Sympathy for Data.
# Copyright (c) 2015-2016 Combine Control Systems AB
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
import contextlib
from .. util import OrderedSet
from . types import Type
from . exceptions import SyInferTypeError


class InfertypeContext(object):

    def __init__(self, delayed):
        self._delayed = delayed
        self.edges = []
        self.errors = []
        self.removed = []
        self.replacements = {}

    @property
    def delayed(self):
        return self._delayed


infertype_ctx = InfertypeContext(False)


@contextlib.contextmanager
def delayed_infertype_ctx():
    global infertype_ctx
    infertype_ctx = InfertypeContext(True)
    yield infertype_ctx
    infertype_ctx = InfertypeContext(False)


def _parent_flow(flow_):
    pflow = flow_
    while pflow is not None:
        flow_ = pflow
        pflow = pflow._flow
    return flow_


def infertype_flow(flow_, check=False, replace=None):
    """
    Infer the type of all ports connected to port0 and port1. When disconnect
    is False, port0 and port1 will be assumed to be connected regardles of the
    actual connections. This is useful since it allows infertype to be called
    before a connection between port0 and port1 is created.
    """
    all_edges = infertype_collect(_parent_flow(flow_))
    infertype(all_edges, check=check, replace=replace)


def infertype_connect(port0, port1, disconnect=False,
                      check=False):
    """
    Infer the type of all ports connected to port0 and port1. When disconnect
    is False, port0 and port1 will be assumed to be connected regardles of the
    actual connections. This is useful since it allows infertype to be called
    before a connection between port0 and port1 is created.
    """
    all_edges = infertype_collect(_parent_flow(port0.flow))
    remove = []

    if disconnect:
        remove = [(port0, port1)]
    else:
        all_edges.add((port0, port1))

    infertype(all_edges, check=check, remove=remove)


def infertype_collect(flow_):

    constraints = OrderedSet()

    for connection in flow_._connections:
        constraints.add((connection.source, connection.destination))

    for subflow in flow_._subflows:
        constraints.update(subflow.infertype_constraints())
        constraints.update(infertype_collect(subflow))
    return constraints


def infertype_constraints(collected, type_mapping, replace=None):
    replace = replace or {}
    res = []

    if not replace:
        res = [(start.datatype_base,
                end.datatype_base)
               for start, end in collected
               if start and end]

    else:
        for start, end in collected:
            if start and end:
                if start in replace:
                    start = replace[start]
                else:
                    start = start.datatype_base
                if end in replace:
                    end = replace[end]
                else:
                    end = end.datatype_base
                res.append((start, end))
    return res


def infertype(all_edges, check=False, remove=None, replace=None):
    type_mapping = {}
    constraints = infertype_constraints(all_edges, type_mapping, replace)
    delayed = infertype_ctx.delayed
    remove = remove or []

    for start, end in constraints:
        if not start.match(end, type_mapping):
            if delayed:
                infertype_ctx.errors.append((start, end))
            else:
                raise SyInferTypeError([(start, end)])

    gen_ports = OrderedSet()
    nodes = OrderedSet()
    inst_edges = set(all_edges)
    inst_edges.update(remove)

    for edge in inst_edges:
        for obj in edge:
            if obj and obj.type in Type.port_types:
                gen_ports.add(obj)
                if obj.node and obj.node.type == Type.Node:
                    nodes.add(obj.node)

    for node in nodes:
        for input_ in node.inputs:
            gen_ports.add(input_)
        for output in node.outputs:
            gen_ports.add(output)

    if not check:
        for port in gen_ports:
            port.datatype_instantiate(type_mapping)

    if delayed and infertype_ctx.errors:
        # After errors in delayed inference, remove connections with unmatched
        # types.
        for start, end in all_edges:
            if start.type in Type.port_types and end.type in Type.port_types:
                if not start.datatype.match(end.datatype, type_mapping):
                    if end.type == Type.InputPort:
                        conn = end.flow.input_connection_to_port(end)
                        if conn is not None:
                            end.flow.remove_connection(conn)
                        infertype_ctx.removed.append((start, end))
