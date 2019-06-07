"""
.. module:: aio_task_bound_context
   :synopsis:
    Context manager that provides a means for context to be set, and retrieved
in Python AsyncIO.

.. moduleauthor:: Ricky Cook <pypi@auto.thatpanda.com>
"""

import asyncio as aio

from functools import lru_cache, wraps


def alru_cache(func):
    """ Basic AsyncIO version of ``lru_cache``

    :param func: function to wrap with cache
    """
    has_value = False
    value = None

    @wraps(func)
    async def inner(*args, **kwargs):
        if not has_value:
            value = await func(*args, **kwargs)
        return value

    return inner


def get_current_task():
    """ Get the current task """
    #try:
    #    return aio.current_task()
    #except AttributeError:
    #    # deprecated in python 3.7
    #    return aio.Task.current_task()
    return aio.Task.current_task()


class TaskBoundContext(object):
    """ Base class for a task-bound context """

    def get_value(self):
        """ Get the current value of the context """
        return self

    @classmethod
    def task_parent(cls, task):
        try:
            return task._ctx_parent
        except AttributeError:
            raise ValueError(
                'Missing task parent; Has set_task_factory been run?',
            )
    @classmethod
    def task_stacks(cls, task):
        try:
            return task._ctx_stacks
        except AttributeError:
            raise ValueError(
                'Missing task stack; Has set_task_factory been run?',
            )

    @classmethod
    def get_stack(cls):
        """ Gets the stack for ``cls`` on the current ``Task`` """
        current_task = task = get_current_task()
        stack = None
        while task is not None:
            task_ctx_stacks = cls.task_stacks(task)
            stack = task_ctx_stacks.get(cls, None)
            if stack is None or stack == []:
                task = cls.task_parent(task)
            else:
                if task != current_task:
                    stack = [stack[-1]]
                    cls.task_stacks(current_task)[cls] = stack
                break

        if stack is None:
            current_task._ctx_stacks[cls] = []

        return current_task._ctx_stacks[cls]
    @classmethod
    def get_stack_last(cls):
        stack = cls.get_stack()
        if len(stack) > 0:
            return stack[-1]
        else:
            return None

    @lru_cache()
    def _get_value_sync(self):
        if self.get_value.__code__.co_argcount == 1:
            return self.get_value()
        else:
            return self.get_value(self.get_stack_last())
    @alru_cache
    async def _get_value_async(self):
        if self.get_value.__code__.co_argcount == 1:
            fut = self.get_value()
        else:
            fut = self.get_value(self.get_stack_last())
        return await fut

    def __enter__(self):
        return self._do_enter(self._get_value_sync())
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._do_exit(self._get_value_sync())

    async def __aenter__(self):
        return self._do_enter(await self._get_value_async())
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._do_exit(await self._get_value_async())

    def _do_enter(self, value):
        self.get_stack().append(value)
        return value
    def _do_exit(self, value):
        popped = self.get_stack().pop()
        assert popped == value

    @classmethod
    def current(cls):
        try:
            return cls.get_stack()[-1]
        except IndexError:
            raise ValueError('No context')


def wrap_task(task):
    setattr(task, '_ctx_parent', get_current_task())
    setattr(task, '_ctx_stacks', {})
    return task


def create_task_factory(task_factory = None, loop = None):
    """ Create a task factory wrapper that adds parent/stack info to tasks

    :param task_factory: the task factory to wrap
    :param loop: loop to set the task factory for
    """
    if loop is None and task_factory is None:
        loop = aio.get_event_loop()
    if task_factory is None:
        task_factory = loop.get_task_factory()

    def inner(inner_loop, coro):
        if task_factory is None:
            task = aio.Task(coro, loop = inner_loop)
            return wrap_task(task)
        else:
            return wrap_task(task_factory(inner_loop, coro))

        return wrap_task(task)

    return inner

def set_task_factory(task_factory = None, loop = None):
    """ Setup a wrapped task factory necessary for tracking parent/context
    stack info

    :param task_factory: the task factory to wrap
    :param loop: loop to set the task factory for
    """
    if loop is None:
        loop = aio.get_event_loop()
    loop.set_task_factory(create_task_factory(
        task_factory = task_factory,
        loop = loop,
    ))
