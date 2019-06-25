#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from collections.abc import MutableMapping, Mapping
except ImportError:
    from collections import MutableMapping, Mapping


_not_given = object()


class myobject(object):
    """Initialize object attributes using kwargs
    """

    def __init__(self, *args, **kwargs):
        """Initialize
        """
        for k, v in list(kwargs.items()):
            setattr(self, k, v)


class dictobj(MutableMapping):
    """Dictionary exposing its values over attributes
    """

    def __init__(self, *args, **kwargs):
        """Initializing

        Works like :py:class:`dict`'s initialization
        """
        self.__data = {}

        for arg in args + (kwargs,):
            dic = arg
            if not isinstance(arg, Mapping):
                dic = dict(arg)

            for k, v in list(dic.items()):
                if isinstance(v, Mapping):
                    v = dictobj(v)

                self[k] = v

        self._changed_values = {}
        self._deleted_keys = set()
        self._initialized = True

    def __repr__(self):
        """Representing dictobj
        """
        return "%s(%s)" % (self.__class__.__name__, repr(self.__data))

    def _updated_keys(self, *args, **kwargs):
        """Track keys that get updated
        """
        # TODO we need to find a way to detect updates when item is a reference
        # (e.g. a dict or list) and this reference gets updated
        # TODO maybe it's easier to store a 'checkpoint' and do a dictdiff on
        # this...
        if '_initialized' in self.__dict__:
            changed = {}
            changed.update(*args, **kwargs)
            self._changed_values.update(changed)
            self._deleted_keys -= set(changed.keys())

    def _removed_key(self, key):
        """Track keys that get removed
        """
        if '_initialized' in self.__dict__:
            self._changed_values.pop(key, None)
            self._deleted_keys.add(key)

    def _clear_changes_tracking(self):
        """Clear changes tracking
        """
        if '_initialized' in self.__dict__:
            self._changed_values.clear()
            self._deleted_keys = set()

    def clear(self):
        """Clear
        """
        self._clear_changes_tracking()
        return super(dictobj, self).clear()

    def __getitem__(self, key):
        return self.__data[key]

    def __setitem__(self, key, value):
        self._updated_keys({key: value})
        self.__data[key] = value

    def __delitem__(self, key):
        self._removed_key(key)
        del self.__data[key]

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    def __getattribute__(self, name):
        """Get attribute

        - if it's on the object/class, we'll get it from there
        - otherwise, try to get it from the dict

        NOTE: the object/class attributes take precedence over the dict

        :returns: The attribute
        :raises: (AttributeError) If not there
        """
        dct = object.__getattribute__(self, '__dict__')
        cls = object.__getattribute__(self, '__class__')
        if name in dct or hasattr(cls, name) or '_initialized' not in dct:
            # try to get the standard attribute (method, variable, etc) if it's
            # present on the class or we're not initialized
            return object.__getattribute__(self, name)
        else:
            # when trying to get an unknown attribute, get it from the dict
            try:
                return self.__getitem__(name)
            except Exception:
                # we didn't find the attribute
                pass

        raise AttributeError("%s not found in %s" % (name, cls.__name__))

    def __setattr__(self, item, value):
        """Maps attributes to values.
        Only if we are initialised

        NOTE: to avoid issues, we don't allow to setattr on class attributes
            (e.g. to avoid modifying dict.items function)
        """
        try:
            if '_initialized' not in self.__dict__:
                # this test allows attributes to be set in the __init__ method
                return object.__setattr__(self, item, value)
            elif item in self.__dict__:
                # any normal attributes are handled normally
                return object.__setattr__(self, item, value)
            elif isinstance(getattr(self.__class__, item, None), property):
                # this allows properties to behave properly
                return object.__setattr__(self, item, value)
        except AttributeError:
            raise AttributeError(u"Can't set attribute '%s' of %r" % (
                item, self))

        return self.__setitem__(item, value)

    def __delattr__(self, name):
        """Delete attribute
        """
        if name in self.__dict__ or hasattr(self.__class__, name):
            # any normal attributes are handled normally
            return object.__delattr__(self, name)

        return self.__delitem__(name)


class SimpleMultiDict(dict):
    """Multi dict (a key can have multiple values)
    """

    def getlist(self, key):
        return self[key] if type(self[key]) == list else [self[key]]

    def __repr__(self):
        return type(self).__name__ + '(' + dict.__repr__(self) + ')'


#EOF
