###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
@author: Stefan-Gabriel CHITIC
'''


class Injector(object):
    """
    The injector provides instances implementing interfaces using classes,
    factories or live objects
    """

    def __init__(self):
        self._providers = {None: {}}

    def provide(self, iface, cls, name=None):
        "Bind an interface to a class"
        assert issubclass(cls, iface)
        self.provide_factory(iface, cls, name)

    def provide_instance(self, iface, obj, name=None):
        "Bind an interface to an object"
        assert isinstance(obj, iface)
        self.provide_factory(iface, lambda: obj, name)

    def provide_factory(self, iface, method, name=None):
        "Bind an interface to a factory method, called with no parameters"
        assert callable(method)
        self._providers.setdefault(name, {})[iface] = method

    def get_instance(self, iface_or_cls, name=None):
        "Get an object implementing an interface"
        provider = self._providers[name].get(iface_or_cls, iface_or_cls)
        return provider()

    def __repr__(self):
        return '<injector>'

# Import this and provide your implementations
injector = Injector()


class Injectable(type):
    "Metaclass to implements dependency injection"

    def __call__(cls, *args, **kwargs):
        for k, c in cls.__dependencies__.items():
            if k not in kwargs:
                kwargs[k] = injector.get_instance(c)
        r = super(Injectable, type(cls)).__call__(cls, *args, **kwargs)
        return r


def _with_meta(new_meta, cls):
    meta = type(cls)
    if not issubclass(meta, new_meta):
        if new_meta.__mro__[1:] != meta.__mro__:
            # class has a custom metaclass, we extend it on the fly
            name = new_meta.__name__ + meta.__name__
            new_meta = type(name, (new_meta,) + meta.__bases__, {})
        # rebuild the class
        return new_meta(cls.__name__, cls.__bases__, dict(cls.__dict__))
    else:
        # class has alredy the correct metaclass due to inheritance
        return cls


def _inject(_injectable_type, **dependencies):
    def annotate(cls):
        cls = _with_meta(_injectable_type, cls)
        setattr(cls, '__dependencies__', dependencies)
        return cls
    return annotate


def inject(**dependencies):
    "Bind constructor arguments to implementations"
    return _inject(Injectable, **dependencies)


__all__ = ['injector', 'inject']
