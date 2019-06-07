#!/usr/bin/env python

__all__ = ["root_path", "data_path"]
_data_path = None


def root_path() -> str:
    from os.path import realpath, join
    return realpath(join(__file__, "../../"))


def data_path() -> str:
    global _data_path
    if _data_path is None:
        from os.path import join
        _data_path = join(root_path(), "data")
    return _data_path


def set_data_path(dp: str):
    global _data_path
    _data_path = dp

