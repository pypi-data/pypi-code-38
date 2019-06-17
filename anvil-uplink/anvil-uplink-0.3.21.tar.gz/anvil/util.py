def _wrap(value):
    if isinstance(value, (WrappedObject, WrappedList)):
        return value
    elif isinstance(value, dict):
        return WrappedObject(value)
    elif isinstance(value, list):
        wl = WrappedList()
        for i in value:
            wl.append(i)
        return wl
    else:
        return value


class WrappedObject(dict):
    _name = "wrapped_object"

    def __init__(self, d=None, **kwargs):

        self.__setitem__("type", self._name)

        if d and isinstance(d, dict):
            for k in d.keys():
                self.__setitem__(k, d[k])

        for k in kwargs.keys():
            self.__setitem__(k, kwargs[k])

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, _wrap(value))

    def __getitem__(self, key):
        _sentinel = WrappedObject()
        r = dict.get(self, key, _sentinel)

        if r is _sentinel:
            dict.__setitem__(self, key, _sentinel)

        return r

    def __repr__(self):
        return "%s<%s>" % (
            self._name[0].upper() + self._name[1:],  # Horrible hack
            ", ".join(["%s=%s" % (k, repr(self[k])) for k in self.keys()])
        )


class WrappedList(list):
    def __init__(self, lst=[]):
        if len(lst) > 0:
            raise Exception("Can only construct empty WrappedList objects for now.")

    def append(self, item):
        list.append(self, _wrap(item))

    def extend(self, items):
        for i in items:
            self.append(i)

    def insert(self, offset, item):
        list.insert(self, offset, _wrap(item))
