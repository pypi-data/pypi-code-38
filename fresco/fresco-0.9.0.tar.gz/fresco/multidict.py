# Copyright 2015 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
"""
An order preserving multidict implementation
"""
from __future__ import absolute_import

try:
    from collections import MutableMapping
except ImportError:
    from UserDict import DictMixin

    class MutableMapping(DictMixin):
        """
        Emulate MutableMapping in Python<2.6
        """

from itertools import repeat


class MultiDict(MutableMapping):
    """
    Dictionary-like object that supports multiple values per key. Insertion
    order is preserved.

    Synopsis:

        >>> from fresco.multidict import MultiDict
        >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
        >>> d['a']
        1
        >>> d['b']
        3
        >>> d.getlist('a')
        [1, 2]
        >>> d.getlist('b')
        [3]
        >>> list(d.allitems())
        [('a', 1), ('a', 2), ('b', 3)]

    """

    setdefault = MutableMapping.setdefault
    __contains__ = MutableMapping.__contains__

    def __init__(self, *args, **kwargs):
        """
        MultiDicts can be constructed in the following ways:

            1. From a sequence of ``(key, value)`` pairs:

                >>> from fresco.multidict import MultiDict
                >>> MultiDict([('a', 1), ('a', 2)])  # doctest: +ELLIPSIS
                MultiDict(...)

            2. Initialized from another MultiDict:

                >>> from fresco.multidict import MultiDict
                >>> d = MultiDict([('a', 1), ('a', 2)])
                >>> MultiDict(d)  # doctest: +ELLIPSIS
                MultiDict(...)

            3. Initialized from a regular dict:

                >>> from fresco.multidict import MultiDict
                >>> MultiDict({'a': 1})  # doctest: +ELLIPSIS
                MultiDict(...)

            4. From keyword arguments:

                >>> from fresco.multidict import MultiDict
                >>> MultiDict(a=1)  # doctest: +ELLIPSIS
                MultiDict(...)

        """
        if len(args) > 1:
            raise TypeError("%s expected at most 2 arguments, got %d" %
                            (self.__class__.__name__,  1 + len(args)))
        self.clear()
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        """
        Return the first item associated with ``key``:

            >>> d = MultiDict([('a', 1), ('a', 2)])
            >>> d['a']
            1
        """
        try:
            return self._dict[key][0]
        except IndexError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        """
        Set the items associated with key to a single item, ``value``.

            >>> d = MultiDict()
            >>> d['b'] = 3
            >>> d
            MultiDict([('b', 3)])
        """
        _order = [(k, v) for k, v in self._order if k != key]
        _order.append((key, value))
        self._order = _order
        self._dict[key] = [value]

    def __delitem__(self, key):
        """
        Delete all values associated with ``key``
        """
        del self._dict[key]
        self._order = [(k, v) for (k, v) in self._order if k != key]

    def __iter__(self):
        """
        Return an iterator over all keys
        """
        return (k for k in self._dict)

    def get(self, key, default=None):
        """
        Return the first available value for key ``key``, or ``default`` if no
        such value exists:

            >>> d = MultiDict([('a', 1), ('a', 2)])
            >>> print(d.get('a'))
            1
            >>> print(d.get('b'))
            None
        """
        return self._dict.get(key, [default])[0]

    def getlist(self, key):
        """
        Return a list of all values for key ``key``.
        """
        return self._dict.get(key, [])

    def copy(self):
        """\
        Return a shallow copy of the dictionary:

            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> copy = d.copy()
            >>> copy
            MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> copy is d
            False
        """
        return self.__class__(self)

    def fromkeys(cls, seq, value=None):
        """\
        Create a new MultiDict with keys from seq and values set to value.

        Example:

            >>> MultiDict.fromkeys(['a', 'b'])
            MultiDict([('a', None), ('b', None)])

        Keys can be repeated:

            >>> d = MultiDict.fromkeys(['a', 'b', 'a'])
            >>> d.getlist('a')
            [None, None]
            >>> d.getlist('b')
            [None]

        """
        return cls(zip(seq, repeat(value)))
    fromkeys = classmethod(fromkeys)

    def items(self):
        """\
        Return a list of ``(key, value)`` tuples. Only the first ``(key,
        value)`` is returned where keys have multiple values:

            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> list(d.items())
            [('a', 1), ('b', 3)]
        """
        seen = set()
        for k, v in self._order:
            if k in seen:
                continue
            yield k, v
            seen.add(k)

    def listitems(self):
        """\
        Like ``items``, but returns lists of values:

            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> list(d.listitems())
            [('a', [1, 2]), ('b', [3])]
        """
        for k in self.keys():
            yield k, self._dict[k]

    def allitems(self):
        """\
        Return ``(key, value)`` pairs for each item in the MultiDict.
        Items with multiple keys will have multiple key-value pairs returned:

            >>> from fresco.multidict import MultiDict
            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> list(d.allitems())
            [('a', 1), ('a', 2), ('b', 3)]
        """
        return iter(self._order)

    def keys(self):
        """\
        Return dictionary keys. Each key is returned only once, even if
        multiple values are present.

            >>> from fresco.multidict import MultiDict
            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> list(d.keys())
            ['a', 'b']
        """
        return (k for k, v in self.items())

    def values(self):
        """\
        Return values from the dictionary. Where keys have multiple values,
        only the first is returned:

            >>> from fresco.multidict import MultiDict
            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> list(d.values())
            [1, 3]
        """
        return (v for k, v in self.items())

    def listvalues(self):
        """\
        Return an iterator over lists of values. Each item will be the list of
        values associated with a single key.

        Example usage:

            >>> from fresco.multidict import MultiDict
            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> list(d.listvalues())
            [[1, 2], [3]]
        """
        return (self._dict[k] for k in self.keys())

    def pop(self, key, *args):
        """
        Dictionary ``pop`` method. Return and remove the value associated with
        ``key``. If more than one value is associated with ``key``, only the
        first is returned.

        Example usage:

            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> d.pop('a')
            1
            >>> d
            MultiDict([('a', 2), ('b', 3)])
            >>> d.pop('a')
            2
            >>> d
            MultiDict([('b', 3)])
            >>> d.pop('a')
            Traceback (most recent call last):
                ...
            KeyError: 'a'
        """
        if len(args) > 1:
            raise TypeError("pop expected at most 2 arguments, got %d" %
                            (1 + len(args)))
        try:
            value = self._dict[key].pop(0)
        except (KeyError, IndexError):
            if args:
                return args[0]
            raise KeyError(key)
        self._order.remove((key, value))
        return value

    def popitem(self):
        """
        Return and remove a ``(key, value)`` pair from the dictionary.

        The item popped is always the most recently added key and the first
        value associated with it:

            >>> d = MultiDict([('a', 1), ('a', 2), ('b', 3)])
            >>> d.popitem()
            ('b', 3)
            >>> d.popitem()
            ('a', 1)
            >>> d.popitem()
            ('a', 2)
            >>> d.popitem() #doctest: +ELLIPSIS
            Traceback (most recent call last):
                ...
            KeyError: 'popitem(): dictionary is empty'
        """
        try:
            key = self._order[-1][0]
        except IndexError:
            raise KeyError('popitem(): dictionary is empty')
        return key, self.pop(key)

    def update(self, *args, **kwargs):
        r"""
        Update the MultiDict from another MultiDict, regular dictionary or a
        iterable of ``(key, value)`` pairs. New keys overwrite old keys - use
        :meth:`extend` if you want new keys to be added to old keys.

        Updating from another MultiDict:

            >>> d = MultiDict([('name', 'eric'), ('occupation', 'lumberjack')])
            >>> d.update(MultiDict([('mood', 'okay')]))
            >>> d
            MultiDict([('name', 'eric'), ('occupation', 'lumberjack'), ('mood', 'okay')])

        from a dictionary:

            >>> d = MultiDict([('name', 'eric'), ('hobby', 'shopping')])
            >>> d.update({'hobby': 'pressing wild flowers'})
            >>> d
            MultiDict([('name', 'eric'), ('hobby', 'pressing wild flowers')])

        an iterable of ``(key, value)`` pairs:

            >>> d = MultiDict([('name', 'eric'), ('occupation', 'lumberjack')])
            >>> d.update([('hobby', 'shopping'),
            ...           ('hobby', 'pressing wild flowers')])
            >>> d
            MultiDict([('name', 'eric'), ('occupation', 'lumberjack'), ('hobby', 'shopping'), ('hobby', 'pressing wild flowers')])

        or keyword arguments:

                >>> d = MultiDict([('name', 'eric'),\
                ...                ('occupation', 'lumberjack')])
                >>> d.update(mood='okay')

        """
        if len(args) > 1:
            raise TypeError("expected at most 1 argument, got %d" %
                            (1 + len(args),))
        if args:
            other = args[0]
        else:
            other = []
        return self._update(other, True, **kwargs)

    def extend(self, *args, **kwargs):
        """
        Extend the MultiDict with another MultiDict, regular dictionary or a
        iterable of ``(key, value)`` pairs. This is similar to :meth:`update`
        except that new keys are added to old keys.
        """
        if len(args) > 1:
            raise TypeError("expected at most 1 argument, got %d"\
                            (1 + len(args),))
        if args:
            other = args[0]
        else:
            other = []
        return self._update(other, False, **kwargs)

    def _update(self, *args, **kwargs):
        """
        Update the MultiDict from another object and optionally kwargs.

        :param other: the other MultiDict, dict, or iterable (first positional
                      arg)
        :param replace: if ``True``, entries will replace rather than extend
                        existing entries (second positional arg)
        """
        other, replace = args

        if isinstance(other, self.__class__):
            items = list(other.allitems())
        elif isinstance(other, dict):
            items = list(other.items())
        else:
            items = list(other)

        if kwargs:
            items += list(kwargs.items())

        if replace:
            replaced = set(k for k, v in items if k in self._dict)
            self._order = [(k, v)
                           for (k, v) in self._order if k not in replaced]
            for key in replaced:
                self._dict[key] = []

        for k, v in items:
            self._dict.setdefault(k, []).append(v)
            self._order.append((k, v))

    def __repr__(self):
        """
        ``__repr__`` representation of object
        """
        return '%s(%r)' % (self.__class__.__name__, list(self.allitems()))

    def __str__(self):
        """
        ``__str__`` representation of object
        """
        return repr(self)

    def __len__(self):
        """
        Return the total number of keys stored.
        """
        return len(self._dict)

    def __eq__(self, other):
        return isinstance(other, MultiDict) \
            and self._order == other._order

    def __ne__(self, other):
        return not (self == other)

    def clear(self):
        self._order = []
        self._dict = {}
