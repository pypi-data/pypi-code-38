# -*- coding: UTF-8 -*-

import functools

try:
    import collections.abc as collections_abc
except ImportError:  # pragma: no cover
    import collections as collections_abc


class closure_method(object):
    '''
    Descriptor decorator to allow closure-optimized functions to replace
    decorated instance methods returning them.
    '''
    def __init__(self, func):
        '''
        :param func: method which returns a closure-oprimized function
        :type func: callable
        '''
        self.func = func

    def __call__(self, instance, *args, **kwargs):
        '''
        Optimize, cache and call closure-based function.

        :param instance: class instance
        :type instance: object
        '''
        return self.__get__(instance)(*args, **kwargs)

    def __get__(self, instance, owner=None):
        '''
        Optimize, cache and return closure-based function.

        :param instance: class instance
        :type instance: object
        '''
        if instance is None:
            return self

        value = functools.update_wrapper(self.func(instance), self.func)
        self.__set__(instance, value)
        return value

    def __set__(self, instance, value):
        '''
        Replace this desriptor on instance with given value.

        :param instance: class instance
        :type instance: object
        :param value: value to replace current descriptor
        '''
        instance.__dict__[self.func.__name__] = value


class CacheView(collections_abc.MappingView):
    '''
    Base class from cache mapping views.

    With both customizable mapping and iteration to bypass
    cache-specific logic.
    '''
    def __init__(self, mapping, iter_fnc=None):
        super(CacheView, self).__init__(mapping)
        self._iter_fnc = iter_fnc or mapping.__iter__

    def __iter__(self):
        return self._iter_fnc()


class CacheKeysView(CacheView, collections_abc.KeysView):
    '''
    Class from cache mapping keys view.
    '''
    pass


class CacheItemsView(CacheView, collections_abc.ItemsView):
    '''
    Base class from cache mapping items view.
    '''
    NOT_FOUND = object()

    def __contains__(self, pair):
        key, value = pair
        stored = self._mapping.peek(key, self.NOT_FOUND)
        return stored is value or stored == value


class CacheValuesView(CacheView, collections_abc.ValuesView):
    '''
    Base class from cache mapping values view.
    '''
    def __contains__(self, value):
        return value in iter(self)


def make_key(args, kwargs, _tuple=tuple, _hash=hash, _type=type):
    '''
    Hash function for function arguments.

    :param args: argument iterable
    :type args: iterable
    :param kwargs: keyword argument dict-like object
    :type kwargs: dict
    :returns: hash of arg and kwargs
    :rtype: int
    '''
    return _hash((
        _tuple((value, _type(value)) for value in args),
        _tuple((key, value, _type(value)) for key, value in kwargs.items())
        ))
