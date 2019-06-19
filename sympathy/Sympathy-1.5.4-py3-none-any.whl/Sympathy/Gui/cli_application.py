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
import sys
import datetime
import logging
import six
import time
from six import text_type

from sympathy.platform import workflow_operations
from sympathy.platform import version_support as vs
from sympathy.platform import exceptions
from Gui import common
from Gui import filename_manager as fm
from Gui.environment_variables import instance as env_instance
from Gui import settings

import PySide.QtCore as QtCore

core_logger = logging.getLogger('core')
node_logger = logging.getLogger('node')

LOCALHOST = '127.0.0.1'


def flow_filename_depending_on_configfile(args_filename, configfile):
    flow_filename = args_filename
    config_filenames, config_workflow_path = (
        workflow_operations.parse_config_arg(
            configfile))

    if config_filenames and os.path.exists(args_filename):
        if config_workflow_path is not None:
            flow_filename = config_workflow_path
        else:
            flow_filename = fm.instance().allocate_config_filename(
                os.path.basename(args_filename))
        workflow_operations.update_workflow_config(
            args_filename,
            workflow_operations.read_config_files(config_filenames),
            flow_filename,
            env_instance)

    return flow_filename


class Application(QtCore.QObject):
    """CLI Application"""
    quit = QtCore.Signal()
    results = QtCore.Signal(dict)

    def __init__(self, app, app_core, args, parent=None):
        parent = parent or app
        super(Application, self).__init__(parent)
        self._node_uuid_label_map = {}
        self._app = app
        self._app_core = app_core
        self._args = args
        self._flow = None
        self._error = False
        self._cwd = six.moves.getcwd()
        self._t0 = time.time()
        self._connect()
        self._app_core.reload_node_library()
        self._next_action = None

    def _connect(self):
        self._app_core.all_execution_has_finished.connect(self.finalize)
        self._app_core.node_output_received[text_type, dict].connect(
            self.print_node_output)
        self._app_core.node_library_output[text_type, dict].connect(
            self.print_node_output)
        self._app_core.node_error_message[text_type, text_type].connect(
            self.error)
        self._app_core.node_progress[text_type, float].connect(
            self.print_progress_message)

    def set_flow(self, flow_filename, config_filename):
        self._flow_filename = flow_filename_depending_on_configfile(
            flow_filename, config_filename)

    @QtCore.Slot()
    def run(self):

        if self._args.generate_documentation:
            self._app_core.reload_documentation(folder=self._args.filename)
            return self._app.exit(common.return_value('success'))
        elif self._args.generate_documentation:
            self._app_core.reload_documentation(folder=self._args.filename)
            return self._app.exit(common.return_value('success'))
        elif self._args.generate_documentation:
            self._app_core.reload_documentation(folder=self._args.filename)
            return self._app.exit(common.return_value('success'))

        else:
            if self._args.filename is None:
                return self._app.exit(common.return_value('success'))

            common.hash_support(self._app, self._app_core)
            common.log_environ(self._app, self._app_core)

            QtCore.QTimer.singleShot(0, self.build_flows)

    @QtCore.Slot()
    def finalize(self):
        if self._error:
            core_logger.info('Flow executed with error')
            self._process_exit(common.return_value('workflow_error'))
        else:
            core_logger.info(
                'Flow successfully executed in %ss', time.time() - self._t0)

            if self._next_action:
                self._next_action()
            else:
                self._process_exit(common.return_value('success'))

    def build_flows(self):
        self._error = False
        self._t0 = time.time()

        if vs.decode(os.path.basename(
                self._args.filename), vs.fs_encoding) == '-':
            self._next_action = self._wait_for_stdin_filename
            self._next_action()
        elif self._args.filename is not None:
            filename = os.path.abspath(
                vs.py_file(self._args.filename))
            self.set_flow(filename, self._args.configfile)
            core_logger.info('Using flow: {}'.format(filename))

            try:
                self.build_flow()
            except exceptions.ReadSyxFileError:
                common.print_error('corrupt_workflow')
                self._process_exit(common.return_value('corrupt_workflow'))

    def _wait_for_stdin_filename(self):
        self._t0 = time.time()
        try:
            filename = sys.stdin.readline()
            filename = filename.strip()

            if not filename:
                self._process_exit(common.return_value('success'))
            else:
                os.chdir(self._cwd)
                self.set_flow(os.path.abspath(filename),
                              self._args.configfile)
                try:
                    self.build_flow()
                except exceptions.ReadSyxFileError:
                    common.print_error('corrupt_workflow')
                    self._process_exit(
                        common.return_value('corrupt_workflow'))
        except Exception:
            common.print_error('corrupt_workflow')
            self._process_exit(common.return_value('corrupt_workflow'))

    @QtCore.Slot()
    def build_flow(self):
        core_logger.info(
            'Start processing flow: %s', self._flow_filename)

        os.chdir(self._cwd)
        self._flow = common.read_flow_from_file(
            self._app_core, self._flow_filename)
        self._update_environment()
        self._flow.validate()

        # Wait until all nodes have been validated.
        self.wait_for_pending()

    def wait_for_pending(self):
        if self._flow.has_pending_request():
            QtCore.QTimer.singleShot(100, self.wait_for_pending)
        else:
            self.execute_all()

    @QtCore.Slot()
    def execute_all(self):
        nodes = self._flow.node_set_list(remove_invalid=False)
        executable = all(node.is_executable() for node in nodes)

        if not executable:
            common.print_error('invalid_nodes')
            self._process_exit(common.return_value('invalid_nodes'))

        elif not nodes:
            common.print_error('empty_workflow')
            self._process_exit(common.return_value('empty_workflow'))
        else:
            self._flow.execute_all_nodes()

    def _update_environment(self):
        parameters = self._flow.parameters
        env = env_instance()
        if 'environment' in parameters:
            env.set_workflow_variables(parameters['environment'])
        else:
            parameters['environment'] = {}

        settings_ = settings.instance()
        env_vars = settings_['environment']
        env.set_global_variables(
            dict([env_var.split('=', 1) for env_var in env_vars]))

    def _process_exit(self, exitcode):
        self._app.exit(exitcode)

    @QtCore.Slot(text_type, float)
    def print_progress(self, full_uuid, progress):
        formatted_message = '{} PROGRESS {} {}'.format(
            datetime.datetime.isoformat(datetime.datetime.today()),
            full_uuid, progress)

        node_logger.info(formatted_message)

    @QtCore.Slot(text_type, text_type)
    def print_progress_message(self, full_uuid, message):
        formatted_message = '{} MESSAGE {} {}'.format(
            datetime.datetime.isoformat(datetime.datetime.today()),
            full_uuid, message)

        node_logger.debug(formatted_message)

    @QtCore.Slot(text_type, dict)
    def print_node_output(self, full_uuid, output):
        if output.has_error():
            self._error = True

        formatted_message = common.format_output_string(output)
        if formatted_message:
            formatted_message = '{} OUTPUT {}\n{}'.format(
                common.BLUE(
                    datetime.datetime.isoformat(datetime.datetime.today())),
                common.WHITE(full_uuid),
                formatted_message)

            node_logger.info(formatted_message)

    @QtCore.Slot(text_type, text_type)
    def error(self, full_uuid, message):
        self._error = True
        formatted_message = '{} ERROR {} {}'.format(
            datetime.datetime.isoformat(datetime.datetime.today()),
            full_uuid, message)

        node_logger.error(formatted_message)

    @QtCore.Slot(text_type)
    def print_state_change(self, full_uuid):
        formatted_message = '{} EXECUTE {} {}'.format(
            datetime.datetime.isoformat(datetime.datetime.today()), full_uuid)

        node_logger.info(formatted_message)


