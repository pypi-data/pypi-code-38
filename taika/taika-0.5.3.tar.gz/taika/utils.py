import contextlib
import json
import sys
from functools import partial

__all__ = ["add_syspath", "pretty_json"]

pretty_json = partial(json.dumps, indent=4)


@contextlib.contextmanager
def add_syspath(paths):
    for path in paths:
        sys.path.insert(0, path)

    yield

    for path in paths:
        sys.path.remove(path)
