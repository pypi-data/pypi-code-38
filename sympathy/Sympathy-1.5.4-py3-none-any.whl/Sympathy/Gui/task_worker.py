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
Sympathy worker used to start Sympathy Python worker processes.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import os
import logging
import contextlib
import six
from . import util
from . import settings
from sympathy.platform import version_support as vs
from . import task_worker2
from sympathy.utils.prim import absolute_paths
from sympathy.platform import message_util
import PySide.QtNetwork as QtNetwork


_client = None
core_logger = logging.getLogger('core')


def _client_instance():
    global _client
    if _client is None:
        _client = TaskClient()
        _client.setup()
    return _client


class TaskClient(message_util.QtMessageReader):

    def __init__(self, parent=None):
        super(message_util.QtMessageReader, self).__init__(parent=parent)
        self._next_taskid = 0
        self._buf = [b'']
        self._qiodev = QtNetwork.QTcpSocket()
        self._qiodev.setSocketOption(
            QtNetwork.QAbstractSocket.SocketOption.KeepAliveOption, True)
        self._qiodev.readyRead.connect(self._read)

    def setup(self):
        try:
            port = settings.instance()['task_manager_port']
        except KeyError:
            # Not set when in extract mode.
            pass
        else:
            self._qiodev.connectToHost('127.0.0.1', port)
            if self._qiodev.waitForConnected():
                pass

    def read(self):
        data = self._qiodev.readAll().data()
        lines = task_worker2.datalines(data, self._buf)
        msgs = [task_worker2.decode_json(line) for line in lines]
        return msgs

    def add_task(self, data, quit_after):
        taskid = self._next_taskid
        yield taskid
        self._next_taskid += 1
        cmd = (task_worker2.NEW_QUIT_TASK
               if quit_after
               else task_worker2.NEW_TASK)
        msg = [taskid, cmd, data]
        self._qiodev.write(task_worker2.encode_json(msg) + b'\n')

    def abort_task(self, taskid):
        msg = [taskid, task_worker2.ABORT_TASK, None]
        self._qiodev.write(task_worker2.encode_json(msg) + b'\n')

    def update_task(self, taskid, data):
        msg = [taskid, task_worker2.UPDATE_TASK, data]
        self._qiodev.write(task_worker2.encode_json(msg) + b'\n')

    def set_workers(self, nworkers=None):
        msg = [None, task_worker2.SET_WORKERS_TASK, nworkers]
        self._qiodev.write(task_worker2.encode_json(msg) + b'\n')

    @contextlib.contextmanager
    def await_done(self, task):
        taskid = six.next(task)
        for _ in task:
            pass

        self.set_block(True)
        wait_msgs = []
        done = False
        while not done:
            self.wait(-1)
            msgs = iter(self.read())
            for msg in msgs:
                taskid_, cmd, data = msg
                if taskid_ == taskid and cmd == task_worker2.DONE_TASK:
                    done = True
                    wait_msgs.extend(msgs)
                    yield msg
                    break
                else:
                    wait_msgs.append(msg)
            wait_msgs.extend(msgs)
        if wait_msgs:
            self.received.emit(wait_msgs)
        self.set_block(False)

    def close(self):
        self._qiodev.close()


def create_client():
    return _client_instance()


def close_client():
    _client_instance().close()


class ProcessError(Exception):
    def __init__(self, status):
        self.status = status
        super(ProcessError, self).__init__('')

    def __str__(self):
        return 'Failed with code {}'.format(self.status)


def set_workers(workers):
    """
    Create the requested number of workers after terminating any existing
    workers. It is important to make sure that no tasks are in the air
    before this function is called. This can be assured by waiting for
    tasks to complete or by aborting them. Setting workers to the same
    number essentially performs a worker restart.
    """
    _client_instance().set_workers(workers)


class Paths(object):
    """Convenience class for accessing paths in the desired format."""
    def __init__(self, install_path=None):
        self._install_path = install_path

    def install_path(self):
        return (self._install_path or
                settings.instance()['install_folder'])

    def python_paths(self):
        return util.python_paths()

    def support_paths(self):
        return absolute_paths(self.install_path(), ['Python'])

    def library_paths(self):
        return util.library_paths()

    def common_paths(self):
        result = []
        for library in self.library_paths():
            result.append(os.path.join(library, 'Common'))
        return result

    def environ(self):
        return vs.OS.environ

    def sys_path(self):
        return list(vs.SYS.path)


paths = Paths()


def common_env():
    python_paths = paths.python_paths()
    common_paths = paths.common_paths()
    support_paths = paths.support_paths()
    settings_ = settings.get_worker_settings()
    return (
        dict(paths.environ().items()),
        paths.library_paths(),
        (paths.sys_path() + python_paths + support_paths +
         common_paths),
        python_paths + support_paths + common_paths,
        settings.instance()['install_folder'],
        settings.instance()['session_folder'],
        settings_)


def worker(action, log_fq_filename, quit_after=False):
    """Internal function called by the Sympathy platform to start
    Python processes where the node will execute.
    """
    return _base_worker(
        (action + common_env() + (log_fq_filename,)),
        quit_after)


def worker_light(action):
    """Internal function called by the Sympathy platform to wrap Python
    function calls in order to intercept exceptions, stdout and stderr.
    """
    return worker(action + common_env(), None, quit_after=False)


def aggregated_parameter_view_worker(action, quit_after=True):
    """Internal function called by Sympathy for Data platform to show
    aggregated parameter views for a flow."""
    return _base_worker(
        action + common_env(), quit_after)


def _base_worker(arguments, quit_after=True):
    return iter(_client_instance().add_task(arguments, quit_after))


def abort_task(taskid):
    _client_instance().abort_task(taskid)


def await_done(taskid):
    return _client_instance().await_done(taskid)


def update_task(taskid, data):
    return _client_instance().update_task(taskid, data)
