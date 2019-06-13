from .generics import *
from .agg_methods import _or_default


class ItemWithIndex(Generic[T]):
    def __init__(self, index: int, item: T):
        self.index = index
        self.item = item

def with_indices(en):
    for index,item in enumerate(en):
        yield ItemWithIndex(index,item)


def foreach(en, action):
    for element in en:
        if action is not None:
            action(element)

def foreach_and_continue(en,action):
    for element in en:
        action(element)
        yield element

def arg_extremum_default(en, selector, is_max, with_default, default):
    argmax = None
    argmax_item = None
    first_time = True
    for item in en:
        if first_time:
            first_time = False
            argmax_item=item
            argmax = selector(item)
        else:
            value = selector(item)
            if (is_max and value>argmax) or (not is_max and value<argmax):
                argmax = value
                argmax_item = item
    if not first_time:
        return argmax_item

    return _or_default(with_default, default)

def append(en,array):
    for e in en:
        yield e
    for e in array:
        yield e

def prepend(en, array):
    for e in array:
        yield e
    for e in en:
        yield e


