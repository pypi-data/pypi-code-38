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
import numpy as np
import json
import six
from . import dsgroup
from . import dstable


class Hdf5Lambda(dsgroup.Hdf5Group):
    """Abstraction of an HDF5-lambda."""
    def __init__(self, factory, group=None, datapointer=None, can_write=False,
                 can_link=False):
        self._compress = (
            dstable.int_compress if can_link else dstable.ext_compress)
        super(Hdf5Lambda, self).__init__(
            factory, group, datapointer, can_write, can_link)

    def _create_dataset(self, name, data):
        if data.nbytes > dstable._h5py_compress_threshold:
            self.group.create_dataset(
                name, data=data, **self._compress)
        else:
            self.group.create_dataset(name, data=data)

    def read(self):
        """
        Return stored pair of flow and list of port assignments or None if
        nothing is stored.
        """
        flow = self.group.attrs['flow'].decode('utf8')
        name = self.group.attrs['name'].decode('utf8')
        nodes = json.loads(
            self.group['nodes'][...][0].tolist().decode('ascii'))
        input_nodes = self.group[
            'input_nodes'][...].astype(six.text_type).tolist()
        output_nodes = self.group[
            'output_nodes'][...].astype(six.text_type).tolist()
        node_deps = self.group['node_deps'][...].astype(six.text_type).tolist()
        input_ports = json.loads(
            self.group['input_ports'][...].tolist().decode('ascii'))
        output_ports = self.group[
            'output_ports'][...].astype(six.text_type).tolist()
        bypass_ports = self.group[
            'bypass_ports'][...].astype(six.text_type).tolist()
        node_settings = json.loads(
            self.group['node_settings'][...].tolist().decode('ascii'))
        ports = json.loads(self.group[
            'ports'][...][0].tolist().decode('ascii'))

        return (
            (flow, name, nodes, input_nodes, output_nodes, node_deps,
             input_ports, output_ports, bypass_ports, node_settings),
            ports)

    def write(self, value):
        """
        Stores lambda in the hdf5 file, at path,
        with data from the given text
        """
        (flow, name, nodes, input_nodes, output_nodes, node_deps,
         input_ports,
         output_ports, bypass_ports, node_settings) = value[0]
        ports = value[1]
        self.group.attrs.create('flow', flow.encode('utf8'))
        self.group.attrs.create('name', name.encode('utf8'))
        self._create_dataset(
            'nodes', data=np.array([json.dumps(nodes).encode('ascii')],
                                   dtype=six.binary_type))
        self.group.create_dataset('input_nodes',
                                  data=np.array(input_nodes,
                                                dtype=six.binary_type),)
        self.group.create_dataset('output_nodes',
                                  data=np.array(
                                      output_nodes, dtype=six.binary_type))
        self.group.create_dataset('node_deps',
                                  data=np.array(
                                      node_deps, dtype=six.binary_type))
        self.group.create_dataset('input_ports',
                                  data=np.array(
                                      json.dumps(input_ports).encode('ascii'),
                                      dtype=six.binary_type))
        self.group.create_dataset('output_ports',
                                  data=np.array(output_ports,
                                                dtype=six.binary_type))
        self.group.create_dataset('bypass_ports',
                                  data=np.array(bypass_ports,
                                                dtype=six.binary_type))
        self.group.create_dataset(
            'ports',
            data=np.array([json.dumps(ports).encode('ascii')],
                          dtype=six.binary_type))
        self.group.create_dataset('node_settings',
                                  data=np.array(
                                      json.dumps(input_ports).encode('ascii'),
                                      dtype=six.binary_type))

    def transferable(self, other):
        return False

    def transfer(self, other):
        self.group.attrs['flow'] = other.group.attrs['flow']
        self.group.attrs['name'] = other.group.attrs['name']
        for key in ['nodes', 'input_nodes', 'output_nodes', 'node_deps',
                    'input_ports',
                    'output_ports', 'bypass_ports']:
            self.group[key] = other.group[key]

    def write_link(self, name, other, other_name):
        return False
