#!/usr/bin/env python

"""Implementation of with block context managers that allow clearly defined skipping of the controlled block ala PEP 377

PEP 377 (rejected) proposed making this a standard language feature, and was rejected primarily because it alters the logical control flow of the with block.
This implementation uses the fact that variable assignments in the with ... as ...: syntax are considered part of the with block
Exceptions raised in these assignments are passed to the __exit__ function of the context manager, and can be used to skip the block.
"""

import threading
import contextlib
from functools import wraps
import sys
import warnings
from . import Singleton
from six import with_metaclass

class SkipStatement(Exception):
    """Exception which when raised by a conditional context manager function will cause the controlled statement to be skipped"""

class StatementNotSkippedType(with_metaclass(Singleton.Singleton)):
    """A singleton object indicating that a context manager for a with clause has not directed the controlled statement to be skipped"""
    name = "StatementNotSkipped"

class StatementSkippedType(with_metaclass(Singleton.Singleton)):
    """A singleton object indicating that a context manager for a with clause has directed the controlled statement to be skipped - also contains the .detector attribute"""
    name = "StatementSkipped"
    def __setattr__(self, attr, value):
        """Only the detector attribute may be set on StatementSkipped"""
        if attr != "detector":
            raise AttributeError("%r object has no attribute %r" % (type(self), attr))
        object.__setattr__(self, attr, value)

    @property
    def detector(self):
        """Attribute which when set triggers the skipping of controlled statements by conditional context managers"""
        raise AttributeError("%r.detector is a write-only attribute" % type(self))

    @detector.setter
    def detector(self, value):
        """Sets the detector attribute, triggering a SkipStatement exception if the value is StatementSkipped"""
        if isinstance(value, tuple) and len(value) == 2 and value[1] in (StatementSkipped, StatementNotSkipped):
            value = value[1]
        if value is StatementSkipped:
            raise SkipStatement()
        elif value is not StatementNotSkipped:
            warnings.warn("%s.detector received an unexpected skip indicator" % self.name, SkipWarning, stacklevel=3)

StatementSkipped = StatementSkippedType()
StatementNotSkipped = StatementNotSkippedType()

del StatementSkippedType
del StatementNotSkippedType

class SkipWarning(Warning):
    """Warning related to with context managers with conditional block skipping"""

class ConditionalContextManager(object):
    """Helper for @conditionalcontextmanager decorator."""
    def __init__(self, gen):
        self.gen = gen

    def __enter__(self):
        try:
            return next(self.gen), StatementNotSkipped
        except SkipStatement as e:
            # set flag
            return StatementSkipped, StatementSkipped
        except StopIteration as e:
            raise RuntimeError("generator didn't yield or raise SkipStatement")

    def __exit__(self, type, value, traceback):
        if type is None:
            try:
                next(self.gen)
            except StopIteration:
                return
            else:
                raise RuntimeError("generator didn't stop")
        else:
            if value is None:
                # Need to force instantiation so we can reliably
                # tell if we get the same exception back
                value = type()
            if isinstance(value, SkipStatement):
                return True
            try:
                self.gen.throw(type, value, traceback)
                raise RuntimeError("generator didn't stop after throw()")
            except StopIteration as exc:
                # Suppress the exception *unless* it's the same exception that
                # was passed to throw().  This prevents a StopIteration
                # raised inside the "with" statement from being suppressed
                return exc is not value
            except:
                # only re-raise if it's *not* the exception that was
                # passed to throw(), because __exit__() must not raise
                # an exception unless __exit__() itself failed.  But throw()
                # has to raise the exception to signal propagation, so this
                # fixes the impedance mismatch between the throw() protocol
                # and the __exit__() protocol.
                #
                if sys.exc_info()[1] is not value:
                    raise


def conditionalcontextmanager(func):
    """@conditionalcontextmanager decorator.

    Typical usage:

        @conditionalcontextmanager
        def some_generator(<arguments>):
            <setup>
            try:
                if <condition>:
                    yield <value>
                else:
                    raise SkipStatement()
            finally:
                <cleanup>

    This makes this:

        with some_generator(<arguments>) as (<variable>, StatementSkipped.detector):
            <body>

    equivalent to this:

        <setup>
        try:
            if <condition>:
                <variable> = <value>
                <body>
        finally:
            <cleanup>

    """
    @wraps(func)
    def helper(*args, **kwds):
        return ConditionalContextManager(func(*args, **kwds))
    return helper

