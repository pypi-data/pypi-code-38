# -*- coding: utf-8 -*-
#
# Copyright (c) 2018~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

class Symbols:
    '''
    the symbols use for ioc.

    this keys are predefined in `ServiceProvider`.
    overwrite this keys will break the expected behavior.
    '''

    # current scoped `IServiceProvider`
    provider = object()

    # the root `IServiceProvider`
    provider_root = object()

    # the cache dict from `IServiceProvider`
    cache = object()

    # the missing resolver from `IServiceProvider`
    missing_resolver = object()
