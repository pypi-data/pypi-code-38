# -*- coding: utf-8 -*-
#
# Copyright (c) 2018~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from abc import abstractmethod
from typing import Any
from collections import ChainMap
from contextlib import ExitStack

from .err import ServiceNotFoundError
from .symbols import Symbols
from .ioc_resolver import IServiceInfoResolver, ServiceInfoChainResolver
from .ioc_service_info import (
    LifeTime,
    IServiceInfo,
    ServiceInfo,
    ProviderServiceInfo,
    ValueServiceInfo,
    GroupedServiceInfo,
    BindedServiceInfo,
)


class IServiceProvider:
    @abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError

    @abstractmethod
    def get(self, key, d=None) -> Any:
        '''
        get a service by key.
        '''
        raise NotImplementedError

    @abstractmethod
    def scope(self):
        '''
        create a scoped service provider for get scoped services.
        '''
        raise NotImplementedError


class ScopedServiceProvider(IServiceProvider):

    def __init__(self, services: ChainMap):
        super().__init__()
        self._services = services
        self._exit_stack = None
        self._services[Symbols.cache] = ValueServiceInfo({})

    def _get_service_info(self, key) -> IServiceInfo:
        try:
            return self._services[key]
        except KeyError:
            pass
        # load missing resolver and resolve service info.
        resolver: IServiceInfoResolver = self._services[Symbols.missing_resolver].get(self)
        return resolver.get(self, key)

    def __getitem__(self, key):
        service_info = self._get_service_info(key)
        try:
            return service_info.get(self)
        except ServiceNotFoundError as err:
            raise ServiceNotFoundError(key, *err.resolve_chain)

    def get(self, key, d=None) -> Any:
        '''
        get a service by key.
        '''
        try:
            return self[key]
        except ServiceNotFoundError as err:
            if len(err.resolve_chain) == 1:
                return d
            raise

    def enter(self, context):
        '''
        enter the context.

        returns the result of the `context.__enter__()` method.
        '''
        if self._exit_stack is None:
            self._exit_stack = ExitStack()
        return self._exit_stack.enter_context(context)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self._exit_stack is not None:
            self._exit_stack.__exit__(*args)

    def register_service_info(self, key, service_info: IServiceInfo):
        '''
        register a `IServiceInfo` by key.
        '''
        if not isinstance(service_info, IServiceInfo):
            raise TypeError('service_info must be instance of IServiceInfo.')
        self._services[key] = service_info

    def register(self, key, factory, lifetime):
        '''
        register a service factory by key.

        `factory` accept a function which require one or zero parameter.
        if the count of parameter is 1, pass a `IServiceProvider` as the argument.
        '''
        return self.register_service_info(key, ServiceInfo(self, key, factory, lifetime))

    def register_singleton(self, key, factory=None):
        '''
        register a service factory by key.

        `factory` accept a function which require one or zero parameter.
        if the count of parameter is 1, pass a `IServiceProvider` as the argument.
        '''
        return self.register(key, factory, LifeTime.singleton)

    def register_scoped(self, key, factory=None):
        '''
        register a service factory by key.

        `factory` accept a function which require one or zero parameter.
        if the count of parameter is 1, pass a `IServiceProvider` as the argument.
        '''
        return self.register(key, factory, LifeTime.scoped)

    def register_transient(self, key, factory=None):
        '''
        register a service factory by key.

        `factory` accept a function which require one or zero parameter.
        if the count of parameter is 1, pass a `IServiceProvider` as the argument.
        '''
        return self.register(key, factory, LifeTime.transient)

    def register_value(self, key, value):
        '''
        register a value by key.

        equals `register_transient(key, lambda ioc: value)`
        '''
        return self.register_service_info(key, ValueServiceInfo(value))

    def register_group(self, key, keys: list):
        '''
        register a grouped `key` for get other `keys`.

        the `keys` can be a ref and you can update it later.

        for example:

        ``` py
        provider.register_value('str', 'name')
        provider.register_value('int', 1)
        provider.register_group('any', ['str', 'int'])
        assert provider['any'] == ('name', 1)
        ```

        equals `register_transient(key, lambda ioc: tuple(ioc[k] for k in keys))`
        '''
        sym = Symbols.get_symbol_for_group_src(key)
        self.register_value(sym, keys)
        return self.register_service_info(key, GroupedServiceInfo(keys))

    def register_bind(self, new_key, target_key):
        '''
        bind `new_key` to `target_key` so
        you can use `new_key` as key to get value from service provider.

        equals `register_transient(new_key, lambda ioc: ioc[target_key])`
        '''
        return self.register_service_info(new_key, BindedServiceInfo(target_key))

    def scope(self):
        '''
        create a scoped service provider.
        '''
        return ScopedServiceProvider(self._services.new_child())

    @property
    def builder(self):
        '''
        get a new `ServiceProviderBuilder` for use high level api for this `ServiceProvider`.
        '''
        from .builder import ServiceProviderBuilder
        return ServiceProviderBuilder(self)


class ServiceProvider(ScopedServiceProvider):
    def __init__(self):
        super().__init__(ChainMap())
        self._services[Symbols.provider] = ProviderServiceInfo()
        self._services[Symbols.provider_root] = ValueServiceInfo(self)
        self._services[Symbols.missing_resolver] = ValueServiceInfo(ServiceInfoChainResolver())
        # service alias
        self._services['ioc'] = self._services[Symbols.provider]
        self._services['provider'] = self._services[Symbols.provider]
        self._services['service_provider'] = self._services[Symbols.provider]
