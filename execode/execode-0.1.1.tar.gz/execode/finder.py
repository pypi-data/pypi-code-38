# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import sys
import contextlib
from importlib._bootstrap_external import PathFinder

PATH_MAP = {}

class Finder(PathFinder):

    @classmethod
    def find_spec(cls, fullname: str, path=None, target=None):
        path = PATH_MAP.get(fullname)
        if path is None:
            return None
        path = [path]
        return PathFinder.find_spec(fullname, path=path, target=target)

sys.meta_path.insert(0, Finder)

@contextlib.contextmanager
def use_path(**kwargs):
    PATH_MAP.update(kwargs)
    yield
    for k, v in kwargs.items():
        if PATH_MAP[k] == v:
            del PATH_MAP[k]
