# This file is part of Sympathy for Data.
# Copyright (c) 2013-2016 Combine Control Systems AB
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
"""
Sympathy worker used to start Sympathy Python worker processes.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import six
import locale
import os
import sys
import json
import base64
import tempfile
import sqlite3
import cProfile as profile
import copy
import io
import traceback
import dask
from datetime import datetime
import warnings


# Add path to Python folder to be able to import sympathy package.
fs_encoding = sys.getfilesystemencoding()
if six.PY2:
    _pydir = b'Python'
else:
    _pydir = 'Python'
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__),
                 os.pardir, _pydir)))

startup_file = os.environ.get('PYTHONSTARTUP')
if startup_file:
    try:
        exec(open(startup_file).read())
    except:
        traceback.print_exc()

from PySide import QtGui, QtCore
from PySide import QtNetwork
from sympathy.utils.prim import uri_to_path
from sympathy.platform import state
from sympathy.platform import node_result
from sympathy.platform import os_support
from sympathy.platform import version_support as vs
from sympathy.utils import parameter_helper
from sympathy.types import types
from Gui import builtin
from Gui.config_aggregation import (ConfigurationAggregation, clean_flow_info)


capture_output = vs.OS.environ.get('SY_NOCAPTURE') != '1'


def set_high_dpi_unaware():
    os_support.set_high_dpi_unaware()


def write_run_config(filename, *args):
    def quote(filename):
        return filename.replace('\\', '\\\\')

    arguments = base64.b64encode(
        json.dumps(args).encode('ascii')).decode('ascii')
    source_file = args[0]
    data_filename = '{}.data.py'.format(filename)
    run_filename = '{}.run.py'.format(filename)
    run_config_string = """# -*- coding: utf-8 -*-
import sys
import os
import base64
import json
argumentsb64 = b'{arguments}'
arguments = json.loads(
    base64.b64decode(argumentsb64).decode('ascii'))
sys.path[:] = arguments[9]
sys.path.append('{file_dir}')
from Gui.task_worker_subprocess import debug_worker
""".format(arguments=str(arguments), file_dir=quote(vs.py_file_dir(__file__)))
    with io.open(data_filename, 'w', encoding='utf8') as run_config:
        run_config.write(run_config_string)

    with io.open(run_filename, 'w', encoding='utf8') as run_config:
        run_config.write("""# -*- coding: utf-8 -*-
from spyderplugins import p_sympathy
exec(open(u'{data_filename}').read())
dnc = debug_node_context = debug_worker(
    p_sympathy.Sympathy.GLOBAL, *arguments).open()
