#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base Classes for the beeswax wrapper
Components in this module should not be used but built upon
"""
from __future__ import unicode_literals

import sys
from abc import ABCMeta, abstractproperty

from beeswax_wrapper.core.exceptions import BeeswaxRESTException

try:
    from boltons.funcutils import wraps
except ImportError:
    from functools import wraps

from six import with_metaclass, reraise


class BeeswaxABCMeta(ABCMeta):

    def __new__(mcs, name, bases, attrs):
        """Wrap methods in BeeswaxRestException raising"""
        for attr, pos_func in attrs.items():

            if callable(pos_func) and attr in {'retrieve', 'create', 'list', 'update', 'delete'}:
                attrs[attr] = BeeswaxABCMeta.wrap_errors(pos_func)

        return super(BeeswaxABCMeta, mcs).__new__(mcs, name, bases, attrs)

    @staticmethod
    def wrap_errors(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                reraise(BeeswaxRESTException, BeeswaxRESTException(e), sys.exc_info()[2])
        return new_func


class BaseAPI(with_metaclass(BeeswaxABCMeta, object)):
    """Base API class for attribute API structures"""

    def __init__(self, dal):
        """
        :type dal: LabsDAL
        """
        self._dal = dal

    @abstractproperty
    def paths(self):
        pass

    def _call(self, method, **kwargs):
        """Call to the DAL"""
        return self._dal.call(method, self.paths, **kwargs)
