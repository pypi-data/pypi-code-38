#
#  utils/stdio.py
#  bxtorch
#
#  Created by Oliver Borchert on May 11, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

class cached_property:
    """
    Python property which is computed exactly once and a cached value is
    returned upon every subsequent call.
    """

    # MARK: Initialization
    def __init__(self, func):
        self.func = func
        self._cache = None

    # MARK: Special Methods
    def __get__(self, obj, objtype):
        if self._cache is not None:
            return self._cache
        self._cache = self.func(obj)
        return self._cache

    def __repr__(self):
        return self.func.__doc__


def flatten(l):
    """
    Flattens the specified list.

    Parameters:
    -----------
    - l: list
        A two-dimensional list.

    Returns:
    --------
    - list
        The flattened list.
    """
    return [e for s in l for e in s]