""".format(data_filename=quote(data_filename)))

    try:
        dbpath = os.path.join(tempfile.gettempdir(),
                              'sympathy_1.1.dbg.sqlite3')
        conn = sqlite3.connect(dbpath)
        conn.execute(
            'CREATE TABLE if not exists dbg (src text PRIMARY KEY, dst text)')
        conn.execute('insert or replace into dbg values (?, ?)',
                     (uri_to_path(source_file), run_filename))
        conn.commit()
    finally:
        conn.close()




def load_typealiases(typealiases):
    if typealiases:
        for key, value in typealiases.items():
            types.manager.add_load_typealias(key, value)
            utilmod = value['util'].split(':')[0]
            __import__(utilmod)
        types.manager.load_typealiases()


def _write_result_close(socket, data):
    chunk = 4096
    for i in range(0, len(data), chunk):
        socket.write(data[i: i + chunk])
        socket.waitForBytesWritten(-1)
    socket.close()


class PrintErrorApplication(QtGui.QApplication):

    def __init__(self, argv):
        super(PrintErrorApplication, self).__init__(argv)

    def notify(self, obj, evt):
        try:
            return super(PrintErrorApplication, self).notify(obj, evt)
        except:
            traceback.print_exc(file=sys.stderr)
            return False


class DebugNodeContextManager(object):

    def __init__(self, node, typealiases, parameters,
                 library_dirs, application_dir, session_dir, python_paths,
                 debug_state, node_settings):
        self._node = node
        self._typealiases = typealiases
        self._parameters = parameters
        self._library_dirs = library_dirs
        self._application_dir = application_dir
        self._session_dir = session_dir
        self._python_paths = python_paths
        self._gens = []
        self._debug_state = debug_state
        self._node_settings = node_settings

    def open(self):
        with state.state():
            try:
                # state.cache_hdf5_state()
                state.node_state().create(
                    library_dirs=self._library_dirs,
                    application_dir=self._application_dir,
                    session_dir=self._session_dir,
                    support_dirs=self._python_paths,
                    node_settings=self._node_settings)

                node_context = self._node._build_node_context(
                    self._parameters,
                    self._typealiases,
                    read_only=True)
                input_fileobjs = [input for input in node_context.input]
                output_fileobjs = [output for output in node_context.output]

                self._fileobjs = input_fileobjs + output_fileobjs
                return self._node.update_node_context(
                    node_context,
                    input_fileobjs,
                    output_fileobjs,
                    parameters=parameter_helper.ParameterRoot(
                        node_context.parameters))
            finally:
                self._debug_state['opened'] = self
                self._debug_state['state'] = state.node_state()

    def close(self):
        try:
            for fileobj in reversed(self._fileobjs):
                fileobj.close()
        except TypeError:
            pass

        self._debug_state['state'].clear()
        self._debug_state['opened'] = None
        self._debug_state['state'] = None


def debug_worker(debug_state, source_file, library_dirs, class_name,
                 identifier,
                 json_parameters, type_aliases, action,
                 log_fq_filename, environ, path, python_paths, application_dir,
                 session_dir, working_dir, node_settings, worker_settings):
    os.chdir(working_dir)
    vs.OS.environ.update(environ)
    opened = debug_state.get('opened', None)
    if opened:
        opened.close()

    with state.state():

        try:
            # state.cache_hdf5_state()
            mod = builtin.source_module(source_file)
            node = getattr(mod, class_name)()
            state.node_state().create(library_dirs=library_dirs,
                                      application_dir=application_dir,
                                      session_dir=session_dir,
                                      support_dirs=python_paths,
                                      worker_settings=worker_settings,
                                      node_settings=node_settings)

            type_aliases = type_aliases
            parameters = json.loads(json_parameters)
            load_typealiases(type_aliases)

            if action == 'execute':
                node._sys_execute(parameters, type_aliases)
            return DebugNodeContextManager(
                node, type_aliases, parameters, library_dirs, application_dir,
                session_dir, python_paths, debug_state, node_settings)
        finally:
            state.node_state().clear()


def worker(io_bundle, action, *args,
           **kwargs):
    """
    Interface function to switch between different specialized workers.
    """
    warning_filters = warnings.filters[:]
    try:
        # Dask >= 0.18.
        dask_config = dask.config.set(scheduler='single-threaded')
    except AttributeError:
        dask_config = dask.set_options(get=dask.local.get_sync)
    with dask_config:
        if action == 'aggregated_parameter_view':
            return aggregated_parameter_view_worker(
                io_bundle, action, *args, **kwargs)
        else:
            node_worker(
                io_bundle, action, *args, **kwargs)
    warnings.filters[:] = warning_filters


def _log(times, mark, action, name, identifier=None, dt=None):
    assert(mark in '{}')

    if isinstance(action, list):
        action = ':'.join(action)

    if dt is None:
        dt = datetime.now()

    if identifier:
        times['{} "{}":{} {}'.format(
            action, name, identifier, mark)] = dt
    else:
        times['{} "{}" {}'.format(
            action, name, mark)] = dt


SocketBundle = builtin.SocketBundle


def setup_socket(port):
    socket = QtNetwork.QTcpSocket()
    socket.setSocketOption(
        QtNetwork.QAbstractSocket.SocketOption.KeepAliveOption, True)
    socket.connectToHost('127.0.0.1', port)
    if socket.waitForConnected(-1):
        pass
    return socket


def _execute_node(node, parameters, typealiases, context, result):
    coverage_tester = None
    if 'COVERAGE_PROCESS_START' in os.environ:
        from sympathy.utils.coverage import CoverageTester
        coverage_tester = CoverageTester()
        coverage_tester.start_coverage()

    node._sys_before_execute()
    node._sys_execute(parameters, typealiases)
    node._sys_after_execute()
    builtin.store_stdouterr(result, context, capture_output)
    if coverage_tester:
        coverage_tester.stop_coverage()


def node_worker(io_bundle, action, source_file, class_name,
                identifier, json_parameters, type_aliases, working_dir,
                node_settings, environ,
                library_dirs, path, python_paths,
                application_dir, session_dir,
                worker_settings,
                log_fq_filename):
    """
    Internal function called by the Sympathy platform to start
    Python processes where the node will execute.

    The returned value is a dictionary with the two following keys:
        exception_string = '' if valid is True and a string representation
            of the Exception otherwise.
        exception_trace = [] if valid is True and a list of strings
            containing the exception trace otherwise.
        output = None, on complete failure and otherwise depending on
            action. Every action has a default value and which will
            be used for the result in the exception case.
        stdout = String containing captured stdout.
        stderr = String containing captured stderr.
        valid = True if no unhandled Exception occured False otherwise.
    """
    beg = datetime.now()
    vs.OS.environ.update(environ)
    sys.path[:] = [vs.str_(p, vs.fs_encoding) for p in path]
    os.chdir(working_dir)
    context = {}
    builtin.capture_stdouterr(context, capture_output)
    result = node_result.NodeResult()
    name = ''

    if action in ['execute_parameter_view', 'execute_port_viewer']:
        # Must create QApplication before socket to ensure that events
        # can be handled by the Eventloop.
        os_support.set_application_id()
        application = PrintErrorApplication([])  # NOQA
        QtCore.QLocale.setDefault(QtCore.QLocale('C'))
    else:
        application = None

    socket = setup_socket(io_bundle.port)
    socket_bundle = SocketBundle(
        socket, io_bundle.input_func, io_bundle.output_func)
    try:
        # state.cache_hdf5_state()
        state.node_state().create(library_dirs=library_dirs,
                                  application_dir=application_dir,
                                  session_dir=session_dir,
                                  support_dirs=python_paths,
                                  worker_settings=worker_settings,
                                  node_settings=node_settings)

        result = state.node_state().result
        parameters = json.loads(json_parameters)
        load_typealiases(type_aliases)
        beg_compile = datetime.now()
        mod = builtin.source_module(source_file)
        node = getattr(mod, class_name)()
        node.socket_bundle = socket_bundle
        name = node.name

        _log(result.times, '{', ['node_worker', action], name, identifier, beg)
        _log(result.times, '{', ['node_worker', action, 'compile'], name,
             identifier, beg_compile)
        _log(result.times, '}', ['node_worker', action, 'compile'], name,
             identifier)
        _log(result.times, '{', ['node_worker', action, 'action'], name,
             identifier)

        if action == 'execute':
            _execute_node(node, parameters, type_aliases, context, result)

            with io.open(log_fq_filename, 'w', encoding='utf8') as out_file:
                out_file.write(result.format_std_output())
        elif action == 'profile':  # => 'execute'
            clean_identifier = ''.join(
                [c for c in identifier if c not in '{}'])
            stat_fq_filename = os.path.join(session_dir, '{}_{}.stat'.format(
                class_name, clean_identifier))
            result.output = ''
            # The code should be the same as performed in the 'execute' case,
            # the reason for not using a function here is to avoid adding an
            # extra level to tracebacks etc (there are already so many before
            # the user's node execute starts).
            prof = profile.Profile()
            prof.runcall(
                _execute_node, node, parameters, type_aliases, context, result)
            prof.dump_stats(stat_fq_filename)
        elif action == 'debug':  # => 'execute'
            clean_identifier = ''.join(
                [c for c in identifier if c not in '{}'])
            log_fq_filename = os.path.join(session_dir, '{}_{}.log'.format(
                class_name, clean_identifier))
            run_fq_filename = os.path.join(session_dir, '{}_{}'.format(
                class_name, clean_identifier))

            write_run_config(
                run_fq_filename,
                source_file, library_dirs, class_name, identifier,
                json_parameters,
                type_aliases, 'execute',
                log_fq_filename, environ, path, python_paths, application_dir,
                session_dir, working_dir, node_settings, worker_settings)

            os_support.run_spyder([uri_to_path(source_file)])

        elif action == 'validate_parameters':
            result.output = False
            result.output = node._sys_verify_parameters(
                parameters, type_aliases)
        elif action == 'execute_parameter_view':
            result.output = json_parameters
            result.output = json.dumps(node._sys_exec_parameter_view(
                parameters, type_aliases))
        elif action == 'test_parameter_view':
            result.output = json_parameters
            node._sys_exec_parameter_view(
                parameters, type_aliases, return_widget=True)
        elif action == 'execute_port_viewer':
            result.output = True
            node.exec_port_viewer(parameters)
            builtin.store_stdouterr(result, context, capture_output)
        elif action == 'adjust_parameters':
            assert False, 'Can this be removed?'
            result.output = json_parameters
            result.output = json.dumps(node._sys_adjust_parameters(
                parameters, type_aliases))
        elif action == 'execute_library_creator':
            libraries, temp_dir = parameters
            create_result = node.create(
                libraries, temp_dir, session_dir)
            builtin.store_stdouterr(result, context, capture_output)
            result.output = create_result
        else:
            print('Unsupported node action requested.')

        _log(result.times, '}', ['node_worker', action, 'action'], name,
             identifier)

        created_qapplication = QtCore.QCoreApplication.instance()
        if application:
            if application.clipboard().ownsClipboard():
                os_support.flush_clipboard()
        elif created_qapplication:
            print('WARNING: node created a QApplication, this will cause hard '
                  'crashes in worker processes. Please refrain from creating '
                  'QApplications except in separate subprocesses, '
                  'using matplotlib.pyplot in F(x) is a frequent cause.',
                  file=sys.stderr)
    except:
        result.valid = False
        result.store_current_exception(source_file)
    finally:
        state.node_state().clear()

    builtin.store_stdouterr(result, context, capture_output)
    builtin.restore_stdouterr(context, capture_output)
    result.stdout_limit = worker_settings.get('max_task_chars')
    result.stderr_limit = worker_settings.get('max_task_chars')
    if log_fq_filename:
        result.limit_footer = 'Wrote full output to: {}.'.format(
            log_fq_filename)

    _log(result.times, '}', ['node_worker', action], name,
         identifier)

    _write_result_close(socket, io_bundle.result_func(result))


def aggregated_parameter_view_worker(
        io_bundle, action, conf, json_flow_info, type_aliases,
        working_dir, environ,
        library_dirs, path, python_paths,
        application_dir, session_dir,
        worker_settings):

    vs.OS.environ.update(environ)
    os_support.set_application_id()
    sys.path[:] = [vs.str_(p, vs.fs_encoding) for p in path]
    os.chdir(working_dir)
    context = {}
    builtin.capture_stdouterr(context, capture_output)
    result = node_result.NodeResult()
    result.output = json_flow_info

    def add_instances(x):
        for key, value in x.items():
            if key == 'nodes':
                for node_info in value:
                    source_file = node_info['source_file']
                    class_name = node_info['class_name']
                    mod = builtin.source_module(source_file)
                    node_instance = getattr(mod, class_name)()
                    # Extra payload.
                    node_info['library_node_instance'] = node_instance
            elif key == 'flows':
                for flw in value:
                    add_instances(flw)

    application = PrintErrorApplication([])  # NOQA
    socket = setup_socket(io_bundle.port)
    socket_bundle = SocketBundle(
        socket, io_bundle.input_func, io_bundle.output_func)

    # TODO: Move to top level when shiboken is no longer being imported.

    try:
        # state.cache_hdf5_state()
        state.node_state().create(library_dirs=library_dirs,
                                  application_dir=application_dir,
                                  session_dir=session_dir,
                                  support_dirs=python_paths,
                                  worker_settings=worker_settings)
        load_typealiases(type_aliases)

        flow_info = json.loads(json_flow_info)

        # Store flow info without instances.
        old_flow_info = copy.deepcopy(flow_info)

        # Manage modifications to flow_info automatically.
        # with node_instances(flow_info) as modified_flow_info:
        add_instances(flow_info)
        aggregator = ConfigurationAggregation(conf,
                                              socket_bundle,
                                              flow_info,
                                              type_aliases)
        accept = aggregator.run()
        aggregator = None
        del aggregator
        flow_info = clean_flow_info(flow_info)

        if accept:
            result.output = json.dumps(flow_info)
        else:
            result.valid = False
            result.output = json.dumps(old_flow_info)

        if application.clipboard().ownsClipboard():
            os_support.flush_clipboard()
    except:
        result.valid = False
        result.store_current_exception()
    finally:
        state.node_state().clear()

    builtin.store_stdouterr(result, context, capture_output)
    builtin.restore_stdouterr(context, capture_output)

    result.stdout_limit = worker_settings.get('max_task_chars')
    result.stderr_limit = worker_settings.get('max_task_chars')
    _write_result_close(socket, io_bundle.result_func(result))


def main():
    json_parent_context = sys.argv[-1]
    parent_context = json.loads(json_parent_context)
    vs.OS.environ.update(parent_context['environ'])
    sys.path[:] = parent_context['sys.path']
    result = worker(*sys.argv[1:-1])
    sys.stdout.write(json.dumps(result,
                                encoding=locale.getpreferredencoding()))


if __name__ == '__main__':
    main()
