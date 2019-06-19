# This file is part of Sympathy for Data.
# Copyright (c) 2016 Combine Control Systems AB
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
from __future__ import absolute_import, unicode_literals, print_function
import os
import six
import sys
import collections
import subprocess
import logging
from twisted.internet.error import ProcessExitedAlready
from twisted.internet import protocol, reactor, base, stdio
from twisted.protocols import basic
from . task_worker2 import (
    datalines, decode_json, encode_json,
    NEW_TASK, NEW_QUIT_TASK, UPDATE_TASK, ABORT_TASK, DONE_TASK,
    SET_WORKERS_TASK
)

# Monkey patch of checkProcessArgs to prevent twisted from re-encoding
# using default encoding.
base.ReactorBase._checkProcessArgs = lambda self, args, env: (args, env)

core_logger = logging.getLogger('core')
_module_file = os.path.abspath(__file__)


class TaskManager(object):
    def __init__(self, args, nworkers=1, environ=None, nocapture=False,
                 loglevel=0, node_loglevel=0):
        self.worker_args = args
        self.worker_env = environ
        self.nocapture = nocapture
        self.loglevel = loglevel
        self.node_loglevel = node_loglevel
        self.bufl = []
        self.nworkers = nworkers
        self.blocked_workers = set()
        self.free_workers = set()
        self.workers = set()
        self.wait_tasks = collections.OrderedDict()
        self.run_tasks = {}
        self.protocols = set()
        self.set_workers(nworkers)

    def dataReceived(self, data):
        def get_msgs():
            lines = datalines(data, self.bufl)
            return [decode_json(line) for line in lines]

        self.input_msgs(get_msgs())

    def input_msgs(self, msgs):
        for msg in msgs:
            taskid, cmd, args = msg
            if cmd == NEW_TASK:
                self.add_task(msg, False)
            elif cmd == NEW_QUIT_TASK:
                self.add_task(msg, True)
            elif cmd == UPDATE_TASK:
                self.update_task(msg)
            elif cmd == ABORT_TASK:
                self.abort_task(taskid)
            elif cmd == SET_WORKERS_TASK:
                self.set_workers(args)
            else:
                assert False

    def output_msg(self, msg):
        taskid, cmd, args = msg
        if cmd in [UPDATE_TASK, DONE_TASK]:
            for protocol_ in self.protocols:
                protocol_.sendData(encode_json(msg) + b'\n')

    def add_task(self, task, quit_after):
        taskid, cmd, data = task
        core_logger.debug('TaskManager.add_task %s', taskid)
        if quit_after:
            self.start_worker()

        if self.free_workers:
            if taskid not in self.run_tasks:
                self.start_task(task)
        else:
            self.wait_tasks[taskid] = task

    def _schedule_task(self, task=None):
        if task:
            self.start_task(task)
        elif self.wait_tasks:
            task = self.wait_tasks.popitem(False)[1]
            self.start_task(task)

    def start_task(self, task):
        taskid, cmd, data = task
        free_worker = self.free_workers.pop()
        if cmd == NEW_QUIT_TASK:
            self.blocked_workers.add(free_worker)
        self.run_tasks[taskid] = (free_worker, task)
        free_worker.start_task(task)
        core_logger.debug('TaskManager.start_task %s, %s', taskid, free_worker)

    def reply_done_task(self, task):
        taskid, cmd, args = task
        core_logger.debug('TaskManager.reply_done_task %s', taskid)
        worker, task_ = self.run_tasks.pop(taskid, (None, None))
        if worker and task_:
            taskid, cmd, data = task_
            if worker in self.blocked_workers:
                self.stop_worker(worker)
            else:
                self.free_workers.add(worker)
                self._schedule_task()

        self.output_msg(task)

    def reply_update_task(self, task):
        self.output_msg(task)

    def update_task(self, task):
        taskid, cmd, data = task
        worker = self.run_tasks.get(taskid, [None])[0]
        if worker:
            worker.update_task(task)

    def abort_task(self, taskid):
        self.wait_tasks.pop(taskid, None)
        worker = self.run_tasks.get(taskid, [None])[0]
        if worker:
            blocked = worker in self.blocked_workers
            self.stop_worker(worker)
            if not blocked:
                self._start_worker_schedule_task()

    def worker_exited(self, worker, status):
        blocked = worker in self.blocked_workers
        if blocked:
            self.blocked_workers.remove(worker)

        if worker in self.workers:
            self.workers.remove(worker)

            if worker in self.free_workers:
                self.free_workers.remove(worker)
                self._start_worker_schedule_task()
            else:
                for taskid, (worker_, task) in list(self.run_tasks.items()):
                    if worker == worker_:
                        self.run_tasks.pop(taskid)
                        self.output_msg([taskid, DONE_TASK, status])
                        if not blocked:
                            self._start_worker_schedule_task()

    def start_worker(self):
        worker = TwistedProcessWorker(self)
        worker.start()
        self.workers.add(worker)
        self.free_workers.add(worker)
        return worker

    def _start_worker_schedule_task(self):
        self.start_worker()
        self._schedule_task()

    def stop_worker(self, worker):
        if worker in self.workers:
            self.workers.remove(worker)
            if worker in self.blocked_workers:
                self.blocked_workers.remove(worker)
            # Remove task before stopping worker.
            if worker in self.free_workers:
                self.free_workers.remove(worker)
            worker.stop()

    def set_workers(self, nworkers=None):
        self.nworkers = nworkers or self.nworkers
        self.blocked_workers = set(
            worker for worker, task in self.run_tasks.values())
        prev_free_workers = list(self.free_workers)
        self.free_workers = set()
        for worker in prev_free_workers:
            if worker not in self.blocked_workers:
                self.stop_worker(worker)
        for i in range(self.nworkers):
            self._start_worker_schedule_task()

    def stop(self):
        for worker in self.workers:
            self.blocked_workers.add(worker)
            worker.stop()


