# coding=utf8

import threading
import redis
from bgtask.task import TaskTransfer


class SingletonMixin(object):
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()

        return cls.__singleton_instance


class RedisConnection(SingletonMixin):
    def __init__(self):
        self.redis = None
        self.host = None
        self.port = None
        self.queue_name = None
        self.connected = False

    def init_redis(self, host, port, queue_name):
        self.host = host
        self.port = port
        self.queue_name = queue_name

    def reconnect(self):
        if not self.connected:
            self.redis = redis.StrictRedis(host=self.host, port=self.port)
            self.connected = True

    def waitfor(self):
        self.reconnect()
        return self.redis.blpop(self.queue_name)

    def push_queue(self, value):
        self.reconnect()
        self.redis.rpush(self.queue_name, value)


class Configuration(SingletonMixin):
    def __init__(self):
        self.host = ''
        self.port = 0
        self.queue_name = ''
        self.worker_count = 2

    def config(self, host, port, _alive, queue_key, worker_count):
        self.host = host
        self.port = port
        self.queue_name = queue_key
        self.worker_count = worker_count


class TaskHolder(SingletonMixin):
    def __init__(self):
        self.tasks = {}

    def regist_task(self, _task):
        self.tasks[_task.name] =_task

    def getTask(self, task_name):
        return self.tasks.get(task_name, None)


class TaskInvoker(object):
    def __init__(self, f):
        self.function = f
        self.task_name = f.func_name

    def __call__(self, *args, **kwargs):
        self.function(*args, **kwargs)

    def _validate_args(self, *args, **kwargs):
        func_defaults = self.function.__defaults__
        raw_count = self.function.func_code.co_argcount
        args_count = raw_count - len(func_defaults or '')
        if len(args) != args_count:
            raise TypeError('%s() takes at least %s arguments (%s given)' % (self.task_name, args_count, len(args)))

    def delay(self, *args, **kwargs):
        self._validate_args(*args, **kwargs)
        transfer = TaskTransfer.fromMethod(self.task_name, args, kwargs)
        conn = RedisConnection.instance()
        data = str(transfer)
        conn.push_queue(data)


def task(timeout=5):
    def decorator(f):
        from bgtask.task import Task
        TaskHolder.instance().regist_task(Task(f.func_name, timeout, f))
        taskInvoker = TaskInvoker(f)
        return taskInvoker
    return decorator


def update_config(configration):
    Configuration.instance().config(configration.get('REDIS_HOST'),
                                    configration.get('REDIS_PORT'),
                                    configration.get('REDIS_ALIVE', 300),
                                    configration.get('TASK_QUEUE_KEY'),
                                    configration.get('TASK_WORKER'),
                                    )


def Server():
    from server import Server as BgSerber
    return BgSerber()
