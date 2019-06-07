# Copyright 2018 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import functools
import inspect
import unittest

import testtools

from tobiko.common import _fixture


SkipException = testtools.TestCase.skipException


def skip(reason, *args, **kwargs):
    if args or kwargs:
        reason = reason.format(*args, **kwargs)
    raise SkipException(reason)


def skip_if(reason, predicate, *args, **kwargs):
    return skip_if_match(reason, bool, predicate, *args, **kwargs)


def skip_until(reason, predicate, *args, **kwargs):
    return skip_if_match(reason, lambda x: bool(not x), predicate, *args,
                         **kwargs)


def skip_if_match(reason, match, predicate, *args, **kwargs):

    def decorator(obj):
        method = _get_decorated_method(obj)

        @functools.wraps(method)
        def wrapped_method(*_args, **_kwargs):
            return_value = predicate(*args, **kwargs)
            if match(return_value):
                skip(reason, return_value=return_value)
            return method(*_args, **_kwargs)

        if obj is method:
            return wrapped_method
        else:
            setattr(obj, method.__name__, wrapped_method)
            return obj

    return decorator


def _get_decorated_method(obj):
    if inspect.isclass(obj):
        if issubclass(obj, (unittest.TestCase, testtools.TestCase)):
            return obj.setUp
        elif _fixture.is_fixture(obj):
            return obj.setUp
        else:
            raise TypeError("Cannot decorate class {!r}".format(obj))
    else:
        if callable(obj):
            return obj
        else:
            raise TypeError("Cannot decorate object {!r}".format(obj))
