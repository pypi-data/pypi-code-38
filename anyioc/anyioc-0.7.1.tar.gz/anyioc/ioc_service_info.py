# -*- coding: utf-8 -*-
#
# Copyright (c) 2018~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from abc import abstractmethod, ABC
from enum import Enum
from inspect import signature, Parameter
from typing import Any
from threading import RLock

from .symbols import Symbols


class LifeTime(Enum):
    transient = 0
    scoped = 1
    singleton = 2


class IServiceInfo(ABC):
    __slots__ = ()

    @abstractmethod
    def get(self, provider) -> Any:
        raise NotImplementedError


class ServiceInfo(IServiceInfo):
    '''generic `IServiceInfo`.'''

    __slots__ = (
        '_key', '_lifetime', '_factory',
        # for not transient
        '_lock',
        # for singleton
        '_cache_value', '_service_provider'
    )

    def __init__(self, service_provider, key, factory, lifetime):

        sign = signature(factory)
        if not sign.parameters:
            self._factory = lambda _: factory()
        elif len(sign.parameters) == 1:
            arg_0 = list(sign.parameters.values())[0]
            if arg_0.kind != Parameter.POSITIONAL_OR_KEYWORD:
                raise TypeError('1st parameter of factory must be a positional parameter.')
            self._factory = factory
        else:
            raise TypeError('factory has too many parameters.')

        self._key = key
        self._lifetime = lifetime
        self._cache_value = None
        self._service_provider = service_provider

        if self._lifetime != LifeTime.transient:
            self._lock = RLock()
        else:
            self._lock = None

        if self._lifetime == LifeTime.singleton:
            # service_provider is required when lifetime == singleton
            assert self._service_provider is not None

    def get(self, provider):
        if self._lifetime is LifeTime.transient:
            return self._factory(provider)

        if self._lifetime is LifeTime.scoped:
            return self._from_scoped(provider)

        if self._lifetime is LifeTime.singleton:
            return self._from_singleton()

        raise NotImplementedError(f'what is {self._lifetime}?')

    def _from_scoped(self, provider):
        cache: dict = provider[Symbols.cache]
        try:
            return cache[self]
        except KeyError:
            pass
        with self._lock:
            try:
                return cache[self]
            except KeyError:
                value = self._factory(provider)
                cache[self] = value
                return value

    def _from_singleton(self):
        if self._cache_value is None:
            with self._lock:
                if self._cache_value is None:
                    self._cache_value = (self._factory(self._service_provider), )
        return self._cache_value[0]


class ProviderServiceInfo(IServiceInfo):
    '''a `IServiceInfo` use for get current `ServiceProvider`.'''

    __slots__ = ()

    def get(self, provider):
        return provider


class ValueServiceInfo(IServiceInfo):
    '''a `IServiceInfo` use for get fixed value.'''

    __slots__ = ('_value')

    def __init__(self, value):
        self._value = value

    def get(self, provider):
        return self._value


class GroupedServiceInfo(IServiceInfo):
    '''a `IServiceInfo` use for get multi values as a tuple from keys list.'''

    __slots__ = ('_keys')

    def __init__(self, keys: list):
        self._keys = keys

    def get(self, provider):
        return tuple(provider[k] for k in self._keys)


class BindedServiceInfo(IServiceInfo):
    '''a `IServiceInfo` use for get value from target key.'''

    __slots__ = ('_target_key')

    def __init__(self, target_key):
        self._target_key = target_key

    def get(self, provider):
        return provider[self._target_key]
