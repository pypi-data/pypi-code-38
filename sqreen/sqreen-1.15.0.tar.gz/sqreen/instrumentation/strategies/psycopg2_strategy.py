# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Custom strategy for psycopg2 oddities
"""
import logging

from .dbapi2 import CustomConnection, CustomCursor
from .import_hook import ImportHookStrategy

LOGGER = logging.getLogger(__name__)


def wrap_custom_register_type(original):
    def custom_register_type(obj, scope=None):
        if isinstance(scope, (CustomConnection, CustomCursor)):
            scope = scope._obj

        return original(obj, scope)

    return custom_register_type


class Psycopg2Strategy(ImportHookStrategy):
    """ Simple strategy that replace psycopg2.*.register_type to works with our
    Proxy objects.
    """

    def import_hook_callback(self, original):
        """ Monkey-patch the object located at psycopg2.*.register_type to
        monkey-patch the register_type function
        """
        return wrap_custom_register_type(original)
