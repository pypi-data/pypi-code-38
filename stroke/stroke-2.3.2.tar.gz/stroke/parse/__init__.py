import itertools

from .general import *


__all__ = ('draw', 'craft', *general.__all__)


empty = ' '


default = ''


def wrap(ends, value):

    (open, close) = ends

    return open + value + close


enclose = '()'


variable = '[]'


def sketch(store, full = False, enclose = enclose, variable = variable):

    if isinstance(store, dict):

        store = store.items()

    for (index, bundle) in enumerate(store):

        (flag, item) = bundle

        if not item:

            value = default

        elif isinstance(item, str):

            value = wrap(variable, item)

        else:

            value = draw(item, full = full)

            value = wrap(enclose, value)

        if index or full:

            start = flag

            if not value is default:

                start += empty + value

            value = start

        yield value


def draw(store, **kwargs):

    values = sketch(store, **kwargs)

    value = empty.join(values)

    return value


def craft(store, value):

    flags = store.keys()

    limits = ((flag, 0) for flag in flags)

    pairs = general.flag(value, *limits)

    for (index, pair) in enumerate(pairs):

        (flag, value) = pair

        if not index:

            flag = next(iter(flags))

        item = store[flag]

        if isinstance(item, dict):

            value = resolve(item, value)

        else:

            value = general.strip(value)

        yield (flag, value)