class LambdaExtractorApplication(Application):
    def __init__(self, app, app_core, exe_core, filenames, identifier, env,
                 result, parent=None):
        parent = parent or app
        super(Application, self).__init__(parent)
        self._node_uuid_label_map = {}
        self._app = app
        self._app_core = app_core
        self._exe_core = exe_core
        self._filenames = filenames
        self._identifier = identifier
        self._current_filename = None
        self._env = env
        # Input output parameter result.
        self._result = result
        self._result_dict = {}

        self._connect()

    def build_flows(self):
        filenames = self._filenames

        try:
            fm.instance().set_prefix(self._identifier)
            env = env_instance()
            env.set_global_variables(self._env['global'])
            env.set_shell_variables(self._env['shell'])
        except:
            for filename in filenames:
                self._result_dict[filename] = (False, 'Global extract failure')
            filenames = []

        try:
            self._app_core.set_reload_node_library_enabled(False)
            for filename in filenames:
                self._current_filename = filename
                try:
                    self._flow = common.read_flow_from_file(
                        self._app_core, filename)
                    self._update_workflow_environment()
                    self._result_dict[filename] = (True, self._flow)
                except:
                    self._result_dict[filename] = (False, 'Could not read file')
        finally:
            self._app_core.set_reload_node_library_enabled(True)

        self._result[:] = [(filename, self._result_dict[filename])
                           for filename in filenames]
        self._app.quit()

    def _update_workflow_environment(self):
        parameters = self._flow.parameters
        env = env_instance()
        workflow_variables = dict(self._env['workflow'])
        if 'environment' in parameters:
            workflow_variables.update(parameters['environment'])
        else:
            parameters['environment'] = {}

        env.set_workflow_variables(workflow_variables)

    def run(self):
        QtCore.QTimer.singleShot(0, self.build_flows)

    @QtCore.Slot(text_type, dict)
    def print_node_output(self, full_uuid, output):
        def print_with_path(path, data, file=sys.stdout):
            data = data.strip()
            if data:
                print(path, ':', '\n', data, file=file, sep='')

        if output.has_error():
            self._result_dict[self._current_filename] = (False, 'Error')

        flode = self._app_core.get_flode(full_uuid)
        paths = [flode.name]
        parent = flode.flow
        while parent is not None:
            paths.append(parent.name)
            parent = parent.flow
        path = ' > '.join(reversed(paths))
        print_with_path(path, output.stdout, file=sys.stdout)
        print_with_path(path, output.stderr, file=sys.stderr)
