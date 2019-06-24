

__all__ = ()


def parse(content, lower, middle):

    try:

        (instruct, argument) = content.split(middle, 1)

    except ValueError:

        (instruct, argument) = (content, '')

    names = instruct.split(lower)

    return (names, argument)


def trail(store, names):

    for name in names:

        (value, store) = store[name]

    return value
