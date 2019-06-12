# coding=utf-8
from __future__ import absolute_import, print_function

import functools
import json

import numpy as np

from suanpan import path


class SPEncoder(json.JSONEncoder):
    NUMPY_INT = (
        np.int_,
        np.intc,
        np.intp,
        np.int8,
        np.int16,
        np.int32,
        np.int64,
        np.uint8,
        np.uint16,
        np.uint32,
        np.uint64,
    )
    NUMPY_FLOAT = (np.float_, np.float16, np.float32, np.float64)
    NUMPY_ARRAY = (np.ndarray,)

    def default(self, obj):  # pylint: disable=method-hidden
        if isinstance(obj, self.NUMPY_INT):
            return int(obj)
        if isinstance(obj, self.NUMPY_FLOAT):
            return float(obj)
        if isinstance(obj, self.NUMPY_ARRAY):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


_load = functools.partial(json.load, encoding="utf-8")
_loads = functools.partial(json.loads, encoding="utf-8")
_dump = functools.partial(json.dump, ensure_ascii=False, cls=SPEncoder)
_dumps = functools.partial(json.dumps, ensure_ascii=False, cls=SPEncoder)


def _loadf(file, *args, **kwargs):
    encoding = kwargs.pop("encoding", "utf-8")
    with open(file, "r", encoding=encoding) as _file:
        return _load(_file, *args, **kwargs)


def _dumpf(s, file, *args, **kwargs):
    encoding = kwargs.pop("encoding", "utf-8")
    path.safeMkdirsForFile(file)
    with open(file, "w", encoding=encoding) as _file:
        return _dump(s, _file, *args, **kwargs)


def load(file, *args, **kwargs):
    _l = _loadf if isinstance(file, str) else _load
    return _l(file, *args, **kwargs)


def dump(s, file, *args, **kwargs):
    _d = _dumpf if isinstance(file, str) else _dump
    return _d(s, file, *args, **kwargs)


loads = _loads
dumps = _dumps
