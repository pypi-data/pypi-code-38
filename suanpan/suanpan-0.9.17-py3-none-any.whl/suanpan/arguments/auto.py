# coding=utf-8
from __future__ import absolute_import, print_function

import functools

from suanpan.proxy import Proxy


class AutoArg(Proxy):
    TYPE_KEY = "argtype"
    DEFAULT_TYPE = "params"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault(self.TYPE_KEY, self.DEFAULT_TYPE)
        super(AutoArg, self).__init__(*args, **kwargs)

    @property
    def backend(self):
        if self._backend is None:
            self.setBackend(self._args, self._kwargs)
        if isinstance(self._backend, functools.partial):
            self._backend = self._backend()
        return self._backend

    def setBackend(self, *args, **kwargs):
        backendType = kwargs.get(self.TYPE_KEY)
        if not backendType:
            raise Exception("{} set error: backend type is required".format(self.name))
        BackendClass = self.MAPPING.get(backendType)
        if not BackendClass:
            raise Exception(
                "{} don't supported backend type: {}".format(self.name, backendType)
            )
        _args = [*self._args, *args]
        _kwargs = {**self._kwargs, **kwargs}
        _kwargs.pop(self.TYPE_KEY)
        self._backend = functools.partial(BackendClass, *_args, **_kwargs)
        return self
