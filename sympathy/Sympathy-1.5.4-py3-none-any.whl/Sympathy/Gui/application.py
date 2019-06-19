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
"""
Main GUI and CLI application entry point.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import sys
import os
import functools
import six
import signal
import psutil

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

from sympathy.platform import arg_parser
from sympathy.platform import node_result
from sympathy.platform import version_support as vs
from sympathy.platform import os_support as oss

from . import execore
from . import appcore
from . import version
from . import util
from . import task_worker
from . import settings
from . import flow
from . import cli_application
from . import common


# Python's default recursion limit (1000) is a bit low. We currently hit that
# ceiling when recursively traversing big (hundreds of nodes) workflows. This
# is an easier fix than optimizing those graph algorithms.
sys.setrecursionlimit(10000)


def connect_app_and_exe(app_core, exe_core):
    # Signals from app_core
    app_core.execute_nodes_requested[set].connect(exe_core.execute_nodes)
    app_core.debug_nodes_requested[set].connect(exe_core.debug_nodes)
    app_core.profile_nodes_requested[set, set].connect(exe_core.profile_nodes)

    app_core.abort_node_requested[six.text_type].connect(
        exe_core.abort_node)

    app_core.validate_node_requested[flow.Node].connect(
        exe_core.validate_node)
    app_core.execute_node_parameter_view_requested[flow.Node].connect(
        exe_core.execute_node_parameter_view)
    app_core.execute_subflow_parameter_view_requested[
        flow.Flow, six.text_type].connect(
            exe_core.execute_subflow_parameter_view)
    app_core.execute_port_viewer[flow.Port].connect(
        exe_core.execute_port_viewer)
    app_core.node_library_aliases.connect(exe_core.set_type_aliases)
    app_core.restart_all_task_workers.connect(
        exe_core.restart_all_task_workers)
    app_core.message_output.connect(
        exe_core.message_input)

    # Signals from exe_core
    exe_core.execute_node_done[six.text_type, int].connect(
        app_core.execute_node_done)
    exe_core.execute_child_node_done[
        six.text_type, six.text_type, node_result.NodeResult, bool].connect(
            app_core.execute_child_node_done)
    exe_core.node_output[six.text_type, node_result.NodeResult].connect(
        app_core.node_output)
    exe_core.info_output[six.text_type, node_result.NodeResult].connect(
        app_core.info_output)
    exe_core.node_has_aborted[six.text_type, list].connect(
        app_core.node_has_aborted)
    exe_core.node_is_aborting[six.text_type, list].connect(
        app_core.set_node_is_aborting)
    exe_core.validate_node_done[six.text_type, int].connect(
        app_core.validate_node_done)
    exe_core.node_progress_changed[six.text_type, float].connect(
        app_core.update_node_progress)
    exe_core.child_node_progress_changed[
        six.text_type, six.text_type, float].connect(
        app_core.update_child_node_progress)
    exe_core.execute_node_parameter_view_done[
        six.text_type, six.text_type].connect(
            app_core.execute_node_parameter_view_done)
    exe_core.execute_subflow_parameter_view_done[
        six.text_type, six.text_type].connect(
            app_core.execute_subflow_parameter_view_done)
    exe_core.node_is_queued[six.text_type].connect(
        app_core.set_node_status_queued)
    exe_core.node_execution_started[six.text_type].connect(
        app_core.set_node_status_execution_started)
    exe_core.all_nodes_finished.connect(
        app_core.all_execution_has_finished)
    exe_core.profiling_finished[set].connect(
        app_core.profiling_finished)
    exe_core.message_output.connect(
        app_core.message_input)


def create_server():
    settings.instance()['task_manager_port'] = int(
        vs.OS.environ['SY_TASK_MANAGER_PORT'])


def basic_setup(app):
    app_core = appcore.AppCore(parent=app)
    # app_core.reload_node_library()
    exe_core = execore.ExeCore(parent=app)
    execore.working_dir = six.moves.getcwd()
    connect_app_and_exe(app_core, exe_core)
    return app_core, exe_core


def kill(ppid):
    if not psutil.pid_exists(ppid):
        os.kill(os.getpid(), signal.SIGTERM)


def common_setup(app):
    # app.processEvents()
    create_server()
    task_worker.create_client()
    util.create_default_folder()
    util.create_install_folder()
    util.setup_resource_folder()
    # WARNING: create_storage_folder depends on the application name (via
    # QDesktopServices.storageLocation). Make sure to use setApplicationName
    # before common_setup.
    util.create_storage_folder()
    # Moved before creating AppCore, and ExeCore to enable use of server tasks
    # while initiating these components.
    return basic_setup(app)


def common_teardown(app_core):
    # Gracefully exit appcore and deallocate resources used by the platform.
    task_worker.close_client()
    util.post_execution()


def start_syg(args, sys_args):
    # Made imports internal to the function to avoid pulling dependencies into
    # the CLI and the Extract code path. Alternatively this function could be
    # moved to a separate module with these two dependencies on the toplevel
    # (as well as application.py).
    oss.set_high_dpi_unaware()
    oss.set_application_id()

    from . import main_window
    from . import gui_manager

    app = QtGui.QApplication(sys_args)
    app.setApplicationName(version.application_name())
    app_core, exe_core = common_setup(app)
    QtCore.QLocale.setDefault(QtCore.QLocale('C'))
    app.setWindowIcon(QtGui.QIcon(util.icon_path('application.png')))
    app.setApplicationVersion(version.version)
    main_window_ = main_window.MainWindow(app_core, args)
    gui_manager_ = gui_manager.GuiManager(main_window_, app_core, parent=app)
    main_window_.show()
    main_window_.raise_()
    main_window_.activateWindow()
    if args.filename is not None and len(args.filename) > 0:
        flow_filename = cli_application.flow_filename_depending_on_configfile(
            args.filename, args.configfile)

        QtCore.QTimer.singleShot(
            0, functools.partial(
                gui_manager_.open_flow_from_file, flow_filename))
    elif not settings.instance()['save_session']:
        QtCore.QTimer.singleShot(0, gui_manager_.create_flow)

    def interrupt_handler(signum, frame):
        main_window_.quit_application()

    signal.signal(signal.SIGINT, interrupt_handler)

    ppid = os.environ.get('SY_TASK_MANAGER_PID')
    if ppid:
        ppid = int(ppid)
        kill_timer = QtCore.QTimer()
        kill_timer.timeout.connect(lambda: kill(ppid))
        kill_timer.start(200)

    return_code = app.exec_()
    common_teardown(app_core)
    return return_code


def start_sy(args, sys_args):
    if args.version:
        print('{} {}'.format(
            version.application_name(),
            version.version))
        return common.return_value('success')

    documentation = args.generate_documentation

    if documentation:
        if not documentation:
            arg_parser.instance().print_help()
            return common.return_value('success')

    elif args.filename:
        if vs.decode(os.path.basename(args.filename), vs.fs_encoding) == '-':
            pass
        elif not os.path.isfile(args.filename):
            common.print_error('no_such_file')
            return common.return_value('no_such_file')

    # Using QApplication instead of QCoreApplication on
    # Windows to avoid QPixmap errors.
    if sys.platform in ('win32'):
        app = QtGui.QApplication(sys_args)
    else:
        app = QtCore.QCoreApplication(sys_args)
    app.setApplicationName(version.application_name())
    app.setApplicationVersion(version.version)

    app_core, exe_core = common_setup(app)

    application = cli_application.Application(app, app_core, args)
    QtCore.QTimer.singleShot(0, application.run)
    ppid = os.environ.get('SY_TASK_MANAGER_PID')
    if ppid:
        ppid = int(ppid)
        kill_timer = QtCore.QTimer()
        kill_timer.timeout.connect(lambda: kill(ppid))
        kill_timer.start(200)

    return_code = app.exec_()
    common_teardown(app_core)
    return return_code


def _named_application():
    try:
        app = QtCore.QCoreApplication([])
    except RuntimeError:
        app = QtCore.QCoreApplication.instance()

    app.setApplicationName(version.application_name())
    app.setApplicationVersion(version.version)
    return app


def extract_lambdas(filenames, datatype, env, lib, folders, identifier):
    app = _named_application()

    for key, value in folders.items():
        settings.instance()['{}_folder'.format(key)] = value

    app_core, exe_core = basic_setup(app)
    app_core.set_library_dict(lib)

    result = []
    application = cli_application.LambdaExtractorApplication(
        app, app_core, exe_core, filenames, identifier, env, result)
    QtCore.QTimer.singleShot(0, application.run)
    app.exec_()
    return result


def clear(session=False, storage=False):
    app = _named_application()  # NOQA
    if session:
        print('Clearing sessions in:', util.sessions_folder())
        try:
            util.remove_sessions_folder()
        except OSError:
            # Nothing to do, assuming not existing.
            pass
    if storage:
        print('Clearing caches in:', util.storage_folder())
        try:
            util.remove_storage_folders()
        except OSError:
            # Nothing to do, assuming not existing.
            pass


if __name__ == '__main__':
    return_code = start_syg()
    sys.exit(return_code)
