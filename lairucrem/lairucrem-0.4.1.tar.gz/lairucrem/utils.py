#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""Utilities."""

import asyncio
import functools
import sys
from asyncio import BaseEventLoop, Handle, Task
from typing import Callable, List, Sequence, Text, Tuple, Type

from . import config


class ParseError(ValueError):
    """Raises when the parsing of a command output fails."""


def monkeypatch(cls: Type, methodname: Text=None):
    """Patch the given class with decorated method."""

    def decorator(func: Callable):
        """Decorated"""
        name = methodname or func.__name__
        functools.wraps(getattr(cls, name, None))(func, assigned=())
        setattr(cls, name, func)
        return func
    return decorator


class ensure_one:

    def __init__(self, obj: Callable, *args, **kwargs):
        assert callable(obj), obj
        self.task = None
        self.handle = None
        self.obj = obj
        super().__init__(*args, **kwargs)

    def delay(self, *args,
              duration: float=0.3, loop: BaseEventLoop=None) -> Handle:
        """Delay task from corofunc `obj` and cancal previous delayed one."""
        self.cancel()
        loop = loop or asyncio.get_event_loop()
        if asyncio.iscoroutinefunction(self.obj):
            self.handle = loop.call_later(duration, self.ensure, *args)
        else:
            self.handle = loop.call_later(duration, self.obj, *args)
        return self.handle

    def ensure(self, *args, loop: BaseEventLoop=None) -> Task:
        """Ensure future task from corofunc `obj` and cancel previous task."""
        assert asyncio.iscoroutinefunction(self.obj), \
            f'not a coroutine function: {self.obj}'

        self.cancel()

        if config.DEBUG:

            async def runner():
                async with popup_error(
                        Exception, ignores=(asyncio.CancelledError,)):
                    await self.obj(*args)

            self.task = asyncio.ensure_future(runner(), loop=loop)
        else:
            self.task = asyncio.ensure_future(self.obj(*args), loop=loop)
        return self.task

    def __call__(self, *args, **kwargs):
        """Call the original object."""
        self.cancel()
        return self.obj(*args, **kwargs)

    def cancel(self):
        """Cancel the task generated from this coroutine function."""
        if self.handle:
            self.handle.cancel()
        if self.task and not self.task.done():
            self.task.cancel()


def parse_colored_line(
        line: Text,
        default_style: Text='',
        skip_empty=False) -> List[Tuple[Text, Text]]:
    """Parse line given by hg with color markers into urwid markers."""
    if not line:
        return [] if skip_empty else [(default_style, '')]
    match = config.COLOR_REGEXP.search(line)
    if not match:
        return [(default_style, line)]
    start, end = match.start(), match.end()
    if start:
        out = [(default_style, line[:start])]
    else:
        out = []
    style, content = match.groups()
    style = style.strip()
    # put back trailling ']' for nested colors
    content += line[match.regs[-1][-1]: end-1]
    # considere nested color syles or applys parent style if none note: we are
    # insite a line, so we can skip emtpy empty content because it's not a
    # empty line.
    _inner = parse_colored_line(content, style, skip_empty=True)
    out += ((_style, _content) for _style, _content in _inner if _content)
    return out + parse_colored_line(line[end:], default_style, skip_empty=True)


class popup_error:
    """Contextmanager that popup raised exception."""

    def __init__(self,
                 *exctypes: Tuple[Type],
                 donotraise=False,
                 ignores: Sequence[Type]=()):
        self.exctypes = exctypes
        self.ignores = ignores
        self.donotraise = donotraise

    async def display_exception(
            self,
            exctype: Type,
            excobj: BaseException,
            traceback):
        """Display the given exception into a pupop."""
        from .widgets.dialog import simple
        from urwid import Text
        msg = excobj.strerror if isinstance(excobj, OSError) else str(excobj)
        diag = simple(Text(parse_colored_line(msg)),
                      title=exctype.__name__,
                      min_height=msg.count('\n') + 5)
        if traceback:
            diag.append_button('traceback', 'traceback', key='?')
        res = await diag
        if res is 'traceback':
            await self.display_traceback(exctype, traceback)

    async def display_traceback(self, exctype: Type, traceback):
        """Display the given traceback into a pupop."""
        from .widgets.dialog import simple
        from traceback import format_tb
        tb = format_tb(traceback)
        await simple(
            ''.join(tb), title=exctype.__name__, min_height=len(tb))

    async def __aenter__(self):
        return self

    async def __aexit__(self, exctype, exc, tb):
        if exctype is None:
            return
        if exc is None:
            exc = exctype()
        if not isinstance(exc, self.exctypes) or isinstance(exc, self.ignores):
            return
        await self.display_exception(exctype, exc, tb)
        return self.donotraise


