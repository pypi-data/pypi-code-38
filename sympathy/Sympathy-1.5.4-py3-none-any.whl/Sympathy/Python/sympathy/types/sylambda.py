# Copyright (c) 2015, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import six
from . import sybase
from . import types
from . import exception as exc


class FlowDesc(object):
    """
    Extra level of typing to ensure that the user takes care and does not pass
    arbitrary strings or objects.
    """
    def __init__(self, flow_identifier, name, nodes, input_nodes,
                 output_nodes, node_deps, input_ports, output_ports,
                 bypass_ports,
                 node_settings):
        assert(isinstance(flow_identifier, six.string_types))
        self.flow_identifier = flow_identifier
        self.name = name
        self.nodes = nodes
        self.input_nodes = input_nodes
        self.output_nodes = output_nodes
        self.node_deps = node_deps
        self.input_ports = input_ports
        self.output_ports = output_ports
        self.bypass_ports = bypass_ports
        self.node_settings = node_settings


class PortDesc(object):
    """
    Extra level of typing to ensure that the user takes care and does not pass
    arbitrary strings or objects.
    """
    def __init__(self, port):
        assert(isinstance(port, dict))
        self.data = port


class sylambda(sybase.sygroup):

    def __init__(self, container_type, datasource=sybase.NULL_SOURCE):
        super(sylambda, self).__init__(container_type,
                                       datasource or sybase.NULL_SOURCE)
        self._args = []
        self._cache = (None, False)

        body_type = container_type

        try:
            while True:
                self._args.append(body_type.arg)
                body_type = body_type.result

        except AttributeError:
            # Last body reached, all args collected.
            pass

    def _get(self):
        value = self._cache[0]

        if value is None:
            value = self._datasource.read()
            self._cache = (value, False)
        return value

    def _set(self, value):
        flow, port = value
        self._cache = (value, True)

    def identifier(self):
        return self._get()[0][0]

    def name(self):
        return self._get()[0][1]

    def get(self):
        """Returns a pair of flow, list of port assignments."""
        flow, ports = self._get()
        return (FlowDesc(*flow), [PortDesc(port) for port in ports])

    def set(self, value):
        """Value is a pair of flow, list of port assignments."""
        flow, ports = value
        self._set(((flow.flow_identifier,
                    flow.name,
                    flow.nodes,
                    flow.input_nodes,
                    flow.output_nodes,
                    flow.node_deps,
                    flow.input_ports,
                    flow.output_ports,
                    flow.bypass_ports,
                    flow.node_settings),
                   [port.data
                    for port in ports]))

    def apply(self, port):
        assert(len(self._args) > 1)
        value = self._get()
        flow, ports = value
        assert(flow is not None)
        ports.append(port.data)
        self._set(value)
        self._args = self._args[1:]
        self.container_type = self.container_type.result

    def arguments(self):
        return self._args

    def source(self, other, shallow=False):
        assert(types.match(self.container_type, other.container_type))
        self._set(other._get())

    def __copy__(self):
        obj = super(sylambda, self).__copy__()
        obj._args = list(self._args)
        obj._cache = tuple(self._cache)
        return obj

    def __deepcopy__(self, memo=None):
        return self.__copy__()

    def _writeback(self, datasource, link=None):
        # Transfer relies on direct compatiblity, for example, in the hdf5
        # datasource case both sources need to be hdf5 and the source needs to
        # be read only.
        origin = self._datasource
        target = datasource
        exc.assert_exc(target.can_write, exc=exc.WritebackReadOnlyError)

        if link:
            return False

        shares_origin = target.shares_origin(origin)
        value, dirty = self._cache

        if shares_origin and not dirty:
            # At this point there is no support for writing flows more than
            # once.
            return

        if target.transferable(origin) and not dirty:
            target.transfer(
                None, origin, None)
        else:
            # No transfer possible, writing using numpy texts.
            if value is None:
                value = self._get()

            if value is not None:
                target.write(value)

    def __repr__(self):
        return "lambda()"
