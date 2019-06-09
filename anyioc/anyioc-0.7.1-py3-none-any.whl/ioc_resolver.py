# -*- coding: utf-8 -*-
#
# Copyright (c) 2018~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from abc import abstractmethod
import typing
from typing import List
from threading import RLock
from contextlib import nullcontext

from .err import ServiceNotFoundError
from .ioc_service_info import ValueServiceInfo, ServiceInfo, LifeTime, IServiceInfo, GroupedServiceInfo

class IServiceInfoResolver:
    '''
    the base class for dynamic resolve `IServiceInfo`.
    '''

    def get(self, provider, key) -> IServiceInfo:
        '''
        get the `IServiceInfo` from resolver.
        '''
        raise ServiceNotFoundError(key)

    def __add__(self, other):
        new_resolver = ServiceInfoChainResolver()
        new_resolver.chain.append(self)
        new_resolver.append(other)
        return new_resolver

    def cache(self, *, sync=False):
        '''
        return a `IServiceInfoResolver` to cache all values from current `IServiceInfoResolver`.
        that mean all values will not dynamic update after first resolved.
        '''
        return CacheServiceInfoResolver(self, sync=sync)


class ServiceInfoChainResolver(IServiceInfoResolver):
    '''
    a helper resolver for resolve values from each `IServiceInfoResolver`
    '''

    def __init__(self, *resolvers):
        self.chain: List[IServiceInfoResolver] = list(resolvers)

    def get(self, provider, key):
        for resolver in self.chain:
            try:
                return resolver.get(provider, key)
            except ServiceNotFoundError:
                pass
        return super().get(provider, key)

    def append(self, other):
        if isinstance(other, ServiceInfoChainResolver):
            self.chain.extend(other.chain)
        else:
            self.chain.append(other)

    def __add__(self, other):
        new_resolver = ServiceInfoChainResolver()
        new_resolver.chain.extend(self.chain)
        new_resolver.append(other)
        return new_resolver


class CacheServiceInfoResolver(IServiceInfoResolver):
    '''
    a helper resolver for cache values from other `IServiceInfoResolver`

    NOTE:
    if a `IServiceInfo` is affect by `provider`, you should not cache it.
    `CacheServiceInfoResolver` only cache by the `key` and ignore the `provider` arguments.
    '''

    def __init__(self, base_resolver: IServiceInfoResolver, *, sync=False):
        super().__init__()
        self._base_resolver = base_resolver
        self._cache = {}
        self._lock = RLock() if sync else nullcontext()

    def get(self, provider, key):
        try:
            return self._cache[key]
        except KeyError:
            pass
        with self._lock:
            try:
                return self._cache[key]
            except KeyError:
                pass
            service_info = self._base_resolver.get(provider, key)
            self._cache[key] = service_info
            return service_info

    def cache(self):
        return self


class ImportServiceInfoResolver(IServiceInfoResolver):
    '''
    dynamic resolve `IServiceInfo` if the key is a package name.
    '''

    def get(self, provider, key):
        import importlib
        if isinstance(key, str):
            try:
                module = importlib.import_module(key)
                return ValueServiceInfo(module)
            except TypeError:
                pass
            except ModuleNotFoundError:
                pass
        return super().get(provider, key)


class SimpleServiceInfo(IServiceInfo):
    __slots__ = ('_factory')

    def __init__(self, factory):
        self._factory = factory

    def get(self, provider):
        return self._factory(provider)


class TypesServiceInfoResolver(IServiceInfoResolver):
    '''
    dynamic resolve `IServiceInfo` if the key is a type instance.
    '''

    inject_by = None

    def get(self, provider, key):
        if isinstance(key, type):
            factory = self.inject_by(key) if self.inject_by else key
            return SimpleServiceInfo(factory)
        return super().get(provider, key)


class TypeNameServiceInfoResolver(IServiceInfoResolver):
    '''
    dynamic resolve `IServiceInfo` if the key is a type name or qualname.
    '''

    inject_by = None

    def _get_type(self, key):
        if isinstance(key, str):
            for klass in object.__subclasses__():
                if getattr(klass, '__name__', None) == key:
                    return klass
                if getattr(klass, '__qualname__', None) == key:
                    return klass
        # None

    def get(self, provider, key):
        klass = self._get_type(str)
        if klass is not None:
            factory = self.inject_by(klass) if self.inject_by else klass
            return SimpleServiceInfo(factory)
        return super().get(provider, key)


class TypingServiceInfoResolver(IServiceInfoResolver):
    '''
    dynamic resolve `IServiceInfo` if the key is a generic type make from typing.

    to use this, you need to install `type_info` module from pypi.
    '''

    def get(self, provider, key):
        from type_info import get_type_info

        try:
            type_info = get_type_info(key)
        except TypeError:
            type_info = None

        if type_info and type_info.is_generic:
            factory = None

            if type_info.generic_type is typing.Tuple:
                if all(not a.is_generic and not a.is_typevar for a in type_info.generic_args):
                    keys = [t.target_type for t in type_info.generic_args]
                    def factory(ioc):
                        return type_info.std_type(provider[k] for k in keys)

            if factory is not None:
                return SimpleServiceInfo(factory)

        return super().get(provider, key)