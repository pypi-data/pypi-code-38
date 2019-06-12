#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utilities for implementing various object-orientated design pattern concepts"""

# Copyright 2006 St James Software

import threading
from six import with_metaclass

class MultitonMetaclass(type):
    """Metaclass for Multiton. Needs to add a per-subclass lock object and
       key dictionary at class creation."""

    def __init__(cls, name, bases, dct):
        """Add a lock object at class creation time."""
        super(MultitonMetaclass, cls).__init__(name, bases, dct)
        setattr(cls,"_multiton_lock",threading.Lock())
        setattr(cls,"_multiton_cache",{})

class Multiton(with_metaclass(MultitonMetaclass, object)):
    """Thread-safe multiton baseclass. Sub-classes return only one object per set of
       initialisation parameters. These parameters must all be hashable.

       Instead of implementing __init__ sub-classes should implement multiton_setup
       which is only run when a new object instance is created. They may, of course,
       also implement __init__ which will be run every time someone attempts to
       instantiate the sub-class but this is usually not what you want. Note that
       multiton_setup will be called before __init__ if both are implemented.

       Object creation is thread-safe. It is the sub-classes responsibility to ensure
       that any methods other than multiton_setup (which will be called while holding
       a sub-class wide lock) are thread-safe."""

    def __new__(cls,*args):
        key = hash(tuple(args))
        try:
            cls._multiton_lock.acquire()
            try:
                return cls._multiton_cache[key]
            except KeyError:
                newobj = object.__new__(cls)
                cls._multiton_cache[key] = newobj
                newobj.multiton_setup(*args)
                return newobj
        finally:
            cls._multiton_lock.release()

    def multiton_setup(self,*args):
        """For sub-classes to implement if they have initialisation to do."""
        pass
