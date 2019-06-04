#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django.core.exceptions import PermissionDenied
from functools import wraps


class cls_decorator():
    def __init__(self, cls_name=None):
        self.cls_name = cls_name

    def __call__(self, func):
        @wraps(func)
        def _func(request, *args, **kwargs):
            return func(request, *args, **kwargs)
        return _func


def func_decorator(func_name):
    def dec(func):
        def _dec(request, *args, **kwargs):
            return func(request, *args, **kwargs)

        _dec.__doc__ = func.__doc__
        _dec.__name__ = func.__name__
        return _dec

    return dec