def apply_mixin(obj, mixin: Type):
    """Apply the given mixin to the given object."""
    if isinstance(obj, mixin):
        return
    # python requires that names are uniq in mro
    name = obj.__class__.__name__ + '_' + mixin.__name__
    newcls = type(name, (mixin, obj.__class__), {})
    obj.__class__ = newcls


class nodestr(str):
    """A string representing a changeset node."""
    pass


class shelvestr(str):
    """A string representing a shelve name."""
    pass


class _AsyncContextManager:
    """A synchronuous context manager consuming the given async generator.

    Should be instanciated from `async_contextmanager`.
    """

    def __init__(self, agen):
        self._agen = agen

    async def __aenter__(self):
        # from contextlib.contextmanager
        try:
            return await self._agen.asend(None)
        except StopAsyncIteration:
            raise RuntimeError("generator didn't yield") from None

    async def __aexit__(self, type, value, traceback):  # noqa: C901
        # from contextlib.contextmanager
        if type is None:
            try:
                await self._agen.asend(None)
            except StopAsyncIteration:
                return
            else:
                raise RuntimeError("generator didn't stop")
        else:
            if value is None:
                # Need to force instantiation so we can reliably
                # tell if we get the same exception back
                value = type()
            try:
                return await self._agen.athrow(type, value, traceback)
                raise RuntimeError("generator didn't stop after throw()")
            except StopAsyncIteration as exc:
                # Suppress StopIteration *unless* it's the same exception that
                # was passed to throw().  This prevents a StopIteration
                # raised inside the "with" statement from being suppressed.
                return exc is not value
            except RuntimeError as exc:
                # Don't re-raise the passed in exception. (issue27112)
                if exc is value:
                    return False
                # Likewise, avoid suppressing if a StopIteration exception
                # was passed to throw() and later wrapped into a RuntimeError
                # (see PEP 479).
                if exc.__cause__ is value:
                    return False
                raise
            except:  # noqa: E701
                # only re-raise if it's *not* the exception that was
                # passed to throw(), because __exit__() must not raise
                # an exception unless __exit__() itself failed.  But throw()
                # has to raise the exception to signal propagation, so this
                # fixes the impedance mismatch between the throw() protocol
                # and the __exit__() protocol.
                #
                if sys.exc_info()[1] is not value:
                    raise


def async_contextmanager(func: Callable):
    """Asynchronuous context manager.

    Attention: it will not warn if the async generator has more than
    one `yield`.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return _AsyncContextManager(func(*args, **kwargs))
    return wrapper


class slicer:
    """Partial view of a list.

    IMPORTANT: the full list API is not available yet.
    """

    def __init__(self, reference: Sequence, start: int=None, stop: int=None):
        self.__ref__ = reference
        self._slice = slice(start, stop)

    @property
    def _indices(self):
        return self._slice.indices(len(self.__ref__))

    def __len__(self):
        _start, _stop, _step = self._indices
        return _stop - _start

    def __iter__(self):
        for value in self.__ref__.__getitem__(self._slice):
            yield value

    def __getitem__(self, index: int):
        _start, _stop, _step = self._indices
        if isinstance(index, slice):
            start, stop, step = index.indices(_stop - _start)
            start = min(start + _start, _stop)
            stop = min(stop + _start, _stop)
            return self.__ref__[start:stop:step]
        else:
            index = (_start if index >= 0 else _stop) + index
            if index < _start or index >= _stop:
                raise IndexError(
                    f'index out of range [{_start}:{_stop}]: {index}')
            return self.__ref__[index]

    def append(self, value):
        _start, _stop, _step = self._indices
        self.__ref__.insert(_stop, value)

    def extend(self, values):
        _start, _stop, _step = self._indices
        self.__ref__[_stop:_stop] = values
