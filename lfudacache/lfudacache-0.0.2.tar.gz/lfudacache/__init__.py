# -*- coding: UTF-8 -*-

import functools

try:
    import collections.abc as collections_abc
except ImportError:  # pragma: no cover
    import collections as collections_abc

from .utils import (
    CacheKeysView, CacheValuesView, CacheItemsView,
    closure_method, make_key
    )

from .__meta__ import version as __version__


__all__ = ['LFUDACache', 'make_key', 'memoize', '__version__']


class LFUDACache(collections_abc.MutableMapping):
    '''
    Less Frequently Used with Dynamic Aging cache, implementing the entire
    :class:`collections.abc.MutableMapping' interface.

    Implementation notes:
        * Most methods are self-optimizing into closures when referenced.
        * Cache behaves as as dict, all operations (except iteration or peek)
          count as cache MISS or HIT, affecting key ordering or insertion
          permeability.

    How it works:
        * Every cache hit increases item HIT counter
          (except :method:`LFUDACache.peek`).
        * Every cache miss increases MISSES counter by 1, up to top HITS.
        * When full, a new cache item will only be accepted if MISSES counter
          reaches the less frequently used item HIT counter, which is evicted.
        * When a new item is cached, its HIT counter is set equal to MISSES
          itself.
        * When an existing item is updated, its HIT counter is incremented
          by 1 to at least MISSES + 1.
    '''
    KEY, VALUE, HITS, PREV, NEXT, MISSES, FLAG = range(7)

    @closure_method
    def peek(self):
        '''
        Get value of key from cache, without updating HIT nor MISSES counters.

        If key is not found, and default is not given, KeyError is raised.

        :param key: cache item key
        :param default: optional default parameter
        :returns: cache item value
        :raises KeyError: if no default is given and key is not found

        Usage
        -----
        value = lfudacache.peek(key, 'default_value')
        '''
        VALUE = self.VALUE

        root = self._root
        cache_get = self._data.get
        error_class = KeyError

        def peek(key, default=root):
            item = cache_get(key, default)
            if item is root:
                raise error_class('Key %r not found.' % key)
            return item[VALUE]

        return peek

    @closure_method
    def get(self):
        '''
        Get value of key from cache.

        :param key: cache item key
        :param default: optional default parameter
        :returns: cache item value

        Usage
        -----
        value = lfudacache.get(key, 'default_value')
        '''
        VALUE = self.VALUE
        HITS = self.HITS
        PREV = self.PREV
        NEXT = self.NEXT
        MISSES = self.MISSES
        FLAG = self.FLAG

        cache_get = self._data.get
        root = self._root

        def get(key, default=None):
            item = cache_get(key, root)
            if item is root:
                # optimization: only increment MISSES up to top HITS
                if root[MISSES] < root[PREV][HITS]:
                    root[MISSES] += 1
                return default

            item[HITS] += 1

            # already sorted
            if item[HITS] < item[NEXT][HITS]:
                return item[VALUE]

            # extract
            item[PREV][NEXT] = item[NEXT]
            item[NEXT][PREV] = item[PREV]

            # position (start on next)
            item_next = item[NEXT][NEXT]
            item_hits = item[HITS]
            while item_hits >= item_next[HITS]:
                item_next = item_next[NEXT]

            # insert
            item[PREV] = item_next[PREV]
            item[NEXT] = item_next
            item[PREV][NEXT] = item
            item[NEXT][PREV] = item

            # invalidate iterators
            root[FLAG] = False

            return item[VALUE]

        return get

    @closure_method
    def __getitem__(self):
        '''
        Get value of key from cache.

        If key is not found, KeyError is raised.

        :param key: cache item key
        :param default: optional default parameter
        :returns: cache item value
        :raises KeyError: if key is not found

        Usage
        -----
        value = lfudacache[key]
        '''
        get = self.get
        root = self._root
        error_class = KeyError

        def getitem(key):
            value = get(key, root)
            if value is root:
                raise error_class('Key %r not found.' % key)
            return value
        return getitem

    @closure_method
    def __setitem__(self):
        '''
        Set value for key in cache.

        :param key: cache item key
        :param value: cache item value

        Usage
        -----
        lfudacache[key] = value
        '''
        PREV = self.PREV
        NEXT = self.NEXT
        VALUE = self.VALUE
        HITS = self.HITS
        KEY = self.KEY
        MISSES = self.MISSES
        FLAG = self.FLAG

        cache_get = self._data.get
        cache_delitem = self._data.__delitem__
        cache_setitem = self._data.__setitem__
        cache_len = self._data.__len__
        root = self._root
        maxsize = self._maxsize

        def setitem(key, value):
            item = cache_get(key, root)

            if item is root:
                if cache_len() == maxsize:
                    # less frequently used item
                    item = root[NEXT]
                    if root[MISSES] < item[HITS]:
                        return value  # not expirable yet

                    # uncache
                    cache_delitem(item[KEY])

                    # extract
                    item[PREV][NEXT] = item[NEXT]
                    item[NEXT][PREV] = item[PREV]

                # create new element
                item = [key, value, root[MISSES], root, root[NEXT]]
                cache_setitem(key, item)
            else:
                item[VALUE] = value

                if root[MISSES] > item[HITS]:
                    item[HITS] = root[MISSES]

                item[HITS] += 1

                # already sorted
                if item[HITS] < item[NEXT][HITS]:
                    return value

                # extract
                item[PREV][NEXT] = item[NEXT]
                item[NEXT][PREV] = item[PREV]

            # position (search from LFU)
            item_next = item[NEXT]
            item_hits = item[HITS]
            while item_hits >= item_next[HITS]:
                item_next = item_next[NEXT]

            # insert
            item[PREV] = item_next[PREV]
            item[NEXT] = item_next
            item[PREV][NEXT] = item
            item[NEXT][PREV] = item

            # invalidate iterators
            root[FLAG] = False

            return value

        return setitem

    @closure_method
    def __delitem__(self):
        '''
        Remove specified key and return the corresponding value.
        If key is not found KeyError is raised.

        :param key: cache item key
        :param value: cache item value

        Usage
        -----
        del lfudacache[key]
        '''
        PREV = self.PREV
        NEXT = self.NEXT
        FLAG = self.FLAG

        root = self._root
        cache_pop = self._data.pop
        error_class = KeyError

        def delitem(key):
            item = cache_pop(key, root)
            if item is root:
                raise error_class('Key %r not found.' % key)

            # extract
            item[PREV][NEXT] = item[NEXT]
            item[NEXT][PREV] = item[PREV]

            # invalidate iterators
            root[FLAG] = False

        return delitem

    @closure_method
    def popitem(self):
        '''
        Remove less frequently used key from cache.
        If key is not found, default is returned if given, otherwise
        KeyError is raised.

        :returns: both cache item key and value
        :rtype: tuple
        :raises KeyError: if cache is empty
        '''
        KEY = self.KEY
        VALUE = self.VALUE
        PREV = self.PREV
        NEXT = self.NEXT
        FLAG = self.FLAG

        root = self._root
        cache = self._data
        error_class = KeyError

        def popitem():
            # less frequently used item
            item = root[NEXT]
            if item is root:
                raise error_class('popitem(): cache is empty')

            # extract
            del cache[item[KEY]]
            item[PREV][NEXT] = item[NEXT]
            item[NEXT][PREV] = item[PREV]

            # invalidate iterators
            root[FLAG] = False

            return item[KEY], item[VALUE]

        return popitem

    @closure_method
    def pop(self):
        '''
        Remove specified key and return the corresponding value.
        If key is not found, default is returned if given, otherwise
        KeyError is raised.
        If key is not given, less frequently used item is removed and
        returned.

        :param key: item key
        :param default: optional default parameter
        :returns: cache item value
        :raises KeyError: if no default is given and key is not found
        '''
        PREV = self.PREV
        NEXT = self.NEXT
        VALUE = self.VALUE
        FLAG = self.FLAG

        error_class = KeyError
        cache_pop = self._data.pop
        root = self._root

        def pop(key, default=root):
            item = cache_pop(key, root)
            if item is root:
                if default is root:
                    raise error_class('Key %r not found.' % key)
                return default

            # extract
            item[PREV][NEXT] = item[NEXT]
            item[NEXT][PREV] = item[PREV]

            # invalidate iterators
            root[FLAG] = False

            return item[VALUE]

        return pop

    @closure_method
    def keys(self):
        '''
        Get CacheKeysView (subclass of :class:`collections.abc.KeysView`)
        instance to iterate cache keys.

        :returns: CacheKeysView instance interating cache keys
        :rtype: CacheKeysView
        '''

        view_class = CacheKeysView

        def keys():
            return view_class(self)

        return keys

    @closure_method
    def items(self):
        '''
        Get CacheItemsView (subclass of :class:`collections.abc.ItemsView`)
        instance to iterate cache key-value pairs.

        :returns: CacheItemsView instance interating cache keys
        :rtype: CacheItemsView
        '''
        PREV = self.PREV
        KEY = self.KEY
        VALUE = self.VALUE
        FLAG = self.FLAG

        view_class = CacheItemsView
        error_class = RuntimeError
        root = self._root

        def iter_items():
            # detect changes
            root[FLAG] = True

            # more frequently used item
            prev = root[PREV]
            while prev is not root and root[FLAG]:
                yield prev[KEY], prev[VALUE]
                prev = prev[PREV]

            # detect changes
            if not root[FLAG]:
                raise error_class('cache changed during iteration')

        def items():
            return view_class(self, iter_items)

        return items

    @closure_method
    def values(self):
        '''
        Get CacheValuesView (subclass of :class:`collections.abc.valuesView`)
        instance to iterate cache key-value pairs.

        :returns: CacheValuesView instance interating cache keys
        :rtype: CacheValuesView
        '''
        PREV = self.PREV
        VALUE = self.VALUE
        FLAG = self.FLAG

        view_class = CacheValuesView
        error_class = RuntimeError
        root = self._root

        def iter_values():
            # detect changes
            root[FLAG] = True

            # more frequently used item
            prev = root[PREV]
            while prev is not root and root[FLAG]:
                yield prev[VALUE]
                prev = prev[PREV]

            # detect changes
            if not root[FLAG]:
                raise error_class('cache changed during iteration')

        def values():
            return view_class(self, iter_values)

        return values

    @closure_method
    def __eq__(self):
        '''
        Checks equality against other :class:`collections.abc.Mapping`.

        :returns: True if all items on self and other are the same
        :rtype: bool
        '''
        len_fnc = self.__len__
        item_fnc = self.items

        def eq(other):
            return len_fnc() == len(other) and all(
                a is b or a == b
                for a, b in zip(other.items(), item_fnc())
                )

        return eq

    @closure_method
    def __iter__(self):
        '''
        Get iterable of cache keys sorted from most to lesser frequently used.

        :yields: cache keys
        '''
        PREV = self.PREV
        KEY = self.KEY
        FLAG = self.FLAG

        error_class = RuntimeError
        root = self._root

        def iter_keys():
            # detect changes
            root[FLAG] = True

            # more frequently used item
            prev = root[PREV]
            while prev is not root and root[FLAG]:
                yield prev[KEY]
                prev = prev[PREV]

            # detect changes
            if not root[FLAG]:
                raise error_class('cache changed during iteration')

        return iter_keys

    @closure_method
    def __reversed__(self):
        '''
        Get iterable of cache keys sorted from lesser to most frequently used.

        :yields: cache keys
        '''
        NEXT = self.NEXT
        KEY = self.KEY
        FLAG = self.FLAG

        error_class = RuntimeError
        root = self._root

        def iter_keys():
            # detect changes
            root[FLAG] = True

            # less frequently used item
            next = root[NEXT]
            while next is not root and root[FLAG]:
                yield next[KEY]
                next = next[NEXT]

            # detect changes
            if not root[FLAG]:
                raise error_class('cache changed during iteration')

        return iter_keys

    @closure_method
    def clear(self):
        '''
        Evict the entire cache.
        '''
        cache_clear = self._data.clear
        root_clear = functools.partial(
            self._root.__setitem__,
            slice(self.PREV, self.FLAG + 1),
            (self._root, self._root, 0, 0)
            )

        def clear():
            cache_clear()
            root_clear()

        return clear

    @closure_method
    def __contains__(self):
        '''
        Get if given key is on cache.

        :returns: True if key is cached, False otherwise

        Usage
        -----
        exists = key in lfudacache
        '''
        cache = self._data

        def contains(key):
            return key in cache

        return contains

    @closure_method
    def __len__(self):
        '''
        Return current cache size.

        Usage
        -----
        size = len(lfudacache)
        '''
        cache_len = self._data.__len__

        def len():
            return cache_len()

        return len

    @property
    def maxsize(self):
        '''
        Maximum cache size
        '''
        return self._maxsize

    def __init__(self, maxsize):
        '''
        :param maxsize: number of items to keep on cache
        :type maxsize: int
        '''
        self._maxsize = maxsize
        self._root = root = []
        self._data = {}

        root[:] = [None, None, float('inf'), root, root, 0, False]


def memoize(maxsize, fnc=None, key_fnc=make_key):
    '''
    Memoization decorator using Less Frequenty Used with Dynamic Aging cache
    eviction algorithm.

    The LFUDACache instance is available on the decorated function, as `cache`
    property.

    :param maxsize: maximum cache size
    :type maxsize: int
    :param fnc: optional function to memoize (non-decorating behavior)
    :type fnc: callable or None
    :param key_fnc: optional custom cache key function, receiving argument
                    list and keyword argument dict
    :type key_fnc: callable
    :returns: decorator if fnc is not given, wrapped function otherwise
    :rtype: callable
    '''

    if not isinstance(maxsize, int):
        raise TypeError('Expected maxsize to be an integer')

    def decorator(fnc):
        NOT_FOUND = object()
        cache = LFUDACache(maxsize)
        getitem = cache.get
        setitem = cache.__setitem__

        @functools.wraps(fnc)
        def wrapped(*args, **kwargs):
            key = key_fnc(args, kwargs)
            result = getitem(key, NOT_FOUND)
            if result is NOT_FOUND:
                result = fnc(*args, **kwargs)
                setitem(key, result)
            return result

        wrapped.cache = cache
        return wrapped

    return decorator(fnc) if callable(fnc) else decorator
