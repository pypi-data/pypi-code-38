import itertools

from . import abstract


__all__ = ('strip', 'clean', 'flag', 'group', 'split')


escape = '\\'


def strip(value, escape = escape, apply = str.strip, ghost = 1):

    """
    Strip value and clean escapes from ends.
    """

    value = apply(value)

    revert = len(escape)

    for index in range(ghost):

        if value.startswith(escape):

            value = value[revert:]

        if value.endswith(escape):

            value = value[:-revert]

    return value


def clean(values, strip = strip, empty = True):

    """
    Strip each value and yield if not empty.
    """

    for value in values:

        value = strip(value)

        if not value and empty:

            continue

        yield value


def flag(values, *limits, escape = escape, low = -1):

    """
    Differenciate values according to some keywords.
    """

    kills = 0

    revert = len(escape)

    current = None

    limits = {key: limit or low for (key, limit) in limits}

    for (valid, key, span) in abstract.flag(escape, values, limits):

        (start, stop) = (spot - kills for spot in span)

        if not valid:

            back = start - revert

            values = values[:back] + values[start:]

            kills += revert

            continue

        yield (current, values[:start])

        current = key

        values = values[stop:]

        kills += stop

    yield (current, values)


def group(values, *limits, flag = flag):

    """
    Group key-value pairs by the key.
    """

    (initial, *extras) = flag(values, *limits)

    (junk, initial) = initial

    try:

        (keys, limits) = zip(*limits)

    except ValueError:

        values = ()

    else:

        store = {key: [] for key in keys}

        for (key, value) in extras:

            store[key].append(value)

        (keys, values) = zip(*store.items())

    return (initial, *values)


def split(values, key, limit, group = group):

    """
    Separate flags by the key.
    """

    limit = (key, limit)

    (value, values) = group(values, limit)

    values.insert(0, value)

    return values
