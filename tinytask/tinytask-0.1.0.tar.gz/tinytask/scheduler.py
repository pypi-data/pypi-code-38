import os
import json
import shutil
import traceback

from enum import Enum
from uuid import UUID, uuid4
from functools import wraps
from tempfile import mkdtemp
from datetime import datetime
from multiprocessing import Process, Pipe

from .exceptions import TaskNotFoundError, TaskStartedError


def _task_or_die(func):
    '''
    For the Scheduler instance methods, discovers whether the first argument is
    a ``Task`` instance, or a string guid, and ensures the task exists first.
    If it doesn't exist, it raises ``TaskNotFoundError``.
    If it does, it invokes the decorated function with the task as the first
    argument.
    '''

    @wraps(func)
    def wrapped(self, task_or_guid, *args, **kwargs):
        if isinstance(task_or_guid, UUID):
            task_or_guid = str(task_or_guid)
        if isinstance(task_or_guid, str):
            guid = task_or_guid
            if guid not in self.tasks:
                raise TaskNotFoundError(
                    'cant find task with guid {}'.format(guid)
                )
            task = self.tasks[guid]
        else:
            task = task_or_guid
        return func(self, task, *args, **kwargs)

    return wrapped


class Command(Enum):
    quit = 0
    kill = 1
    start = 2
    get = 3


class Request:
    __slots__ = ('command', 'guid', 'function', 'args', 'kwargs')

    def __repr__(self):
        return (
            'Request({self.command.value}, {self.guid}, '
            '{self.function.__qualname__}, {self.args!r}, {self.kwargs!r})'
        ).format(self=self)

    def __init__(
        self, command, guid=None, function=None, args=None, kwargs=None,
    ):
        self.command = command
        self.guid = guid
        self.function = function
        self.args = args or ()
        self.kwargs = kwargs or {}


class ResponseType(Enum):
    success = 'success'
    error = 'error'
    not_found = 'not_found'


class Response:
    __slots__ = ('response_type', 'msg', 'data')

    def __repr__(self):
        return (
            'Response({self.response_type.value}, msg={self.msg!r}, '
            'data={self.data!r})'
        ).format(self=self)

    def __init__(self, response_type, msg=None, data=None):
        self.response_type = response_type
        self.msg = msg
        self.data = data

    @classmethod
    def error(cls, msg):
        return cls(ResponseType.error, msg=msg)

    @classmethod
    def not_found(cls, msg):
        return cls(ResponseType.not_found, msg=msg)

    @classmethod
    def success(cls, data):
        return cls(ResponseType.success, data=data)

    @property
    def type(self):
        return self.response_type.value

    @property
    def guid(self):
        if isinstance(self.data, SerializedTask):
            return self.data.guid
        try:
            guid = UUID(self.data)
        except ValueError:
            return None
        return str(guid)

    @property
    def status(self):
        if isinstance(self.data, SerializedTask):
            return self.data.status

    @property
    def running(self):
        if isinstance(self.data, SerializedTask):
            return self.data.running

    @property
    def done(self):
        if isinstance(self.data, SerializedTask):
            return self.data.done

    @property
    def pid(self):
        if isinstance(self.data, SerializedTask):
            return self.data.pid

    @property
    def exitcode(self):
        if isinstance(self.data, SerializedTask):
            return self.data.exitcode

    @property
    def result(self):
        if isinstance(self.data, SerializedTask):
            return self.data.result

    @property
    def result_type(self):
        if isinstance(self.data, SerializedTask):
            return self.data.result.result_type.value

    @property
    def result_data(self):
        if isinstance(self.data, SerializedTask):
            return self.data.result.data

    @property
    def task_started(self):
        if isinstance(self.data, SerializedTask):
            return self.data.result.started

    @property
    def task_finished(self):
        if isinstance(self.data, SerializedTask):
            return self.data.result.finished


class ResultType(Enum):
    # Successfully finished.
    success = 'success'
    # If wrapped function errored out.
    failed = 'failed'
    # If the result file is missing.
    not_found = 'not_found'
    # need timeout?


