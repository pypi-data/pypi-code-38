# -*- coding: utf-8 -*-
# based upon https://gist.github.com/eoghanmurray/1360da8635f0a6a6d528
from sqlalchemy.ext.mutable import Mutable


class MutableList(Mutable, list):
    @classmethod
    def coerce(cls, key, value):
        """
        Convert plain list to MutableList.
        """
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __getstate__(self):
        return list(self)

    def __setstate__(self, state):
        self.extend(state)

    def append(self, value):
        list.append(self, value)
        self.changed()

    def extend(self, iterable):
        list.extend(self, iterable)
        self.changed()

    def insert(self, index, item):
        list.insert(self, index, item)
        self.changed()

    def pop(self, index=None):
        if index:
            list.pop(self, index)
        else:
            list.pop(self)
        self.changed()

    def remove(self, item):
        list.remove(self, item)
        self.changed()

    def reverse(self):
        list.reverse(self)
        self.changed()

    def sort(self, **kwargs):
        list.sort(self, **kwargs)
        self.changed()
