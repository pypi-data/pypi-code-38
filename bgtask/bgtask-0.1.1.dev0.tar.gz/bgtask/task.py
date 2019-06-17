# coding=utf8

import signal
import json


def _sigalarmHandle(signum, frame):
    raise RuntimeError


class TaskTransfer(object):
    @classmethod
    def fromMethod(cls, task_name, arguments, keyword_arguments):
        data = {
            "func_name": task_name,
            "arguments": arguments,
            "keyword_arguments": keyword_arguments
        }
        return cls(data)

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return json.dumps(self.data)

    @classmethod
    def restore(cls, message):
        return cls(json.loads(message))

    @property
    def func_name(self):
        return self.data.get('func_name')

    @property
    def args(self):
        return self.data.get('arguments')

    @property
    def kwargs(self):
        return self.data.get('keyword_arguments')


class Task(object):
    def __init__(self, name, timeout, operation_function):
        self.name = name
        self.timeout = timeout
        self.operation = operation_function

    def run(self, tasktranfer):
        try:
            signal.signal(signal.SIGALRM, _sigalarmHandle)
            signal.alarm(self.timeout)
            self.operation(*tasktranfer.args, **tasktranfer.kwargs)
            signal.alarm(0)
            return
        except RuntimeError as e:
            raise e
