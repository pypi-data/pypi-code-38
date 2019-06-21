

__all__ = ()


def specific(rank, values, argument, key = None):

    for value in values:

        check = key(value) if key else value

        level = rank(check, argument)

        yield (value, level)


def generic(rank, fetcher, values, argument):

    for value in values:

        attributes = tuple(fetcher(value))

        if not attributes:

            continue

        level = rank(attributes, argument)

        yield (value, level)