class TaskManagerProtocol(protocol.Protocol):
    def __init__(self, task_manager):
        self._tm = task_manager

    def connectionMade(self):
        core_logger.debug('TaskManagerProtocol.connectionMade')
        try:
            self.transport.setTcpKeepAlive(1)
        except AttributeError:
            pass
        self._tm.protocols.add(self)

    def connectionLost(self, reason):
        core_logger.debug('TaskManagerProtocol.connectionLost')
        self._tm.protocols.remove(self)

    def dataReceived(self, data):
        self._tm.dataReceived(data)

    def sendData(self, data):
        self.transport.write(data)


class TaskWorkerProtocol(protocol.Protocol):
    def __init__(self, worker):
        self._worker = worker
        self._bufl = []

    def connectionMade(self):
        core_logger.debug('TaskWorkerProtocol.connectionMade')
        try:
            self.transport.setTcpKeepAlive(1)
        except AttributeError:
            pass
        self._worker.protocols.add(self)

    def connectionLost(self, reason):
        core_logger.debug('TaskWorkerProtocol.connectionLost %s', self._worker)
        self._worker.protocols.remove(self)

    def dataReceived(self, data):
        def get_msgs():
            lines = datalines(data, self._bufl)
            return [decode_json(line) for line in lines]
        msgs = get_msgs()
        self._worker.output_msgs(msgs)

    def sendData(self, data):
        self.transport.write(data)


class TaskWorkerFactory(protocol.Factory):
    def __init__(self, worker):
        self._worker = worker

    def buildProtocol(self, addr):
        return TaskWorkerProtocol(self._worker)


class WorkerProcessProtocol(protocol.ProcessProtocol):

    def __init__(self, worker):
        self._worker = worker

    def connectionMade(self):
        core_logger.debug('WorkerProcessProtocol.connectionMade')

    def connectionLost(self, reason):
        core_logger.debug(
            'WorkerProcessProtocol.connectionLost %s', self._worker)

    def processExited(self, status):
        core_logger.debug('WorkerProcessProtocol.processExited')
        self._worker.exited(status.value.exitCode or 0)

    def processEnded(self, status):
        core_logger.debug('WorkerProcessProtocol.processEnded')

    def childDataReceived(self, childFD, data):

        if childFD == 1:
            if six.PY2:
                out = sys.stdout
            else:
                out = sys.stdout.buffer

            out.write(data)
            out.flush()

        elif childFD == 2:
            if six.PY2:
                err = sys.stderr
            else:
                err = sys.stderr.buffer

            err.write(data)
            err.flush()


class MasterProcessProtocol(protocol.ProcessProtocol):

    def __init__(self, master):
        self._master = master
        self.bufl = []

    def connectionMade(self):
        core_logger.debug('MasterProcessProtocol.connectionMade')

    def connectionLost(self, reason):
        core_logger.debug('MasterProcessProtocol.connectionLost')

    def processExited(self, status):
        core_logger.debug('MasterProcessProtocol.processExited')
        self._master.exit_code = status.value.exitCode or 0
        reactor.stop()

    def processEnded(self, status):
        core_logger.debug('MasterProcessProtocol.processEnded')

    def childDataReceived(self, childFD, data):
        if childFD == 1:
            stream = sys.stdout

        elif childFD == 2:
            stream = sys.stderr

        if six.PY3:
            data = data.decode('utf8', errors='replace')

        stream.flush()

        try:
            stream.write(data)
        except UnicodeDecodeError:
            stream.write(data.decode('ascii', errors='ignore'))
        stream.flush()


class TwistedProcessMaster(object):
    def __init__(self, port, args, env):
        self.port = port
        self.args = args
        self.env = env
        self._transport = None
        self.exit_code = 0

    def start(self):
        env = dict((self.env or dict(os.environ)).items())
        env['SY_TASK_MANAGER_PORT'] = str(self.port)
        env['SY_TASK_MANAGER_PID'] = str(os.getpid())
        self._transport = reactor.spawnProcess(
            MasterProcessProtocol(self),
            sys.executable, args=self.args, env=env)

    def stop(self):
        try:
            self._transport.signalProcess('KILL')
        except ProcessExitedAlready:
            pass

    def close_stdin(self):
        self._transport.closeStdin()

    def write(self, data):
        self._transport.write(data)


