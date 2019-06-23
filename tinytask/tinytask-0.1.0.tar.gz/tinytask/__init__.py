'''
tinytask

A tiny task framework using forked processes without a message broker.
'''

__title__ = 'tinytask'
__version__ = '0.1.0'
__all__ = (
    'Task',
    'TaskStatus',
    'Scheduler',
    'Request',
    'Response',
    'ResponseType',
    'Result',
    'ResultType',
    'TinyTaskError',
    'TaskNotDoneError',
    'TaskClearedError',
    'TaskStartedError',
    'TaskResultsMissingError',
    'TaskNotFoundError',
)
__author__ = 'Johan Nestaas <johannestaas@gmail.com>'
__license__ = 'GPLv3'
__copyright__ = 'Copyright 2019 Johan Nestaas'

from .scheduler import (
    Task, TaskStatus, Scheduler, Request, Response, ResponseType, Result,
    ResultType,
)
from .exceptions import (
    TinyTaskError, TaskNotDoneError, TaskClearedError, TaskStartedError,
    TaskResultsMissingError, TaskNotFoundError,
)
