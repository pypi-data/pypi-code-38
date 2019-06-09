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

    # the named group tag for builder
    _group_src_tag = object()

    @classmethod
    def get_symbol_for_group_src(cls, group):
        '''
        get a symbol for get group source from `ServiceProvider`.

        this may change after anyioc update (include return value type).
        '''
        return (cls._group_src_tag, group)
