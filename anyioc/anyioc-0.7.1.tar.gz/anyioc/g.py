# -*- coding: utf-8 -*-
#
# Copyright (c) 2018~2999 - Cologler <skyoflw@gmail.com>
# ----------
# a global ioc
# ----------

import importlib
import functools
import inspect

from .ioc import ServiceProvider
from .utils import inject_by_name, dispose_at_exit

ioc = ServiceProvider()
dispose_at_exit(ioc)

# scoped global ioc

def _make_module_scoped_provider():
    from .ioc_resolver import IServiceInfoResolver
    from .ioc_service_info import ValueServiceInfo, IServiceInfo
    from .symbols import Symbols

    class ServiceProviderServiceInfoResolver(IServiceInfoResolver):
        def get(self, provider: ServiceProvider, key) -> IServiceInfo:
            new_provider = ServiceProvider()
            provider.enter(new_provider)

            try:
                init_ioc = importlib.import_module(key + '.init_ioc')
            except ImportError:
                init_ioc = None
            if init_ioc is not None:
                conf_ioc = getattr(init_ioc, 'conf_ioc', None)
                if conf_ioc is not None:
                    conf_ioc(new_provider)

            return ValueServiceInfo(new_provider)

    provider = ServiceProvider()
    provider[Symbols.missing_resolver].append(
        ServiceProviderServiceInfoResolver().cache(sync=True)
    )
    dispose_at_exit(provider)
    return provider

_module_scoped_providers = _make_module_scoped_provider()

def get_module_provider(module_name: str=None) -> ServiceProvider:
    '''
    get the module scoped singleton `ServiceProvider`.

    if `module_name` is `None`, use caller module name.

    if module `{module_name}.init_ioc` exists and it has a attr `conf_ioc`, will auto config like:

    ``` py
    (importlib.import_module(module_name + '.init_ioc')).conf_ioc(module_provider)
    ```
    '''
    if module_name is None:
        fr = inspect.getouterframes(inspect.currentframe())[1]
        mo = inspect.getmodule(fr.frame)
        module_name = mo.__name__

    if not isinstance(module_name, str):
        raise TypeError

    return _module_scoped_providers[module_name]

def get_namespace_provider(namespace: str=None) -> ServiceProvider:
    '''
    get the namespace scoped singleton `ServiceProvider`.

    if `namespace` is `None`, use caller namespace.

    for example, `get_namespace_provider('A.B.C.D')` is equals `get_module_provider('A')`
    '''
    if namespace is None:
        fr = inspect.getouterframes(inspect.currentframe())[1]
        mo = inspect.getmodule(fr.frame)
        namespace = mo.__name__

    if not isinstance(namespace, str):
        raise TypeError

    namespace = namespace.partition('.')[0]
    return _module_scoped_providers[namespace]
