"""Dictionary utility tools"""


def merge(*dicts):
    """Deep merges right the most dictionaries into the left most one.

    Args:
        *dicts (dict): dictionaries to be merged.

    Examples:

        >>> a = {'a': 1, 'b': 2}
        >>> b = {'b': 3, 'c': {'c1': 4, 'c2': 3}}
        >>> c = {'a': 3, 'c': {'c1': 3 }}
        >>> print(merge(a,b,c))
        {'c': {'c1': 3, 'c2': 3}, 'a': 3, 'b': 3}

    Returns:
        dict
    """

    def _merge(dict1, dict2):
        for k in set(dict1.keys()).union(dict2.keys()):
            if k in dict1 and k in dict2:
                if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                    yield (k, dict(merge(dict1[k], dict2[k])))
                else:
                    # If one of the values is not a dict, you can't continue merging it.
                    # Value from second dict overrides one in first and we move on.
                    yield (k, dict2[k])
            elif k in dict1:
                yield (k, dict1[k])
            else:
                yield (k, dict2[k])

    result = dict()
    for index, _dict in reversed(list(enumerate(dicts))):
        if not result:
            result = dict(_merge(dicts[index-1], _dict))
        result = dict(_merge(dicts[index-1], result))

    return dict(result)


def get_nested(the_dict, nested_key, default=None):
    """
    Returns the value of a nested key in an dictorinary

    Args:
        the_dict (dict): The dictionary to get the nested value from
        nested_key (str): The nested key
        default: The value to be returned if the key is not found

    Returns:

    Examples:
        >>> t = {'a': {'b': {'c':'value_of_c'}}}
        >>> get_nested(t, 'b:c')
        'value_of_c'
        >>> get_nested(t, 'b:c:d', 'not found')
        'not found'

    """

    keys = nested_key.split(':')

    if not hasattr(the_dict, '__iter__'):
        return default

    if len(keys) == 1:
        if keys[0] in the_dict:
            return the_dict[keys[0]]
        else:
            return default
    else:
        if keys[0] in the_dict:
            return get_nested(the_dict[keys[0]], ':'.join(keys[1:]), default)
        else:
            return default


def update_nested(the_dict, nested_key, value):
    """
    Updates nested keys inside a dictionary

    Args:
        the_dict (dict): The dictionary to be updated
        nested_key (str): The nested key
        value: The value to be set to the nested key

    Examples:
        >>> t = {}
        >>> update_nested(t, 'a:b:c', 1)
        >>> t
        {'a': {'b': {'c': 1}}}
        >>> update_nested(t, 'a:b:d', 1)
        >>> t
        {'a': {'b': {'c': 1, 'd': 1}}}
        >>> update_nested(t, 'a:b:c', 2)
        >>> t
        {'a': {'b': {'c': 2, 'd': 1}}}
    """
    keys = nested_key.split(':')

    if len(keys) == 1:
        the_dict.update({keys[0]: value})
    else:
        if keys[0] not in the_dict:
            the_dict[keys[0]] = {}
        update_nested(the_dict[keys[0]], ':'.join(keys[1:]), value)

    return the_dict
