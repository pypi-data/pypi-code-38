#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Class for creating a unique ordered set.
   """

# Copyright 2006 St James Software

class OrderedSet(list):
    """
    Extends list class to a class which represents a set of unique items.
    Items are ordered by when they are first added to a list (new items are
    added at the end, unless they are already present, in which case their
    positions are left unaltered).
    """
    def __init__(self,*args,**kwargs):
        super(OrderedSet,self).__init__(self,*args,**kwargs)
        self._existing = {}
        self._append = super(OrderedSet,self).append

    def __delitem__(self,i):
        del self._existing[self[i]]
        super(OrderedSet,self).__delitem__(i)

    def extend(self,iterable):
        existing = self._existing
        append = self._append
        for x in iterable:
            if x in existing: continue
            existing[x] = 1
            append(x)

    def update(self,iterable):
        self.extend(iterable)

    def append(self,x):
        self.extend([x])

    def add(self,x):
        self.extend([x])

    def remove(self,x):
        super(OrderedSet,self).remove(x)
        del self._existing[x]
