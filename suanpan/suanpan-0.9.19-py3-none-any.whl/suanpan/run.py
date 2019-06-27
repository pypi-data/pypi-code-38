# coding=utf-8
from __future__ import absolute_import, print_function

import argparse
import contextlib
import importlib
import os
import sys


def load(name):
    try:
        module_name, component_name = name.replace(os.sep, ".").rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, component_name)
    except Exception as e:
        print("Load component error!", file=sys.stderr, flush=True)
        raise e


def run(component, *args, **kwargs):
    if isinstance(component, str):
        component = load(component)
    with env(**kwargs.pop("env", {})):
        return component(*args, **kwargs)


@contextlib.contextmanager
def env(**kwargs):
    old = {key: os.environ.get(key) for key in kwargs}
    os.environ.update(kwargs)
    yield os.environ
    os.environ.update(old)


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("component")
    _args, _rest = parser.parse_known_args()

    sys.argv = sys.argv[:1]
    return run(_args.component, *_rest)


if __name__ == "__main__":
    cli()
