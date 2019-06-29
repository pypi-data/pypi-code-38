def verify(item: list, default_to_empty=True):
    """
    In web scraping applications, we often receive lists where we would want strings. Using foo[0] often gives an error
    because the list may be empty (or we may have even received an empty string). Verify() verifies that the passed in
    list is not empty and returns the first item in the list. If the passed in item is a string instead, the string will
    be returned.
    :param item: The list to verify.
    :param default_to_empty: If True, verify() will return empty string if item does not exist in local.
    :return: First item of the list (or complete string, if string was passed in instead), or string representation.
    If item does not exist in local, returns empty string if default_to_empty is True.

    >>>verify('abc')
    'abc'
    >>>verify(['abc'])
    'abc'
    >>>verify(['a', 'b', 'c'])
    "['a', 'b', 'c']"
    """
    if default_to_empty:
        if 'item' not in locals():
            item = ''
            return item
            # Could alternatively return '', but this is more readable.

        elif isinstance(item, list) and len(item) == 1:
            return item[0]

        else:
            return item.__str__()

    else:
        if isinstance(item, list) and len(item) == 1:
            return item[0]

        else:
            return item.__str__()

def clean_list(item: list, remove_str_control=True, remove_empty=True):
    """
    When scraping information from the internet, lists sometimes have rows in them that consist just of newline
    characters, or newline characters might be at the beginning or end of rows in the list. This function cleans a list
    so that only rows with content are retained, and rows are also stripped of any string control characters.
    :param item: A list.
    :param remove_str_control: Should string control characters be removed?
    :param remove_empty: Should empty rows be removed?
    :return: Cleaned list.
    """
    if remove_str_control:
        item = [' '.join(row.split()) for row in item]
    else:
        item = [row.strip() for row in item]
    if remove_empty:
        item = [row for row in item if row]
    return item

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
