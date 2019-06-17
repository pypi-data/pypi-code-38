"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:

"""
import json
from functools import wraps
import time


class Ddict(dict):
    """
    Dict object where value by key and key by value is possible
    """
    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            return list(self.keys())[list(self.values()).index(item)]


class _DictEncoder(json.JSONEncoder):
    def encode(self, dict_):
        def hint_tuples(item):
            if isinstance(item, tuple):
                return {"__tuple__": True, "items": tuple(hint_tuples(e) for e in item)}
            if isinstance(item, list):
                return [hint_tuples(e) for e in item]
            if isinstance(item, dict):
                return {key: hint_tuples(value) for key, value in item.items()}
            else:
                return item

        return super().encode(hint_tuples(dict_))


def _hinted_tuple_hook(obj):
    if "__tuple__" in obj:
        return tuple(obj["items"])
    else:
        return obj


def dump_dict_to_json(dict_):
    enc = _DictEncoder()
    return enc.encode(dict_)


def load_dict_from_json(json_):
    return json.loads(json_, object_hook=_hinted_tuple_hook)


def time_func(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print(f'func:{f.__name__} took: {te - ts} sec')
        return result
    return wrap
