import collections


class MultiValueDict(collections.MutableMapping):
    """
    QueryDict acts like a plain `dict` type, but it handles
    automatially multiple values for same key.

    The most safest representation of URI query parameters is a list
    of tuples, because the parameter names aren't unique. Unfortunately
    accessing list of tuples is not so handy, so a mapping is
    required.

    In most cases query parameters looks like a mapping of simple
    key => value pairs, so we're expecting just one value per key. But when
    value is a list, we're expecting that accessing a key will return that
    list, not last nor first value.

    The problematic case is for keys, for which we're expecting always a list
    of values, but just one was passed in URI. Accessing the key will give
    just straight value instead of expected list with one item. In that cases
    you should use `QueryDict.getlist()` directly, which returns always a list.

    The values are stored internally as lists.

    `.items()` method returns a list of (key, value) tuples, where value is
    a single value from a key's values list. This means that key may not be
    unique. This representation is compatible with `urllib.urlencode()`.

    `.keys()` returns unique key names, same as for pure `dict`.

    `.values()` returns list of same values, which can be accessed by key,

    `.lists()` returns internal representation as list of lists.
    """

    def __init__(self, initial=None):
        self._data = {}
        self.update(initial)

    def update(self, data):
        if data is None:
            return
        else:
            try:
                data = list(data.items())
            except AttributeError:
                pass
        keys = list(set([x[0] for x in data]))
        for key in keys:
            self._data[key] = []
        for key, value in data:
            if isinstance(value, (list, tuple)):
                for x in value:
                    self._data[key].append(x)
            else:
                self._data[key].append(value)

    def items(self):
        result = []
        for key, values in self._data.items():
            result += list(map(lambda x: (key, x), values))
        return result

    def getlist(self, key, default=None):
        return self._data.get(key, default)

    def lists(self):
        return self._data.items()

    def __setitem__(self, key, value):
        return self.update({key: value})

    def __getitem__(self, key):
        return self._data[key][-1]\
                if len(self._data[key]) < 2 else self._data[key]

    def __delitem__(self, key):
        del self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return repr(self._data)


QueryDict = MultiValueDict
