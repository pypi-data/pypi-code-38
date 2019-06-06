"""
Module containing utility functions for working with dicts.
"""


def reduced_get(key, dicts, default=None):
    """
    Reduced version of ``dict.get()``.

    Parameters
    ----------
    key : any
        The key to search for in dicts.
    dicts : iterable of dicts
        The dicts to search for key. Dicts further right have higher priority.
    default : any, optional
        The default value if the key is not found in any of the dicts.

    Returns
    -------
    any
        The value of the key in the furthest-right dict, or default if none of
        the dicts had the key.
    """
    return reduce(lambda x, y: y.get(key, x), dicts, default)
