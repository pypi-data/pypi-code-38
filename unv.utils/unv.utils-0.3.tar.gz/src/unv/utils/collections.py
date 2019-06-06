def update_dict_recur(
        original: dict, from_dict: dict, copy: bool = False) -> dict:
    """Update dict recursively.

    >>> original = {0: 'zero', 1: {1: 'one'}, 2: {2: {3: 3}}, 6: 'item'}
    >>> update_with = {0: 1, 1: {1: 'hello'}, 2: {2: {4: 4}}, 5: 1}
    >>> result = update_dict_recur(original, update_with)
    >>> result is original  # original dict not copied
    True
    >>> result[0]  # was 'one'
    1
    >>> result[1]  # updated inside, was 'one'
    {1: 'hello'}
    >>> result[2][2]  # added {4: 4} from `update_with`
    {3: 3, 4: 4}
    >>> result[5]  # added new item to dict
    1
    >>> result[6]  # same
    'item'
    >>> original = {1: 'one', 2: {2: 2}}
    >>> update_with = {1: 1, 2: {2: 'two'}}
    >>> result = update_dict_recur(original, update_with, copy=True)
    >>> original is not result
    True
    >>> result[2][2]
    'two'
    """
    if copy:
        original = original.copy()
    for key, value in from_dict.items():
        if isinstance(value, dict) and key in original:
            original[key] = update_dict_recur(
                original.get(key, {}), value, copy)
        else:
            original[key] = value
    return original
