# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

from functools import wraps

from tcell_agent.global_state import get_test_mode
from tcell_agent.tcell_logger import get_module_logger


def safe_wrap_function(description, func, *args, **kwargs):
    if get_test_mode():
        print("[tcell] >" + description + "<")
        return func(*args, **kwargs)
    try:
        return func(*args, **kwargs)
    except Exception as exception:
        import inspect
        calling_function = inspect.stack()[1]
        module_name = inspect.getmodule(calling_function[0]).__name__
        LOGGER = get_module_logger(module_name)
        LOGGER.error("{}: {}".format(description, exception))
        LOGGER.exception(exception)


def catches_generic_exception(module_name, message, return_value=None):
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exception:
                LOGGER = get_module_logger(module_name)
                LOGGER.error("{}: {}".format(message, exception))
                LOGGER.exception(exception)
                return return_value
        return decorated

    return decorator
