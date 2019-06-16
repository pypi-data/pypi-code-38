#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals

import contextlib
import importlib
import os
import sys


def subattr(obj, *names):
    for x in names:
        obj = getattr(obj, x)
    return obj


def load_symbol(symbolpath):
    parts = symbolpath.split(':', 1)
    symbol = importlib.import_module(parts.pop(0))
    if parts:
        symbol = subattr(symbol, *parts[0].split('.'))
    return symbol


def load_variables(*contexts):
    import re
    scope = {}
    for ctx in contexts:
        if not isinstance(ctx, dict):
            ctx = {re.split('[.:]', x)[-1]: x for x in ctx}
        for key, val in ctx.items():
            scope[key] = load_symbol(val)
    return scope


@contextlib.contextmanager
def remember_cwd():
    curdir = os.getcwd()
    try:
        yield
    finally:
        os.chdir(curdir)


class CommandNotFound(KeyError):
    pass


class CommandConf(object):
    def __init__(self, commands):
        self.commands = dict(commands)
        self.commands.setdefault('_global', {})

    @classmethod
    def from_yaml(cls, name, default_dir=None):
        import yaml
        ext = os.path.splitext(name)[1].lower()
        if ext not in ['.yml', '.yaml']:
            name += '.yml'
        path = cls._locate(name, default_dir)
        return cls(yaml.load(open(path)))

    @classmethod
    def from_json(cls, name, default_dir=None):
        import json
        ext = os.path.splitext(name)[1].lower()
        if ext != '.json':
            name += '.json'
        path = cls._locate(name, default_dir)
        return cls(json.load(open(path)))

    @staticmethod
    def _locate(path, default_dir):
        paths = [path]
        if default_dir is not None:
            paths.append(os.path.join(default_dir, path))
        for path in paths:
            if os.path.isfile(path):
                return path
        raise FileNotFoundError(path)

    @staticmethod
    def _execute(params):
        # only 'module' is a must-have
        prefix = params.get('prefix', '')
        module = prefix + params['module']
        call = params.get('call', 'run')
        args = params.get('args', [])
        kwargs = params.get('kwargs', {})
        if not isinstance(args, (list, tuple)):
            args = [args]
        m = importlib.import_module(module)
        subattr(m, *call.split('.'))(*args, **kwargs)

    def __call__(self, cmd):
        if cmd not in self.commands:
            raise CommandNotFound(str(cmd))
        params = dict(self.commands['_global'])
        params.update(self.commands[cmd])
        with remember_cwd():
            os.chdir(params.get('cd', '.'))
            self._execute(params)

    @classmethod
    def run(cls, prog=None, args=None, default_dir=None, **kwargs):
        from argparse import ArgumentParser
        kwargs.setdefault('description', 'volkanic command-conf runner')
        parser = ArgumentParser(prog=prog, **kwargs)
        parser.add_argument('name', help='a YAML file')
        parser.add_argument(
            'key', nargs='?', default='default',
            help='a top-level key in the YAML file',
        )
        ns = parser.parse_args(args=args)
        cconf = cls.from_yaml(ns.name, default_dir)
        cconf(ns.key)


class CommandRegistry(object):
    def __init__(self, entries):
        self.entries = entries
        self.commands = {v: k for k, v in entries.items()}

    def show_commands(self):
        print('availabe commands:')
        for cmd in sorted(self.commands):
            print('-', cmd)

    def __call__(self, argv=None):
        if argv is None:
            argv = sys.argv
        else:
            argv = list(argv)

        try:
            dotpath = self.commands[argv[1]]
        except LookupError:
            self.show_commands()
            sys.exit(1)

        # intended use: argparse.ArgumentParser(prog=prog)
        prog = '{} {}'.format(os.path.basename(argv[0]), argv[1])

        if ':' not in dotpath:
            dotpath += ':run'
        return load_symbol(dotpath)(prog, argv[2:])
