#!/usr/bin/env python

import treap

class nlowest:
    def __init__(self, n, allow_duplicates=True):
        self.n = n
        if allow_duplicates:
            import dupdict_mod
            self.treap = dupdict_mod.Dupdict(dict_like_object=treap.treap())
        else:
            self.treap = treap.treap()
            
    def add(self, value):
        self.treap[value] = 0
        if len(self.treap) > self.n:
            (dummy, zero) = self.treap.remove_max()

    def __iter__(self):
        for key in self.treap:
            yield key

class nhighest:
    def __init__(self, n, allow_duplicates=True):
        self.n = n
        if allow_duplicates:
            import dupdict_mod
            self.treap = dupdict_mod.Dupdict(dict_like_object=treap.treap())
        else:
            self.treap = treap.treap()

    def add(self, value):
        self.treap[value] = 0
        if len(self.treap) > self.n:
            (dummy, zero) = self.treap.remove_min()

    def __iter__(self):
        for key in self.treap.reverse_iterator():
            yield key

