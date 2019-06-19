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
import os
import sys
import copy
import uuid
import six
import contextlib
from collections import OrderedDict
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

from sympathy.api import parameters as syparameters
from sympathy.platform import basicnode as node
from sympathy.utils import port as port_util
from sympathy.utils import parameter_helper
from sympathy.utils.prim import uri_to_path, fuzzy_filter, group_pairs
from sympathy.types import types
from sympathy.platform import state


_app_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir, os.pardir, os.pardir))

sys.path.append(_app_dir)

import launch


class InteractiveError(Exception):
    pass


class InteractiveNotNodeError(Exception):
    pass


@contextlib.contextmanager
def _instantiated_ports(ports, inputs=None):
    if inputs is None:
        yield
        return

    org_inp = ports.get('inputs')
    org_out = ports.get('outputs')

    inp = [dict(port) for port in org_inp or []]
    out = [dict(port) for port in org_out or []]

    mapping = {}

    for input_, port in zip(inputs, inp):
        dt = types.parse_base_line(port['type'])
        port['type_base'] = dt
        types.match(dt, input_.container_type, mapping)

    for port in out:
        dt = types.parse_base_line(port['type'])
        port['type_base'] = dt

    for port in inp + out:
        port['type'] = str(types.instantiate(port['type_base'], mapping))
        del port['type_base']

    ports['inputs'] = inp
    ports['outputs'] = out

    yield

    if org_inp is None:
        ports.pop('inputs')
    else:
        ports['inputs'] = org_inp

    if org_out is None:
        ports.pop('outputs')
    else:
        ports['outputs'] = org_out


class SyiContext(object):
    def __init__(self, sys_path):
        self.__sys_path = sys_path
        self.__sys_path_before = []

    def __enter__(self):
        self.__sys_path_before = list(sys.path)
        sys.path[:] = self.__sys_path
        return self

    def __exit__(self, *args):
        sys.path[:] = self.__sys_path_before


class SyiNode(object):
    def __init__(self, context, node, parameters, filename):
        parameters = copy.deepcopy(parameters)
        self.__context = context
        self.__node = node
        self.__parameters = parameters
        self.__syiparameters = SyiParameters(type(node), parameters)
        self.__filename = filename

        inputs = parameters['ports'].get('inputs', [])
        outputs = parameters['ports'].get('outputs', [])
        inputs, outputs = port_util.instantiate(
            inputs, outputs, {})

        for port in inputs:
            port['file'] = six.text_type(uuid.uuid4())

        for port in outputs:
            port['file'] = six.text_type(uuid.uuid4())

        parameters['ports']['inputs'] = inputs
        parameters['ports']['outputs'] = outputs

    def execute(self, inputs=None):
        """
        Compute output by executing node.
        """
        ports = self.__parameters['ports']

        with _instantiated_ports(ports, inputs):
            node_inputs = _build_ports(inputs, ports.get('inputs', []))
            builder = node.ManualContextBuilder(node_inputs, OrderedDict(),
                                                False,
                                                check_fns=False)
            try:
                self.__node._sys_execute(
                    self.__parameters, {}, builder=builder)

                return [value for value in builder.outputs.values()]
            finally:
                state.node_state().cleardata()

    def configure(self, inputs=None):
        """
        Create configuration by launching parameter GUI.
        """
        return self.__configure(inputs, False)

    def __build_node_context(self, inputs=None):
        ports = self.__parameters['ports'].get('inputs', [])
        node_inputs = _build_ports(inputs, ports)
        builder = node.ManualContextBuilder(node_inputs, OrderedDict(),
                                            False, check_fns=False)
        exclude_input = 'inputs' not in self.__parameters['ports']
        return self.__node._build_node_context(
            self.__parameters, {}, exclude_input=exclude_input,
            builder=builder)

    def __adjust_parameters(self, node_context):
        return self.__node.adjust_parameters_basic(node_context)

    def __configure_widget(self, inputs=None, node_context=None):
        """
        Internal method (for testing only).
        """
        if node_context is None:
            node_context = self.__build_node_context(inputs)
            self.__node.adjust_parameters_basic(node_context)
        widget = self.__node._execute_parameter_view(
            node_context, return_widget=True)
        return widget

    def __configure(self, inputs, return_widget):
        """
        Create configuration by launching parameter GUI.
        """
        ports = self.__parameters['ports']
        with _instantiated_ports(ports, inputs):
            node_inputs = _build_ports(inputs, ports.get('inputs', []))
            builder = node.ManualContextBuilder(node_inputs, OrderedDict(),
                                                False, check_fns=False)

            try:
                return self.__node._sys_exec_parameter_view(
                    self.__parameters, {}, builder=builder,
                    return_widget=return_widget)
            finally:
                state.node_state().cleardata()

    @property
    def parameters(self):
        return self.__syiparameters

    @parameters.setter
    def parameters(self, value):
        assert(self.node_cls == value.node_cls)
        value = copy.deepcopy(value)
        self.__syiparameters = value
        self.__parameters = value.parameters

    @property
    def filename(self):
        return self.__filename

    @property
    def node_cls(self):
        return type(self.__node)


