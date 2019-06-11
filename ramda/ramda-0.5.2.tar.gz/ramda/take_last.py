from ramda.curry import curry
from builtins import list as _list


@curry
def take_last(n, list):
    """Returns a new list containing the last n elements of the given list.
If n > list.length, returns a list of list.length elements"""
    try:
        return list[-n:]
    except TypeError:
        return _list(list)[-n:]
