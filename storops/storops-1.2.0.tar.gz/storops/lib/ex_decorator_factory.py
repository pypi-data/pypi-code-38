# coding=utf-8
# Copyright (c) 2015 EMC Corporation.
# All Rights Reserved.
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
from __future__ import unicode_literals

import logging

import six

__author__ = 'Cedric Zhuang'

log = logging.getLogger(__name__)


class MappedErrorCodeDecoratorFactory(object):
    def __init__(self, default_exception, exception_map=None):
        if exception_map is None:
            exception_map = {}
        self.exception_map = exception_map
        self.default = default_exception

    def clz_decorator(self):
        def decorator(clz):
            if not hasattr(clz, 'error_code'):
                raise AttributeError(
                    '"error_code" property is required on class {}.'.format(
                        clz.__name__))
            if not isinstance(clz.error_code, (list, tuple, set)):
                error_codes = [clz.error_code]
            else:
                error_codes = clz.error_code

            for error_code in error_codes:
                if error_code not in self.exception_map:
                    self.exception_map[error_code] = clz
            return clz

        return decorator

    def get_exception(self, error_code, default=None):
        if default is None:
            default = self.default
        ret = default
        if error_code is not None:
            if not isinstance(error_code, (list, tuple, set)):
                error_code = [error_code]
            for code in error_code:
                if code in self.exception_map:
                    ret = self.exception_map[code]
                    break
        return ret


class ExceptionListDecoratorFactory(object):
    def __init__(self, default_exception, exception_list=None):
        if exception_list is None:
            exception_list = []
        self.exception_list = exception_list
        self.default = default_exception

    def clz_decorator(self):
        def decorator(clz):
            self.exception_list.append(clz)
            return clz

        return decorator

    def get_exception(self, output, default=None):
        if default is not None:
            ret = default
        else:
            ret = self.default

        if output:
            for clz in self.exception_list:
                msg = clz.get_error_message()
                if isinstance(msg, (tuple, list, set)):
                    found = any(m in output for m in msg)
                elif isinstance(msg, six.string_types):
                    found = msg in output
                elif hasattr(msg, 'search'):
                    found = msg.search(output) is not None
                else:
                    raise ValueError('{} is not a valid message.'.format(msg))

                if found:
                    ret = clz
                    break
        return ret
