# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.proxy import Proxy


class AutoArg(Proxy):
    TYPE_KEY = "argtype"
    DEFAULT_TYPE = "params"

    def _setBackend(self, BackendClass, *args, **kwargs):
        kwargs.pop(self.TYPE_KEY)
        return super(AutoArg, self)._setBackend(BackendClass, *args, **kwargs)
