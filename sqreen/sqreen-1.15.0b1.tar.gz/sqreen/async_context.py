# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Provide task-contextual storage for asyncio.

In order to inherit contexts when a sub-task is spawned (e.g. when calling
asyncio.gather), it is required to set up a custom task factory in the event
loop. This task factory will attach a shallow copy of the current context to
every new task.
"""

import asyncio
from functools import wraps
from logging import getLogger

LOGGER = getLogger(__name__)


_TASK_CONTEXT_ATTR = "_sqreen_context"


def with_current_task_context(func):
    """Call the decorated function with the current task context.

    The task context is passed as an additional first argument. If no task is
    running or the context was not set, the function is not called and an error
    message is issued.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        task = asyncio.Task.current_task()
        if task is None:
            # TODO This log message is displayed at startup because we set a
            # request_recorder at initialization, before the event loop is
            # started. Let's dismiss it for now.
            LOGGER.info("No current task, is the event loop running?")
            return
        context = getattr(task, _TASK_CONTEXT_ATTR, None)
        if context is None:
            LOGGER.error(
                "No context attached to the current task, "
                "is the task factory correctly set?"
            )
            return
        return func(context, *args, **kwargs)

    return wrapper


@with_current_task_context
def get(context, key, default=None):
    """Retrieve the value associated to a key in the current task context.

    Fallback to default if the key is missing.
    """
    return context.get(key, default)


@with_current_task_context
def set(context, key, value):
    """Map a key to a value in the current task context.

    If the key is already set, the value is overwritten.
    """
    context[key] = value


@with_current_task_context
def setdefault(context, key, value):
    """If a key is not set in the current task context, map it to a value.

    If the key is already set, its associated value is unchanged.
    """
    context.setdefault(key, value)


@with_current_task_context
def delete(context, key):
    """Delete a key from the current task context."""
    return context.pop(key, None)


def _default_task_factory(loop, coro):
    """Default function to create a new task."""
    return asyncio.tasks.Task(coro, loop=loop)


def create_task_factory(task_factory=None):
    """Wrap a task factory to support task context inheritance.

    When a new task is spawned, it receives a shallow copy of the parent task
    context. This allows to modify the context of the child task without
    altering the parent one.
    """

    if task_factory is None:
        task_factory = _default_task_factory

    def wrapped(loop, coro):
        parent_task = asyncio.Task.current_task(loop=loop)
        child_task = task_factory(loop, coro)
        if child_task._source_traceback:
            del child_task._source_traceback[-1]
        context = getattr(parent_task, _TASK_CONTEXT_ATTR, {})
        setattr(child_task, _TASK_CONTEXT_ATTR, dict(context))
        return child_task

    return wrapped


task_factory = create_task_factory()