class SyiGetAttribute(object):
    def __init__(self, params, path):
        self.__params = params
        self.__path = path

    def __getattribute__(self, name):
        params = object.__getattribute__(self, '_SyiGetAttribute__params')
        path = object.__getattribute__(self, '_SyiGetAttribute__path')
        data = params.data

        for seg in path:
            data = data[seg]

        if name in data.keys():
            value = data[name]
            if isinstance(value, parameter_helper.ParameterGroup):
                return SyiGetAttribute(
                    params, path + [name])
            else:
                return data[name]
        return object.__getattribute__(self, name)

    def __dir__(self):
        params = object.__getattribute__(self, '_SyiGetAttribute__params')
        path = object.__getattribute__(self, '_SyiGetAttribute__path')
        data = params.data

        for seg in path:
            data = data[seg]

        return data.keys()


class SyiParameters(object):
    def __init__(self, node_cls, parameters):
        self.__node_cls = node_cls
        self.__parameters = parameters

    @property
    def attributes(self):
        return SyiGetAttribute(self, [])

    @property
    def node_cls(self):
        return self.__node_cls

    @property
    def data(self):
        return syparameters(
            self.__parameters['parameters'].get('data', {}))

    @data.setter
    def data(self, value):
        value = copy.deepcopy(value)
        self.__parameters['parameters']['data'] = value._parameters_dict


class SyiLibrary(object):
    def __init__(self, context, library, name_library):
        self.__context = context
        self.__library = dict(group_pairs(library.items()))
        self.__name_library = dict(group_pairs(name_library))

    def context(self):
        return self.__context

    def node(self, nid, fuzzy_names=True):
        # Attempt to get the node matching nid.
        def get_node_dict(result):
            if len(result) == 1:
                return result[0]
            elif len(result) > 1:
                raise KeyError('Multiple names matching: {}'.format(
                    [(v['id'], v['name']) for v in result]))

        node_dict = None

        for group in [self.__library, self.__name_library]:
            result = group.get(nid, None)
            if result is not None:
                node_dict = get_node_dict(result)
                if node_dict:
                    break

        if node_dict is None and fuzzy_names:
            result = fuzzy_filter(nid, self.__name_library.items())
            node_dicts = [node_dict_
                          for k, v in result for node_dict_ in v]
            if len(node_dicts) == 1:
                node_dict = node_dicts[0]
            elif len(node_dicts) > 1:
                raise KeyError('Multiple names matching: {}'.format(
                    [(v['id'], v['name']) for v in node_dicts]))

        if node_dict is None:
            raise KeyError(
                'Identifier does not match any nodeid or node name.')

        if node_dict.get('type') == 'flow':
            raise InteractiveNotNodeError

        with self.__context:
            local_filename = uri_to_path(node_dict['file'])
            sys.path.insert(0, os.path.dirname(local_filename))
            modulename = os.path.splitext(os.path.basename(local_filename))[0]
            module = __import__(modulename)

            return SyiNode(
                self.__context,
                getattr(module, node_dict['class'])(),
                {'parameters': node_dict['parameters'],
                 'label': node_dict['name'],
                 'ports': node_dict['ports']},
                local_filename)

    def nodeids(self):
        return self.__library.keys()


def _build_ports(values, ports):
    assert(values is None or len(values) == len(ports))
    result = OrderedDict()
    if values is None:
        # Construct dummy data to allow configuration without value.
        for port in ports:
            data = port_util.port_maker(port, None,
                                        None,
                                        no_datasource=True)
            result[port['file']] = data
    else:
        for port, value in zip(ports, values):
            result[port['file']] = value

    return result


def available_libraries(gui=True):
    from Gui import (util, version, task_worker)
    launch.setup_environment(os.environ)
    # Using QApplication instead of QCoreApplication on darwin
    # due to error: 'Too many open files (signaler.cpp:392)'.
    # On Windows to avoid QPixmap errors.
    try:
        if gui:
            app = QtGui.QApplication([])
        else:
            app = QtCore.QCoreApplication([])
    except RuntimeError:
        app = QtGui.qApp

    util.create_default_folder()
    util.create_install_folder()
    util.create_session_folder()

    app.setApplicationName(version.application_name())
    app.setApplicationVersion(version.version)

    util.create_storage_folder()

    paths = task_worker.Paths(_app_dir)

    return paths.library_paths()


def load_library(gui=True):
    from Gui import (settings, util, version, task_worker, library_creator,
                     library_manager)
    sys_path = list(sys.path)
    launch.setup_environment(os.environ)
    # Using QApplication instead of QCoreApplication on darwin
    # due to error: 'Too many open files (signaler.cpp:392)'.
    # On Windows to avoid QPixmap errors.
    try:
        if gui:
            app = QtGui.QApplication([])
        else:
            app = QtCore.QCoreApplication([])
    except RuntimeError:
        app = QtGui.qApp

    util.create_default_folder()
    util.create_install_folder()
    util.create_session_folder()
    types.manager.normalize()
    session_folder = settings.instance()['session_folder']

    app.setApplicationName(version.application_name())
    app.setApplicationVersion(version.version)

    util.create_storage_folder()

    storage_folder = settings.instance()['storage_folder']
    paths = task_worker.Paths(_app_dir)

    sys.path.extend(paths.common_paths())
    context = SyiContext(list(sys.path))
    state.node_state().set_attributes(
        library_dirs=paths.library_paths(),
        support_dirs=paths.support_paths(),
        worker_settings=settings.get_worker_settings(),
        node_settings={'node/flow_filename': ''})

    try:
        result = library_creator.create(
            paths.library_paths(), storage_folder, session_folder)

        node_library = library_manager.library_by_nodeid(result)
        name_library = library_manager.library_by_name(result)
        library = SyiLibrary(context, node_library, name_library)
        return library

    finally:
        sys.path[:] = sys_path
