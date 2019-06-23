"""
  Copyright (c) 2017-2018 Atrio, Inc.

  All rights reserved.
"""

class NestedMixin(object):
    def __init__(self, parent, path, children):
        self._parent = parent
        self._path = str(path).replace('_', '-')
        self._children = children
        self._root = None

    @property
    def root(self):
        if self._root is None:
            if self._parent is None:
                self._root = self
            else:
                self._root = self._parent.root
        return self._root

    @property
    def full_path(self):
        if self._parent is not None:
            return self._parent.full_path + self._path + '/'
        else:
            return self._path + '/'