class TwistedProcessWorker(object):
    _script = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), 'task_worker2.py'))

    def __init__(self, task_manager):
        self._tm = task_manager
        self._transport = None
        self._closed = True
        self._port = None
        self.protocols = set()

    def input_msg(self, msg):
        if not self._closed:
            taskid, cmd, data = msg
            if cmd in [NEW_TASK, NEW_QUIT_TASK]:
                self._transport.writeToChild(0, encode_json(msg) + b'\n')
            else:
                for protocol_ in self.protocols:
                    protocol_.sendData(encode_json(msg) + b'\n')

    def output_msgs(self, msgs):
        for msg in msgs:
            taskid, cmd, args = msg
            if cmd == DONE_TASK:
                self._tm.reply_done_task(msg)
            elif cmd == UPDATE_TASK:
                self._tm.reply_update_task(msg)
            else:
                assert False

    def start_task(self, task):
        self.input_msg(task)

    def update_task(self, task):
        self.input_msg(task)

    def exited(self, status):
        self.stop()
        self._tm.worker_exited(self, status)

    def start(self):
        self._port = reactor.listenTCP(
            0, TaskWorkerFactory(self), interface='localhost')

        env = self._tm.worker_env or dict(os.environ)
        if self._tm.nocapture:
            env['SY_NOCAPTURE'] = str(1)

        mod_str, func_str = self._tm.worker_args.split(':')

        self._transport = reactor.spawnProcess(
            WorkerProcessProtocol(self),
            sys.executable, args=[
                sys.executable, '-u',
                self._script,
                str(self._port.getHost().port), str(os.getpid()),
                str(self._tm.loglevel),
                str(self._tm.node_loglevel)],
            env=env)
        self._closed = False

    def stop(self):
        self._port.stopListening()
        try:
            self._transport.signalProcess('KILL')
        except ProcessExitedAlready:
            pass
        self._close()

    def join(self):
        pass

    def _close(self):
        self._closed = True


class TaskManagerFactory(protocol.Factory):
    def __init__(self, task_manager):
        self._tm = task_manager

    def buildProtocol(self, addr):
        return TaskManagerProtocol(self._tm)


class StdioForward(basic.LineReceiver):

    def __init__(self, process_master):
        self._pm = process_master

    def dataReceived(self, data):
        self._pm.write(data)

    def connectionLost(self, reason=None):
        self._pm.close_stdin()


def start(worker_args, master_args, nworkers, worker_environ, master_environ,
          nocapture, loglevel=0, node_loglevel=0, pipe=False):
    task_manager = TaskManager(
        worker_args, nworkers, worker_environ, nocapture, loglevel,
        node_loglevel)
    transport = reactor.listenTCP(
        0, TaskManagerFactory(task_manager), interface='localhost')
    port = transport.getHost().port
    master = TwistedProcessMaster(port, master_args, master_environ)
    if pipe:
        stdio_recv = StdioForward(master)
        stdio.StandardIO(stdio_recv)
    try:
        master.start()
        reactor.run()
    finally:
        task_manager.stop()
        master.stop()
    sys.exit(master.exit_code)


def start_external(worker_args, nworkers, worker_environ, nocapture,
                   stdout=None, stderr=None):
    cwd = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), os.pardir))

    args = encode_json(
        repr([worker_args, nworkers, worker_environ, nocapture])).decode(
            'ascii')

    args = ['-u', '-c', """
from __future__ import absolute_import, unicode_literals, print_function
import ast
import logging
logging.basicConfig()
from Gui import task_manager2
from Gui.task_worker2 import decode_json
worker_args, nworkers, worker_environ, nocapture = ast.literal_eval(
    decode_json(b'{args}'))
task_manager = task_manager2.TaskManager(
    worker_args, nworkers, worker_environ, nocapture)
transport = task_manager2.reactor.listenTCP(
    0, task_manager2.TaskManagerFactory(task_manager), interface='localhost')
port = transport.getHost().port
print('manager port:', str(port))
try:
    task_manager2.reactor.run()
finally:
    task_manager.stop()
    """.format(args=args)]

    if isinstance(sys.executable, six.binary_type):
        args = [sys.executable] + [arg.encode('ascii') for arg in args]
    else:
        args = [sys.executable] + args

    if stdout is None:
        stdout = subprocess.PIPE
    if stderr is None:
        stderr = subprocess.STDOUT

    p = subprocess.Popen(
        args,
        cwd=cwd,
        stdout=stdout, stderr=stderr)

    while True:
        line = p.stdout.readline()
        import time
        time.sleep(2)
        print(line)
        if line.startswith(b'manager port: '):
            return p, int(line.split(b' ')[2].strip())
    return p
