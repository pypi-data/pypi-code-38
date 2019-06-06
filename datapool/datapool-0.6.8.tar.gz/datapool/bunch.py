# encoding: utf-8
from __future__ import absolute_import, division, print_function

import copy


class Bunch(dict):
    """Bunch decorates a dict with attributes for accessing the string keys::

            d = {"a": 3}
            x = Bunch(d)
            assert x.a == 3
            x.c = 7

       may be nested:

            d = {"a": 3, b: {"c": 4}}
            x = Bunch(d)
            assert x.b.c == 4
    """

    def __init__(self, dict_):
        super(Bunch, self).__init__(dict_)
        for name, value in dict_.items():
            if isinstance(value, dict):
                setattr(self, name, Bunch(value))
            if isinstance(value, (list, tuple)):
                new_value = []
                for item in value:
                    if isinstance(item, dict) and not isinstance(item, Bunch):
                        item = Bunch(item)
                    new_value.append(item)
                if isinstance(value, tuple):
                    new_value = tuple(new_value)
                setattr(self, name, new_value)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]

    __getattr__ = dict.__getitem__

    def copy(self):
        return self.__class__(dict.copy(self))

    def __str__(self):
        items = ((k, v) for (k, v) in sorted(self.items()) if not k.startswith("_"))
        items = ("{!r}: {!r}".format(k, v) for (k, v) in items)
        return "{" + ", ".join(items) + "}"

    __repr__ = __str__

    def __deepcopy__(self, memo):
        return self.__class__({k: copy.deepcopy(v) for k, v in self.items()})
