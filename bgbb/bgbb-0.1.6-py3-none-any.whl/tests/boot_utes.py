from os import path
import sys
from importlib import reload


def add_path_(p, pos=0):
    p = path.abspath(path.expanduser(p))
    if p in sys.path:
        return
    if pos is None:
        sys.path.append(p)
    else:
        sys.path.insert(pos, p)


def add_path(*ps, pos=0):
    for p in ps:
        add_path_(p, pos=pos)
    return len(sys.path)
