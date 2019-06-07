"""
Fantail
"""
# -*- coding: utf-8 -*-
from __future__ import print_function

import collections
import inspect

import yaml


class FantailConf(dict):

    def __init__(self, *a, **kw):
        dict.__init__(self)

        for item in a:
            if inspect.isclass(item):
                continue
            elif isinstance(item, dict):
                self.update(item)
            else:
                print(item, isinstance(item, FantailConf))
                raise Exception("invalid init argument: {}".format(str(item)))
        self.update(kw)

    def __setitem__(self, key, value):
        if isinstance(key, str) and '.' in key:
            keyA, keyB = key.split('.', 1)
            self[keyA][keyB] = value
        elif isinstance(value, dict) and len(value) > 0:
            self[key].update(value)
        elif isinstance(value, dict):
            #print('#EEE', key)
            dict.__setitem__(self, key, FantailConf())
        else:
            dict.__setitem__(self, key, value)


    def __delitem__(self, key):
        if isinstance(key, str) and '.' in key:
            keyA, keyB = key.split('.', 1)
            del self[keyA][keyB]
        else:
            super().__delitem__(key)


    def get(self, key, default=None):
        if isinstance(key, str) and '.' in key:
            keyA, keyB = key.split('.', 1)
            if not keyA in self:
                return default
            return self[keyA].get(keyB, default)
        else:
            return dict.get(self, key, default)


    def __contains__(self, key):
        if not '.' in key:
            return super(FantailConf, self).__contains__(key)

        keyA, keyB = key.split('.', 1)
        return keyB in self[keyA]

    def has_key(self, key):
        return self.__contains__(key)

    def __getitem__(self, key):
        if isinstance(key, str) and '.' in key:
            keyA, keyB = key.split('.', 1)
            containerA = self[keyA]
            return containerA[keyB]
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            print ("####", key)
            return self.__missing__(key)

    def __missing__(self, key):
        self[key] = FantailConf()
        return self[key]

    def __repr__(self):
        return str(dict(self))

    def __reduce__(self):
        return type(self), (FantailConf, ), None, None, iter(self.items())

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(FantailConf, self)

    def __deepcopy__(self, memo):
        import copy
        return type(self)(FantailConf,
                          copy.deepcopy(self.items()))


    def backfill(self, d=None):
        """
        as update - but use only values that do not exists
        """
        if d is None:
            return
        for k, v in d.items():
            if not k in self:
                self[k] = v


    def update(self, d=None, **kwargs):
        if d is None:
            pass
        elif isinstance(d, dict):
            for k, v in d.items():
                self[k] = v
        if len(kwargs):
            self.update(kwargs)


    def pretty(self):
        """
        Return a formatted string representation
        """

        # d = FantailConf()
        # for s in self.stack[::-1]:
        #     d.update(s)
        #
        # if 'hash' in d:
        #     del d['hash']

#        def unicode_representer(dumper, uni):
#            node = yaml.ScalarNode(tag='tag:yaml.org,2002:str', value=uni)
#            return node

#        yaml.add_representer(unicode, unicode_representer)

        return yaml.dump(self, default_flow_style=False)
