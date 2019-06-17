# encoding: utf-8

import inspect
import uuid
import json
import logging
import pickle
from traceback import format_exc

from django.conf import settings

from .lib import Queue

logger = logging.getLogger("tools")


identify = {"queue": "async.task"}
_container = {}


def listener(data):
    """
    异步任务的回调函数
    其中参数经过pickle.loads
    """
    callback = _container[data["callback"]]
    args = data.get("args", [])
    kwargs = data.get("kwargs", {})
    try:
        callback(*args, **kwargs)
    except Exception:
        logger.error(format_exc())


listen = Queue(identify, logger=logger)(listener)


def register(task):
    """
    注册异步任务的装饰器
    直接调用回调函数时会发送消息到队列aurora.async.task
    跟正常调用方法无区别
    其中会把函数的参数用pickle.dumps， 然后发送消息

    使用方法

    @register
    def mycallback(model, queryset):
        pass

    mycallback(model, queryset)
    """
    _container[task.__name__] = task

    def inner(*args, **kwargs):
        taskId = uuid.uuid4().hex
        if 'taskId' in inspect.getargspec(task).args:
            kwargs.update(taskId=taskId)
        with Queue(identify, logger=logger) as queue:
            message = {"callback": task.__name__, "args": args, "kwargs": kwargs}
            queue.publish(message, encoder="pickle")
        return taskId

    return inner
