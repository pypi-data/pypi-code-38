# -*- coding: utf-8 -*-
# Copyright (c) 2019 Dzmitry Maliuzhenets; MIT License
"""The module contains various utilities."""


def replace_from__word(d: dict):
    """Replace recursive keys in the object from_ to from."""
    res = {}
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [replace_from__word(v) for v in d]

    for key, value in d.items():
        if key == 'from_':
            res['from'] = replace_from__word(d['from_'])
        else:
            res[key] = replace_from__word(d[key])
    return res


def replace_from_word(d: dict) -> dict:
    """Replace recursive keys in the object from to from_."""
    res = {}
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [replace_from_word(v) for v in d]

    for key, value in d.items():
        if key == 'from':
            res['from_'] = replace_from_word(d['from'])
        else:
            res[key] = replace_from_word(d[key])
    return res


def is_str_int_float_bool(value):
    """Is value str, int, float, bool."""
    return isinstance(value, (int, str, float))


def is_ends_with_underscore(value: str):
    """Does value end with underscore."""
    if value == "":
        return False
    else:
        return value[-1] == '_'
