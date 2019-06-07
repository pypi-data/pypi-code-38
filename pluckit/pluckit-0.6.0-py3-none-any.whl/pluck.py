from copy import copy

from .pluckit import pluckit


__all__ = [ 'pluck' ]


def pluck(collection, handle):
    if collection is None:
        # nothing to pluck
        return None

    if isinstance(collection, dict):
        return { k : pluckit(v, handle) for k,v in collection.items() }

    if isinstance(collection, set):
        return { pluckit(x, handle) for x in collection }

    if isinstance(collection, tuple):
        return tuple( pluckit(x, handle) for x in collection )

    if isinstance(collection, list) or hasattr(collection, '__iter__'):
        # list or list like
        return [ pluckit(x, handle) for x in collection ]

    raise TypeError('unpluckable type: %s' % type(collection))
