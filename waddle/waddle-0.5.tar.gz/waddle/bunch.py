from collections.abc import Mapping
from itertools import chain
import logging
import os
import re
from typing import Dict, Any, List, Optional, Tuple
from ruamel.yaml.comments import CommentedMap


__all__ = [
    'Bunch',
    'BunchList',
]
log = logging.getLogger(__name__)
AnyDict = Dict[str, Any]
dict_class = CommentedMap


def wrap(val, obj_wrapper=None):
    if isinstance(val, Mapping):
        return Bunch(val) if obj_wrapper is None else obj_wrapper(val)
    if isinstance(val, list):
        return BunchList(val)
    return val


class BunchList:
    def __init__(self, values, obj_wrapper=None):
        "make iterables into lists"
        if not isinstance(values, list):
            values = list(values)
        self.values = values
        self._obj_wrapper = obj_wrapper

    def __repr__(self):
        return repr(self.values)

    def __eq__(self, other):
        if isinstance(other, BunchList):
            return other.values == self.values
        # make sure we still equal to a dict with the same data
        return other == self.values

    def __ne__(self, other):
        return not self == other

    def __getitem__(self, key):
        value = self.values[key]
        if isinstance(key, slice):
            return BunchList(value, obj_wrapper=self._obj_wrapper)
        return wrap(value, self._obj_wrapper)

    def __setitem__(self, k, value):
        self.values[k] = value

    def __iter__(self):
        return map(lambda i: wrap(i, self._obj_wrapper), self.values)

    def __len__(self):
        return len(self.values)

    def __nonzero__(self):
        return bool(self.values)
    __bool__ = __nonzero__

    def __getattr__(self, name):
        return getattr(self.values, name)

    def __getstate__(self):
        return self.values, self._obj_wrapper

    def __setstate__(self, state):
        self.values, self._obj_wrapper = state


class Bunch:
    """
    Bunch pattern that allows us to reference settings values
    file in a pathy manner.  e.g.,

        x = Bunch()
        x.path.to.key = value
        x.path.greeting = 'hello'
        x['path.other_greeting'] = 'hello world'
    """
    def _set(self, key, value):
        """
        This is a useful function if you want to set
        an attribute on the underlying object so that
        the value isn't stored in the `self.values` dictionary.
        We need this because we override `__setattr__` below.
        """
        super(Bunch, self).__setattr__(key, value)

    def _get(self, key):
        """
        This is a useful function if you want to get
        an attribute on the underlying object.
        We need this because we override `__getattr__` below.
        """
        return self.__dict__.get(key)

    def __init__(self, values=None):
        if values is None:
            self.values: AnyDict = dict_class()
        else:
            self.values: AnyDict = values

    def __contains__(self, key):
        pieces = key.split('.')
        parent = self.walk_to_parent(pieces)
        if parent:
            return pieces[-1] in parent
        return False

    def __nonzero__(self):
        return bool(self.values)

    __bool__ = __nonzero__

    def __dir__(self):
        # introspection for auto-complete in IPython etc
        return chain(self.values, super(Bunch, self).__dir__())

    def __eq__(self, other):
        if isinstance(other, Bunch):
            return other.values == self.values
        # make sure we still equal to a dict with the same data
        return other == self.values

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        r = repr(self.values).replace('ordereddict', '')
        if len(r) > 60:
            r = r[:60] + '...])'
        return r

    def __getstate__(self) -> Tuple[Any]:
        # n.b., trailing comma is intentional
        # since pickle needs a tuple return value
        return self.values,  # pylint: disable=R1707

    def __setstate__(self, state):
        self.values = state[0]

    def __getattr__(self, key):
        if self._is_reserved(key):
            return self._get(key)
        try:
            return wrap(self.values[key])
        except KeyError:
            self.values[key] = dict_class()
            return wrap(self.values[key])

    def __delattr__(self, key):
        try:
            del self.values[key]
        except KeyError:
            raise AttributeError(
                '%r object has no attribute %r' % (
                    self.__class__.__name__, key))

    def __getitem__(self, key):
        pieces = key.split('.')
        parent = self.walk_to_parent(pieces)
        if parent:
            return wrap(parent.get(pieces[-1]))
        return None

    def __setitem__(self, key, value):
        pieces = key.split('.')
        parent = self.create_to_parent(pieces)
        parent[pieces[-1]] = value

    def __delitem__(self, key):
        pieces = key.split('.')
        parent = self.walk_to_parent(pieces)
        if parent:
            del parent[pieces[-1]]

    def _is_reserved(self, key):
        if key in [ 'values' ]:
            return True
        return key in self.__dict__ and not key.startswith('__')

    def __setattr__(self, key, value):
        if self._is_reserved(key):
            self._set(key, value)
            return
        self.values[key] = value

    def create_to_parent(self, pieces: List[str]) -> AnyDict:
        parent: AnyDict = self.values
        for y in pieces[:-1]:
            if y not in parent:
                child = parent[y] = dict_class()
            else:
                child = parent[y]
            parent = child
        return parent

    def walk_to_parent(self, pieces: List[str]) -> Optional[AnyDict]:
        parent: Dict[str, Any] = self.values
        for x in pieces[:-1]:
            parent = parent.get(x)
            if not isinstance(parent, dict):
                return None
        return parent

    def get(self, key, default=None):
        pieces = key.split('.')
        parent = self.walk_to_parent(pieces)
        if parent:
            return wrap(parent.get(pieces[-1], default))
        return wrap(default)

    def setdefault(self, key, value):
        pieces = key.split('.')
        parent = self.create_to_parent(pieces)
        key = pieces[-1]
        return parent.setdefault(key, value)

    def env(self):
        splitter = re.compile(r'[_.]')

        def fn(key, default=None):
            value = os.environ.get(key)
            if not value:
                pieces = splitter.split(key.lower())
                parent: AnyDict = self.walk_to_parent(pieces)
                if not isinstance(parent, dict):
                    return None
                value = parent.get(pieces[-1], default)
            return wrap(value)
        return fn

    def keys(self):
        return self.values.keys()

    def __iter__(self):
        return iter(self.values)

    def items(self, values=None, prefix=None):
        values = values or self.values
        prefix = prefix or []
        for key, value in values.items():
            if isinstance(value, Mapping):
                yield from self.items(
                    values=value,
                    prefix=prefix + [ key ])
            else:
                yield '.'.join(prefix + [ key ]), value

    def to_dict(self):
        return self.values
