#!/usr/bin/env python

from six import with_metaclass

class enum_meta(type):
    def __iter__(cls):
        """iterates over the constants defined in the class"""
        cls._build_lookups()
        # TODO: iterate in definition order rather than constant order
        for constant in sorted(cls._constant_lookup):
            yield constant

_NO_DEFAULT = object()

class enum(with_metaclass(enum_meta, object)):
    __constant_class__ = int
    @classmethod
    def _build_lookups(cls):
        if not hasattr(cls, "_constant_lookup"):
            builtin_attrs = dict.fromkeys(dir(enum))
            constant_attrs = [(attr, getattr(cls, attr, None))
                for attr in dir(cls)
                if attr not in builtin_attrs]
            cls._constant_lookup = dict(
                [(value, attr) for (attr, value) in constant_attrs if isinstance(value, cls.__constant_class__)]
                )
            cls._stringid_lookup = dict(
                [(attr, value) for (attr, value) in constant_attrs if isinstance(value, cls.__constant_class__)]
                )

    @classmethod
    def identify(cls, constant, default=_NO_DEFAULT):
        """returns the string identifier this class uses for the given constant"""
        cls._build_lookups()
        if constant not in cls._constant_lookup:
            if default is not _NO_DEFAULT:
                return default
            raise KeyError("%s does not define anything as the constant %s" % (cls.get_name(), constant))
        return cls._constant_lookup[constant]

    @classmethod
    def lookup(cls, stringid, default=_NO_DEFAULT):
        """returns the constant this class maps the given string identifier too"""
        cls._build_lookups()
        if stringid not in cls._stringid_lookup:
            if default is not _NO_DEFAULT:
                return default
            raise KeyError("%s does not define a constant for the string id %s" % (cls.get_name(), stringid))
        return cls._stringid_lookup[stringid]

    @classmethod
    def get_name(cls):
        """returns the name of the class (can be overridden)"""
        return cls.__name__

