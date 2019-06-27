"""
Convenience decorators for use in fabfiles.
"""
from __future__ import with_statement

#from Crypto import Random

#from fabric import tasks
from fabric.api import runs_once as _runs_once

#from .context_managers import settings
from burlap.tasks import WrappedCallableTask

def task_or_dryrun(*args, **kwargs):
    """
    Decorator declaring the wrapped function to be a new-style task.

    May be invoked as a simple, argument-less decorator (i.e. ``@task``) or
    with arguments customizing its behavior (e.g. ``@task(alias='myalias')``).

    Please see the :ref:`new-style task <task-decorator>` documentation for
    details on how to use this decorator.

    .. versionchanged:: 1.2
        Added the ``alias``, ``aliases``, ``task_class`` and ``default``
        keyword arguments. See :ref:`task-decorator-arguments` for details.
    .. versionchanged:: 1.5
        Added the ``name`` keyword argument.

    .. seealso:: `~fabric.docs.unwrap_tasks`, `~fabric.tasks.WrappedCallableTask`
    """
    invoked = bool(not args or kwargs)
    task_class = kwargs.pop("task_class", WrappedCallableTask)
#     if invoked:
#         func, args = args[0], ()
#     else:
    func, args = args[0], ()

    def wrapper(func):
        return task_class(func, *args, **kwargs)
    wrapper.is_task_or_dryrun = True
    wrapper.wrapped = func

    return wrapper if invoked else wrapper(func)

_METHOD_ATTRIBUTES = ['deploy_before', 'is_post_callback']

def _task(meth):
    meth.is_task = True

    def wrapper(self, *args, **kwargs):
        ret = meth(self, *args, **kwargs)

        # Ensure each satchels local variable scope is cleared after every server execution.
        self.clear_local_renderer()

        return ret

    if hasattr(meth, 'is_deployer') or meth.__name__ == 'configure':
        # Copy the wrapped method's attributes to the wrapper.
        wrapper.__name__ = meth.__name__
        for attr in _METHOD_ATTRIBUTES:
            if hasattr(meth, attr):
                setattr(wrapper, attr, getattr(meth, attr))
        return wrapper
    return meth

def task(*args, **kwargs):
    """
    Decorator for registering a satchel method as a Fabric task.

    Can be used like:

        @task
        def my_method(self):
            ...

        @task(precursors=['other_satchel'])
        def my_method(self):
            ...

    """
    precursors = kwargs.pop('precursors', None)
    post_callback = kwargs.pop('post_callback', False)
    if args and callable(args[0]):
        # direct decoration, @task
        return _task(*args)

    # callable decoration, @task(precursors=['satchel'])
    def wrapper(meth):
        if precursors:
            meth.deploy_before = list(precursors)
        if post_callback:
            #from burlap.common import post_callbacks
            #post_callbacks.append(meth)
            meth.is_post_callback = True
        return _task(meth)
    return wrapper

def runs_once(meth):
    """
    A wrapper around Fabric's runs_once() to support our dryrun feature.
    """
    from burlap.common import get_dryrun, runs_once_methods
    if get_dryrun():
        pass
    else:
        runs_once_methods.append(meth)
        _runs_once(meth)
    return meth
