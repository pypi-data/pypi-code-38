
from . import abstract


__all__ = ('sub', 'trail', 'prefix', 'parse', 'analyse', 'context', 'State')


def sub(store, *names):

    """
    Decorator for adding states to stores.
    Returns a new store for nesting.
    """

    def wrapper(invoke):

        value = type(store)()

        state = (invoke, value)

        for name in names:

            store[name] = state

        return value

    return wrapper


def trail(store, *names):

    """
    Get the value of a state from names.
    Will raise KeyError with the name not belonging to store.
    """

    return abstract.trail(store, names)


def prefix(values, content):

    """
    Discover start and separate from content.
    Will raise ValueError if none of the starts match.
    """

    for value in values:

        if content.startswith(value):

            break

    else:

        raise ValueError('invalid starts')

    content = content[len(value):]

    return (value, content)


lower = '.'


middle = ' '


upper = ' '


def parse(content, lower = lower, middle = middle):

    """
    Split content into names and argument.
    """

    return abstract.parse(content, lower, middle)


def analyse(store, content, parse = parse):

    """
    Parse content and find the respective invoke.
    """

    (names, argument) = parse(content)

    invoke = trail(store, *names) if names else None

    return (names, argument, invoke)


def context(store, starts, content, prefix = prefix, analyse = analyse):

    """
    Split content between start and rest, parse rest to find names and
    argument, use names to find an invoke. Can raise all respective errors.
    """

    (start, content) = prefix(starts, content)

    (names, argument, invoke) = analyse(store, content)

    return (start, names, argument, invoke)


class State(dict):

    """
    Neat little way of collecting this module's functionality.
    """

    __slots__ = ()

    sub = sub

    trail = trail

    analyse = analyse

    context = context