class Result:
    __slots__ = ('result_type', 'data', 'started', 'finished')

    def __repr__(self):
        result_type = self.result_type.value
        data = self.data
        started = self.started and self.started.isoformat()
        finished = self.finished and self.finished.isoformat()
        return (
            'Result({result_type}, data={data!r}, started={started!r}, '
            'finished={finished!r})'
        ).format(
            result_type=result_type, data=data, started=started,
            finished=finished,
        )

    def __init__(self, result_type, data, started, finished):
        self.result_type = result_type
        self.data = data
        self.started = started
        self.finished = finished

    def write(self, guid):
        path = os.path.join(Scheduler.RESULT_DIR, guid)
        lock = path + '.lock'
        with open(lock, 'w') as f:
            json.dump(self.serialize(), f)
        os.rename(lock, path)
        return path

    def serialize(self):
        # If not_found, it's None.
        started = self.started and self.started.timestamp()
        finished = self.finished and self.finished.timestamp()
        return {
            'type': self.result_type.value,
            'data': self.data,
            'started': started,
            'finished': finished,
        }

    @classmethod
    def deserialize(cls, serial):
        result_type = ResultType[serial['type']]
        data = serial['data']
        started, finished = serial['started'], serial['finished']
        started = started and datetime.fromtimestamp(started)
        finished = finished and datetime.fromtimestamp(finished)
        return cls(result_type, data, started, finished)

    @classmethod
    def get(cls, guid):
        path = os.path.join(Scheduler.RESULT_DIR, guid)
        if not os.path.exists(path):
            return cls(ResultType.not_found, None, None, None)
        with open(path) as f:
            serial = json.load(f)
        return cls.deserialize(serial)

    @classmethod
    def failed(cls, error, started, finished):
        return cls(ResultType.failed, error, started, finished)

    @classmethod
    def success(cls, data, started, finished):
        if isinstance(data, Task):
            data = data.serialize()
        return cls(ResultType.success, data, started, finished)


def _task_wrapper(function, guid):

    @wraps(function)
    def _function(*args, **kwargs):
        started = datetime.now()
        data = None
        error = None
        try:
            data = function(*args, **kwargs)
        except Exception:
            error = traceback.format_exc()
        finally:
            finished = datetime.now()
        if error is not None:
            result = Result.failed(error, started, finished)
        else:
            result = Result.success(data, started, finished)
        result.write(guid)
        return result

    return _function


class TaskStatus(Enum):
    created = 'created'
    running = 'running'
    killed = 'killed'
    complete = 'complete'
    failed = 'failed'

    @classmethod
    def done(cls):
        return {cls.killed, cls.complete, cls.failed}


class Task:
    __slots__ = ('guid', 'proc', 'function', '_status')

    def __repr__(self):
        proc_pid = self.proc and self.proc.pid
        func_name = self.function and self.function.__qualname__
        return (
            'Task({self.guid}, proc={proc_pid!r}, '
            'function={func_name}, '
            'status={self._status.value})'
        ).format(self=self, proc_pid=proc_pid, func_name=func_name)

    def __init__(self, function):
        self.guid = str(uuid4())
        self.proc = None
        self.function = function
        self._status = TaskStatus.created

    def _refresh_status(self):
        if self._status in TaskStatus.done():
            return
        if self.proc is None:
            self._status = TaskStatus.created
        elif self.proc.is_alive():
            self._status = TaskStatus.running
        else:
            result_type = self.result.result_type
            if result_type == ResultType.success:
                self._status = TaskStatus.complete
            else:
                # Could be not_found too...
                self._status = TaskStatus.failed

    @property
    def status(self):
        self._refresh_status()
        return self._status

    @property
    def running(self):
        return self.status == TaskStatus.running

    @property
    def pid(self):
        return self.proc and self.proc.pid

    @property
    def exitcode(self):
        return self.proc and self.proc.exitcode

    @property
    def result(self):
        return Result.get(self.guid)

    def serialize(self):
        return {
            'guid': self.guid,
            'status': self.status.value,
            'running': self.running,
            'done': self.status in TaskStatus.done(),
            'pid': self.pid,
            'exitcode': self.exitcode,
            'result': self.result,
        }

    def start(self, args=None, kwargs=None):
        args = args or ()
        kwargs = kwargs or {}
        if self.proc is not None:
            raise TaskStartedError('already started task with guid {}'.format(
                self.guid
            ))
        target = _task_wrapper(self.function, self.guid)
        self.proc = Process(target=target, args=args, kwargs=kwargs)
        self.proc.start()

    def kill(self):
        if self.running:
            self._status = TaskStatus.killed
            return self.proc.terminate()


class SerializedTask:
    __slots__ = (
        'guid', 'status', 'running', 'done', 'pid', 'exitcode', 'result',
    )

    def __repr__(self):
        return (
            'SerializedTask(guid={self.guid}, status={self.status}, '
            'running={self.running}, done={self.done}, pid={self.pid}, '
            'exitcode={self.exitcode}, result={self.result!r})'
        ).format(self=self)

    def __init__(
        self, guid=None, status=None, running=None, done=None, pid=None,
        exitcode=None, result=None,
    ):
        self.guid = guid
        self.status = status
        self.running = running
        self.done = done
        self.pid = pid
        self.exitcode = exitcode
        self.result = result

    @classmethod
    def deserialize(cls, data):
        return cls(**data)


