import re
import itertools


__all__ = ()


def flag(escape, values, limits):

    keys = limits.keys()

    match = lambda key: re.finditer(key, values)

    matches = itertools.chain.from_iterable(map(match, keys))

    matches = sorted(matches, key = lambda match: match.start())

    for match in matches:

        span = match.span()

        (start, end) = span

        defeat = lambda other: (
            not match is other
            and start <= other.start() < end
            and other.end() > end
        )

        if any(map(defeat, matches)):

            continue

        key = match.re.pattern

        limit = limits[key]

        back = start - len(escape)

        against = values[back:start]

        if not limit:

            continue

        valid = not against == escape

        limits[key] = limit - valid

        yield (valid, key, span)
