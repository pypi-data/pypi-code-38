# -*- coding: utf-8 -*-
from j5basic import Errors
import six

def test_traceback_str():
    traceback_str = None
    try:
        raise NotImplementedError()
    except NotImplementedError:
        traceback_str = Errors.traceback_str()
    assert traceback_str is not None

def test_exception_str():
    exception_str = None
    try:
        raise RuntimeError("Testing error")
    except RuntimeError:
        exception_str = Errors.exception_str()
    assert exception_str is not None

def test_unicode_errors():
    value_str = None
    try:
        raise ValueError("Pure ascii")
    except ValueError as e:
        value_str = Errors.error_to_str(e)
    assert value_str is not None

    value_str = None
    try:
        raise ValueError(six.u("前回修正"))
    except ValueError as e:
        value_str = Errors.error_to_str(e)
    assert value_str is not None

    value_str = None
    try:
        raise ValueError(six.u("前回修正").encode('shift-jis'))
    except ValueError as e:
        value_str = Errors.error_to_str(e)
    assert value_str is not None