class Scheduler:
    RESULT_DIR = mkdtemp(prefix='tinytask_')

    def __repr__(self):
        return (
            'Scheduler(concurrency={self.concurrency!r}, '
            '#tasks={len(self.tasks)}, #running={len(self.running)}, '
            '#waiting={len(self.waiting)}, '
            'child={self.child and self.child.pid!r})'
        ).format(self=self)

    def __init__(self, concurrency=None):
        self.concurrency = concurrency
        self.tasks = {}
        self.completed = {}
        self.running = {}
        self.waiting = {}
        self.waiting_tasks = []
        self.pipe = None
        self.scheduler_running = True
        self.child = None

    def _run(self, pipe):
        self.pipe = pipe
        while self.scheduler_running:
            try:
                data = self._listen()
            except TaskNotFoundError as e:
                self.pipe.send(Response.not_found(str(e)))
            except Exception:
                self.pipe.send(Response.error(traceback.format_exc()))
            else:
                # If pipe is closed or no message, don't send anything.
                if data is not None:
                    self.pipe.send(Response.success(data))

    def _listen(self):
        self._refresh_tasks()
        self._start_waiting()
        # Get next command.
        try:
            # Poll for one second, then just refresh tasks and start waiting
            # again.
            if not self.pipe.poll(1):
                return None
        except EOFError:
            self._quit()
            return None
        except KeyboardInterrupt:
            print('ctrl-c received')
            self._quit()
            return None
        try:
            request = self.pipe.recv()
        except EOFError:
            self._quit()
            return None
        except KeyboardInterrupt:
            print('ctrl-c received')
            self._quit()
            return None
        if request.command == Command.quit:
            # Scheduler should quit.
            return self._quit()
        task = self._task_from_request(request)
        # Check if it completed.
        if task.guid in self.running:
            self._refresh_task(task)
        if request.command == Command.kill:
            return self._kill_task(task)
        elif request.command == Command.start:
            if (
                self.concurrency is None or
                len(self.running) < self.concurrency
            ):
                return self._start_task(
                    task, args=request.args, kwargs=request.kwargs,
                )
            else:
                return self._wait_task(
                    task, args=request.args, kwargs=request.kwargs,
                )
        elif request.command == Command.get:
            return self._get(task)

    @_task_or_die
    def _refresh_task(self, task):
        if (
            task.guid in self.running and
            task.status in TaskStatus.done()
        ):
            self._complete_task(task)

    def _refresh_tasks(self):
        for task in list(self.running.values()):
            self._refresh_task(task)

    def _get_task(self, guid):
        if guid not in self.tasks:
            raise TaskNotFoundError('missing task with guid {}'.format(guid))
        return self.tasks[guid]

    def _task_from_request(self, request):
        if request.guid is not None:
            return self._get_task(request.guid)
        if request.function is not None:
            task = Task(request.function)
            self.tasks[task.guid] = task
            return task
        return None

    def _start_waiting(self):
        if self.concurrency is None:
            # None should be waiting.
            return
        while len(self.running) < self.concurrency and self.waiting_tasks:
            # Start from FIFO list.
            task, args, kwargs = self.waiting_tasks[0]
            self._start_task(task, args, kwargs)
            self.waiting_tasks = self.waiting_tasks[1:]
            del self.waiting[task.guid]

    def _start_task(self, task, args=None, kwargs=None):
        task.start(args=args, kwargs=kwargs)
        self.running[task.guid] = task
        return task.guid

    def _wait_task(self, task, args=None, kwargs=None):
        self.waiting_tasks.append((task, args or (), kwargs or {}))
        self.waiting[task.guid] = task
        return task.guid

    def _quit(self):
        self.scheduler_running = False
        for task in self.running.values():
            if task.running:
                print('killing pid {}'.format(task.pid))
                task.kill()
        return True

    @_task_or_die
    def _kill_task(self, task):
        task.kill()
        self._complete_task(task)
        return task.guid

    @_task_or_die
    def _complete_task(self, task):
        if task.guid in self.running:
            del self.running[task.guid]
        if task.guid not in self.completed:
            self.completed[task.guid] = task

    @_task_or_die
    def _get(self, task):
        return SerializedTask.deserialize(task.serialize())

    def _recv(self):
        try:
            return self.pipe.recv()
        except KeyboardInterrupt:
            print('ctrl-c received')
            self._quit()
            return None

    def get(self, guid):
        '''
        Returns the Task from the forked scheduler.

        :param Task|guid task_or_guid: a ``Task`` instance or string guid.
        :return: a ``Task`` object.
        '''
        self.pipe.send(Request(Command.get, guid=guid))
        return self._recv()

    def kill(self, guid):
        self.pipe.send(Request(Command.kill, guid=guid))
        return self._recv()

    def s(self, function):
        def _starter(*args, **kwargs):
            return self.schedule(function, args=args, kwargs=kwargs)
        return _starter

    def schedule(self, function, args=None, kwargs=None):
        self.pipe.send(
            Request(Command.start, function=function, args=args, kwargs=kwargs)
        )
        return self._recv()

    def quit(self, delete_results=True):
        if delete_results:
            shutil.rmtree(Scheduler.RESULT_DIR)
        self.pipe.send(Request(Command.quit))
        return self._recv()

    def run(self):
        # Create a pipe where the parent has the parent end, and the child end
        # gets passed to the child which sets up the pipe as that.
        self.pipe, child_end = Pipe()
        self.child = Process(target=self._run, args=(child_end,))
        self.child.start()
