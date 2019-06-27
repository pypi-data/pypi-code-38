# coding=utf-8
from __future__ import absolute_import, print_function

import functools

from suanpan.objects import HasName


class Proxy(HasName):
    TYPE_KEY = "type"
    DEFAULT_TYPE = None
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
            if self.DEFAULT_TYPE is None:
                raise Exception("{} error: backend isn't set.".format(self.name))
            self.setDefaultBackend(self._args, self._kwargs)
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
        self._backend = self._setBackend(BackendClass, *_args, **_kwargs)
        return self

    def setDefaultBackend(self, *args, **kwargs):
        kwargs.update(self.TYPE_KEY, self.DEFAULT_TYPE)
        return self.setBackend(*args, **kwargs)

    def _setBackend(self, BackendClass, *args, **kwargs):
        return functools.partial(BackendClass, *args, **kwargs)
