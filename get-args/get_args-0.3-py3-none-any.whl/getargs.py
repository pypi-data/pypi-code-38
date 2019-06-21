# -*- coding: utf-8 -*-
import os
import json
import argparse

import yaml
import dotenv


def pretty(d, indent=0):
   for key, value in d.items():
      print('  ' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('  ' * (indent+1) + str(value))


class Arguments:

    def __init__(self, args=None):
        if args is None:
            args = {}

        self._args = args

    def update(self, args, overlap=True):
        for key in args:
            if key in self._args and not overlap:
                continue
            self._args[key] = args[key]

    def _get(self, name):
        name = name.lower()

        if name in self._args:
            return self._args[name]

        nlen = len(name)
        if name.endswith('_'):
            r = {}
            for key in self._args:
                if key.startswith(name):
                    r[key[nlen:]] = self._args[key]
            return r

        return None

    def __setattr__(self, name, value):
        if name.startswith('_'):
            self.__dict__[name] = value
        elif name.endswith('_'):
            for key in value:
                self._args[name + key] = value[key]
        else:
            self._args[name] = value

    def __getattr__(self, name):
        if name.startswith('_'):
            return self.__dict__[name]
        else:
            return self._get(name)

    def __delattr__(self, name):
        if name.startswith('_'):
            del self.__dict__[name]
            return

        if name in self._args:
            del self._args[name]
            return

        if name.endswith('_'):
            for key in list(self._args):
                if key.startswith(name):
                    del self._args[key]
            return

    __setitem__ = __setattr__
    __getitem__ = __getattr__
    __delitem__ = __delattr__

    def __call__(self, key):
        return self._get(key)

    def __str__(self):
        return yaml.dump(self._args, indent=4, default_flow_style=False)


def add_args(parser: argparse.ArgumentParser,
             args: dict,
             prefix: str):

    group = None
    if prefix != '':
        __args = ['[' + args.get('__title', prefix[:-1].upper()) + ']', ]
        desc = args.get('__desc', None)
        if desc:
            __args.append(f'desc: {desc}')

        group = parser.add_argument_group(*__args)

    for key in args:
        if key.startswith('__'):
            continue
        elif key.startswith('_'):
            sub_prefix = '' if key.endswith('|') else (prefix + key[1:] + '_')
            add_args(parser, args[key], sub_prefix)
            continue

        arg_keys = sorted(key.split(' '),  key=len)
        for i, arg_key in enumerate(arg_keys):
            if len(arg_key) > 1:
                arg_keys[i] = ('--' + prefix + arg_key).replace('_', '-')
            else:
                arg_keys[i] = ('-' + arg_key).replace('_', '-')

        kw_args = args.get(key)
        if not isinstance(kw_args, dict):
            if isinstance(kw_args, str) and ' ' in kw_args:
                kw_args = {'help': kw_args}
            elif kw_args in (True, False, ):
                kw_args = {'action': 'store_' + str(kw_args).lower()}
            elif kw_args is None:
                kw_args = {}
            else:
                kw_args = {'default': kw_args}
                if isinstance(kw_args['default'], int):
                    kw_args['type'] = int

        if 'metavar' not in kw_args and kw_args.get('action', '').split('_')[-1] not in ('true', 'false', ):
            kw_args['metavar'] = arg_keys[-1].split('-')[-1].upper()

        #print(arg_keys, kw_args)
        if group is None:
            parser.add_argument(*arg_keys, **kw_args)
        else:
            group.add_argument(*arg_keys, **kw_args)

    return parser


def getargs(file):
    with open(file) as f:
        meta_args = yaml.load(f.read())
        #pretty(meta_args, 2)

    metadata = meta_args['metadata']

    if 'argparse' in metadata and metadata['argparse'].get('enable'):
        options = metadata['argparse'].get('options', {})
        parser = argparse.ArgumentParser(**options)

        args = meta_args['args']
        parser = add_args(parser, args, '')
        args = parser.parse_args()
        print('----')
        print(Arguments(vars(args)))

    if 'environment' in metadata and metadata['environment'].get('enable'):
        env_args = metadata['environment'].get('options', {})

    if 'configuation' in metadata and metadata['configuation'].get('enable'):
        conf_args = metadata['configuation'].get('options', {})


if __name__ == '__main__':
    getargs('./example.yml')
