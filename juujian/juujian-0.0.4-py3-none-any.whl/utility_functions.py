def verify(item: list):
    """
    In web scraping applications, we often receive lists where we would want strings. Using foo[0] often gives an error
    because the list may be empty (or we may have even received an empty string). Verify() verifies that the passed in
    list is not empty and returns the first item in the list. If the passed in item is a string instead, the string will
    be returned.
    :param item: The list to verify.
    :return: First item of the list (or complete string, if string was passed in instead), or string representation.

    >>>verify('abc')
    'abc'
    >>>verify(['abc'])
    'abc'
    >>>verify(['a', 'b', 'c'])
    "['a', 'b', 'c']"
    """
    if isinstance(item, list) and len(item) == 1:
        return item[0]

    else:
        return item.__str__()


def find_index(item: str, _list: list, else_return=9999):
    """
    Finds the index of an item and returns a numeric NA is item is not in list. This allows for instance for finding the
    min (or max) of several strings in a list, even if some of the strings are not in the list. The else_return
    parameter is meant to be set to a value high enough (or low enough) that the values that are not in the list are
    never picked.
    :param item: Item for which the index is to be found.
    :param _list: List in which to look up the item.
    :param else_return: Alternative value to return if item not in list.
    :return: Index (or placeholder value).

    """
    if item in _list:
        return _list.index(item)
    else:
        return else_return
