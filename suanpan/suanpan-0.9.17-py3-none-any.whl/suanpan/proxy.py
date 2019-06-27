# coding=utf-8
from __future__ import absolute_import, print_function

import functools

from suanpan.objects import HasName


class Proxy(HasName):
    TYPE_KEY = "type"
    MAPPING = {}

    def __init__(self, *args, **kwargs):
        super(Proxy, self).__init__()
        self._backend = None
        self._args = args
        self._kwargs = kwargs

    def __getattr__(self, key):
        return getattr(self.backend, key)

    @property
    def backend(self):
        if self._backend is None:
            raise Exception("{} error: backend isn't set.".format(self.name))
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
        self._backend = functools.partial(BackendClass, *_args, **_kwargs)
        return self
