# -*- coding: utf-8 -*-
import msgpack


def flatten(nested_iterable):
    return [item for sublist in nested_iterable for item in sublist]


def is_none_ish(val):
    return val is None or val in [(), [], {}]


def filter_empty_values_from_dict(dict_):
    return {k: v for k, v in dict_.items() if not is_none_ish(v)}


def msgpack_dict(dict_):
    return msgpack.packb(dict_)
