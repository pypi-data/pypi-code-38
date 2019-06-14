from typing import Any, Dict


def dict_deep_update(a: Dict[Any, Any], b: Dict[Any, Any]) -> None:
    """
    Recursively merges two dicts.

    It merges all keys with non-dict values from `b` into `a`. For keys in `a`
    and `b` with dict values, these sub-dicts are recursively merged.
    """
    for key in b:
        if not isinstance(b[key], dict) or not isinstance(a.get(key), dict):
            a[key] = b[key]
        else:
            dict_deep_update(a[key], b[key])
