# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals


class InstrumentedMethod(object):
    def __init__(self, obj, func_name, target):
        self.obj = obj
        self.func_name = func_name
        self.target = target


class InstrumentationManager(object):
    _instrumented = {}

    @classmethod
    def instrument(cls, original_object, original_method_str, new_method):
        target_method = getattr(original_object, original_method_str)
        already_wrapped = hasattr(target_method, "__tcell_instrumentation__original_method__")
        if already_wrapped:
            return

        def wrapped_func(*args, **kwargs):
            return new_method(target_method, *args, **kwargs)

        wrapped_func.__tcell_instrumentation__original_method__ = target_method
        wrapped_func.__tcell_instrumentation__original_object__ = original_object
        wrapped_func.__tcell_instrumentation__original_method_str__ = original_method_str
        setattr(original_object, original_method_str, wrapped_func)
        return

    @classmethod
    def is_instrumented(cls, target_method):
        already_wrapped = hasattr(target_method, "__tcell_instrumentation__original_method__")
        return already_wrapped

    @classmethod
    def remove_instrumentation(cls, original_object, original_func_name, target_method):
        pass
