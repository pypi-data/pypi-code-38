#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals, print_function

import importlib
import os

import volkanic


def _linux_open(path):
    import subprocess
    subprocess.run(['xdg-open', path])


def _macos_open(path):
    import subprocess
    subprocess.run(['open', path])


def _windows_open(path):
    os.startfile(path)


def desktop_open(*paths):
    import platform
    osname = platform.system().lower()
    if osname == 'darwin':
        handler = _macos_open
    elif osname == 'windows':
        handler = _windows_open
    else:
        handler = _linux_open
    for path in paths:
        handler(path)


def where(name):
    mod = importlib.import_module(name)
    path = getattr(mod, '__file__', 'NotAvailable')
    dir_, filename = os.path.split(path)
    if filename.startswith('__init__.'):
        return dir_
    return path


def run_where(_, args):
    for arg in args:
        try:
            path = where(arg)
            print(arg, path, sep='\t')
        except ModuleNotFoundError:
            print(arg, 'ModuleNotFoundError', sep='\t')


def run_argv_debug(prog, _):
    import sys
    for ix, arg in enumerate(sys.argv):
        print(ix, repr(arg), sep='\t')
    print('\nprog:', repr(prog), sep='\t', file=sys.stderr)


def run_desktop_open(_, args):
    desktop_open(*args)


run_command_conf = volkanic.CommandConf.run

registry = volkanic.CommandRegistry({
    'volkanic.default:run_where': 'where',
    'volkanic.default:run_argv_debug': 'a',
    'volkanic.default:run_desktop_open': 'o',
    'volkanic.default:run_command_conf': 'runconf',
})
