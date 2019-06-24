import difflib
import functools

from . import abstract


__all__ = ('specific', 'generic', 'rank', 'lead')


def single(value, argument):

    """
    Return the best matcher ratio of the two arguments.
    """

    matcher = difflib.SequenceMatcher(a = argument, b = value)

    ratio = matcher.ratio()

    return ratio


def specific(values, argument, single = single, key = None):

    """
    Return value-ratio pairs for values against the argument.
    """

    rank = single

    return abstract.specific(rank, values, argument, key = key)


def multiple(attributes, argument, specific = specific, key = None):

    """
    Return the highest best ratio against the argument.
    """

    assets = specific(attributes, argument, key = key)

    (junk, ratios) = zip(*assets)

    ratio = max(ratios)

    return ratio


def generic(fetcher, values, argument, multiple = multiple, key = None):

    """
    Return value-ratio pairs for value's attributes against argument.
    """

    rank = functools.partial(multiple, key = key)

    return abstract.generic(rank, fetcher, values, argument)


def select(pair):

    """
    Overglorified sorting key.
    """

    (value, ratio) = pair

    return ratio


def rank(pairs, select = select, reverse = False):

    """
    Use on results similar from the exposed functions.
    """

    return sorted(pairs, key = select, reverse = not reverse)


def lead(pairs, rank = rank):

    """
    Return the highest scored pair.
    """

    (leader, *lowers) = rank(pairs)

    (value, ratio) = leader

    return value
