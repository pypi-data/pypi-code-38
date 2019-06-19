# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import path


def _loadf(file, *args, **kwargs):
    encoding = kwargs.pop("encoding", "utf-8")
    with open(file, "r", encoding=encoding) as _file:
        return _load(_file, *args, **kwargs)


def _dumpf(s, file, *args, **kwargs):
    encoding = kwargs.pop("encoding", "utf-8")
    path.safeMkdirsForFile(file)
    with open(file, "w", encoding=encoding) as _file:
        return _dump(s, _file, *args, **kwargs)


def _load(file, *args, **kwargs):  # pylint: disable=unused-argument
    return file.read().strip()


def _dump(s, file, *args, **kwargs):  # pylint: disable=unused-argument
    file.write(s)


def load(file, *args, **kwargs):
    _l = _loadf if isinstance(file, str) else _load
    return _l(file, *args, **kwargs)


def dump(s, file, *args, **kwargs):
    _d = _dumpf if isinstance(file, str) else _dump
    return _d(s, file, *args, **kwargs)
