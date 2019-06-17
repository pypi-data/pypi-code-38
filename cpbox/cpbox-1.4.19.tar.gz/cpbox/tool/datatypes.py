import re
import six
from itertools import chain
try:              # Python 2
    items = 'iteritems'
except NameError: # Python 3
    items = 'items'

_RaiseKeyError = object()

def is_list_or_tuple(value):
    if isinstance(value, six.string_types):
        return False
    return isinstance(value, (list, tuple))

def merge(src, update, list_behaviour='replace'):
    for key, value in update.items():
        if isinstance(value, dict):
            old = src.setdefault(key, {})
            merge(old, value, list_behaviour)
        elif isinstance(value, six.string_types):
            src[key] = value
        elif isinstance(value, tuple):
            old = src.setdefault(key, ())
            if list_behaviour == 'merge' and is_list_or_tuple(node):
                src[key] = old + value
            else:
                src[key] = value
        elif isinstance(value, list):
            old = src.setdefault(key, [])
            if list_behaviour == 'merge' and is_list_or_tuple(old):
                old.extend(value)
            else:
                src[key] = value
        else:
            src[key] = value
    return src

def filter_item(item, key, re_pattern):
    if callable(key):
        value = key(item)
        return _match_value(value, re_pattern)
    else:
        value = item[key]
        return _match_value(value, re_pattern)

def filter_item_by_dict(item, dict):
    for key, value in dict.items():
        if key not in item or item[key] != value:
            return False
    return True

def filter_by_keys(item, keys):
    ret = {}
    for key in keys:
        ret[key] = item[key]
    return ret

def _match_value(value, re_pattern):
    if isinstance(value, six.string_types):
        return re_pattern.match(value)
    if isinstance(value, (list, tuple)):
        for _item in value:
            if _match_value(_item, re_pattern):
                return True
    return False

class NameIdItem(dict):

    __slots__ = ('id_key', 'name_key')

    def __init__(self, id_key, name_key, *args, **kwargs):
        self.id_key = id_key
        self.name_key = name_key
        super(NameIdItem, self).__init__(*args, **kwargs)

    def get_id(self):
        return self[self.id_key]

    def get_name(self):
        return self[self.name_key]

class NameIdDict(dict):

    __slots__ = ('id_key', 'name_key', 'name_id_map')

    def __init__(self, id_key, name_key, *args, **kwargs):
        self.id_key = id_key
        self.name_key = name_key
        self.name_id_map = {}
        data_indexed_by_id = self._process_args(*args, **kwargs)
        super(NameIdDict, self).__init__(data_indexed_by_id)

    def _process_args(self, *args, **kwargs):
        data = dict(*args, **kwargs)
        data_indexed_by_id = {}
        for item in data.values():
            id = item[self.id_key]
            name = item[self.name_key]
            self.name_id_map[name] = id
            data_indexed_by_id[id] = NameIdItem(self.id_key, self.name_key, item)
        return data_indexed_by_id

    def _should_be_id(self, k):
        if k in self.name_id_map:
            return self.name_id_map[k]
        return k

    def __getitem__(self, k):
        return super(NameIdDict, self).__getitem__(self._should_be_id(k))

    def __setitem__(self, k, v):
        return super(NameIdDict, self).__setitem__(self._should_be_id(k), v)

    def __delitem__(self, k):
        k = self._should_be_id(k)
        return super(NameIdDict, self).__delitem__(k)

    def get(self, k, default=None):
        return super(NameIdDict, self).get(self._should_be_id(k), default)

    def setdefault(self, k, default=None):
        return super(NameIdDict, self).setdefault(self._should_be_id(k), default)

    def pop(self, k, v=_RaiseKeyError):
        if v is _RaiseKeyError:
            return super(NameIdDict, self).pop(self._should_be_id(k))
        return super(NameIdDict, self).pop(self._should_be_id(k), v)

    def update(self, *args, **kwargs):
        super(NameIdDict, self).update(self._process_args(*args, **kwargs))

    def __contains__(self, k):
        return super(NameIdDict, self).__contains__(self._should_be_id(k))

    def copy(self): # don't delegate w/ super - dict.copy() -> dict :(
        return type(self)(self)

    @classmethod
    def fromkeys(cls, keys, v=None):
        return super(NameIdDict, cls).fromkeys((self._should_be_id(k) for k in keys), v)

    def __repr__(self):
        return '{0}({1})'.format(type(self).__name__, super(NameIdDict, self).__repr__())

    def get_id(self, id_or_name):
        if id_or_name in self:
            return self[id_or_name][self.id_key]

    def get_name(self, id_or_name):
        if id_or_name in self:
            return self[id_or_name][self.name_key]
