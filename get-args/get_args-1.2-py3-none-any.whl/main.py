# -*- coding: utf-8 -*-
import os
import json
import random
import argparse
import json

import yaml
from dotenv import load_dotenv
try:
    import toml
except ImportError:
    pass


__version__ = '1.2'


class Arguments:

    def __init__(self, args=None):
        if args is None:
            args = {}

        self._not_exist = random.random()
        self._args = args

    def all_args(self):
        return self._args

    def update(self, args, overlap=True):
        for key in args:
            key = key.lower().replace('-', '_')

            if key in self._args and not overlap:
                continue
            self._args[key] = args[key]

    def get(self, name, default=None):
        name = name.lower().replace('-', '_')

        if name in self._args:
            return self._args[name]

        nlen = len(name)
        if name.endswith('_'):
            r = {}
            for key in self._args:
                if key.startswith(name):
                    r[key[nlen:]] = self._args[key]
            if not r:
                return default
            else:
                return r
        elif '_' in name:   # support nested dict
            value = self._get_recur(name, self._args)
            if value == self._not_exist:
                return default
            else:
                return value

        return default

    def _get_recur(self, name, d):
        for k in d:
            if k == name:
                return d[k]
            elif not name.startswith(k):
                continue
            elif not isinstance(d[k], dict):
                continue

            v = self._get_recur(name[len(k) + 1:], d[k])
            if v is not self._not_exist:
                return v

        return self._not_exist

    def set_default(self, name, default):
        name = name.lower().replace('-', '_')

        if name not in self._args or self._args[name] is None:
            self._args[name] = default

    def set(self, name, value):
        name = name.lower().replace('-', '_')

        if name.startswith('_'):
            self.__dict__[name] = value
        elif name.endswith('_'):
            for key in value:
                self._args[name + key] = value[key]
        else:
            self._args[name] = value

    def __setattr__(self, name, value):
        name = name.lower().replace('-', '_')

        self.set(name, value)

    def __getattr__(self, name):
        name = name.lower().replace('-', '_')

        if name.startswith('_'):
            return self.__dict__[name]
        else:
            return self.get(name)

    def __contains__(self, name):
        name = name.lower().replace('-', '_')

        return self.get(name, self._not_exist) != self._not_exist

    def __delattr__(self, name):
        name = name.lower().replace('-', '_')

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

    def __iter__(self):
        return iter(self._args)

    __setitem__ = __setattr__
    __getitem__ = __getattr__
    __delitem__ = __delattr__

    def __call__(self, name):
        return self.get(name.lower().replace('-', '_'))

    def __str__(self):
        return yaml.dump(self._args, indent=4, default_flow_style=False)


def add_args(parser: argparse.ArgumentParser,
             arguments: Arguments,
             meta_args: dict,
             arg_prefix: str = '',
             dest_prefix: str = ''):
    group = None
    if arg_prefix != '':
        __args = ['[' + meta_args.get('__title', arg_prefix[:-1].upper()) + ']', ]
        desc = meta_args.get('__desc', None)
        if desc:
            __args.append(f'desc: {desc}')

        group = parser.add_argument_group(*__args)
    else:
        if '__options' in meta_args:
            options = meta_args.pop('__options') or {}
            for option in options:
                parser.add_argument(option, **options[option])

    for key in meta_args:
        if key.startswith('__'):
            continue
        elif key.startswith('_'):
            sub_arg_prefix = '' if key.endswith('|') else arg_prefix + key[1:] + '_'
            sub_dest_prefix = dest_prefix + key[1:].rstrip('|') + '_'
            add_args(parser, arguments, meta_args[key], sub_arg_prefix, sub_dest_prefix)
            continue

        arg_keys = sorted(key.split(' '),  key=len)
        args = []
        for arg_key in arg_keys:
            if len(arg_key) > 1:
                if arg_key.endswith('|'):
                    args.append('--' + arg_key[:-1].replace('_', '-'))
                else:
                    args.append('--' + (arg_prefix + arg_key).replace('_', '-'))
            else:
                args.append('-' + arg_key)

        kw_args = meta_args.get(key)
        if not isinstance(kw_args, dict):
            if isinstance(kw_args, str) and ' ' in kw_args:
                kw_args = {'help': kw_args}
            elif kw_args in (True, False, ):
                kw_args = {'action': 'store_' + str(kw_args).lower()}
            elif kw_args is None:
                kw_args = {}
            elif isinstance(kw_args, list):
                kw_args = {'choices': kw_args, 'help': f'choices: {kw_args}'}
            else:
                kw_args = {'default': kw_args}
                if isinstance(kw_args['default'], int):
                    kw_args['type'] = int
        if 'dest' not in kw_args:
            kw_args['dest'] = (dest_prefix + arg_keys[-1]).lower().replace('-', '_').rstrip('|')

        if 'metavar' not in kw_args and kw_args.get('action', '').split('_')[-1] not in ('true', 'false', ):
            kw_args['metavar'] = arg_keys[-1].split('_')[-1].upper().rstrip('|')

        #print(arg_keys, kw_args)
        if group is None:
            parser.add_argument(*args, **kw_args)
        else:
            group.add_argument(*args, **kw_args)

    return parser


def advanced_env_var(value):
    value = value.strip()

    try:
        return {
            'true': True,
            'false': False,
            'null': None
        }[value]
    except KeyError:
        pass

    try:
        if value.startswith('0b'):
            return int(value, base=2)
        elif value.startswith('0o'):
            return int(value, base=8)
        elif value.startswith('0x'):
            return int(value, base=16)
        else:
            return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except:
        pass

    if value.startswith('!!'):
        _type, _value = value.split(' ', 1)

        try:
            if _type == '!!json':
                return json.loads(_value)
        except:
            pass

        try:
            return globals()[_type](_value)
        except:
            pass

    return value


def get_args(file_or_yaml, debug=False):
    # 1. load metadata config
    if os.path.isfile(file_or_yaml):
        with open(file_or_yaml) as f:
            args_conf = yaml.load(f.read(), Loader=yaml.FullLoader)
    elif '=' not in file_or_yaml:
        raise FileNotFoundError(file_or_yaml)
    else:
        args_conf = yaml.load(file_or_yaml, Loader=yaml.FullLoader)

    # 2. construct command line parser
    metadata = args_conf['metadata']
    arguments_cmd = Arguments()
    argparse_options = metadata['argparse'].get('options', {})

    parser = argparse.ArgumentParser(**argparse_options)
    add_args(parser, arguments_cmd, args_conf['args'])

    enable_env = False
    enable_conf = False

    if 'environment' in metadata and metadata['environment'].get('enable'):
        enable_env = True
        env_options = metadata['environment'].get('options', {})
        add_args(parser, arguments_cmd, env_options.get('argparse', {}), dest_prefix='env_file_')

    if 'configuration' in metadata and metadata['configuration'].get('enable'):
        enable_conf = True
        conf_options = metadata['configuration'].get('options', {})
        add_args(parser, arguments_cmd, conf_options.get('argparse', {}), dest_prefix='conf_file_')

    if '__version' in metadata:
        parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + str(metadata['__version']))

    # 3. parse args
    args = parser.parse_args()
    arguments_cmd.update(vars(args))
    #print(arguments_cmd)

    # 4. generate last values
    priority_cmd = metadata['argparse'].get('priority')

    if enable_env:
        priority_env = metadata['environment'].get('priority')
        override_cmd_env = metadata['environment'].get('override_cmd_env', True)

        env_files = metadata['environment']['options'].get('env_file', [])
        if arguments_cmd['env_file_'] is not None:
            env_files.extend(arguments_cmd['env_file_'].values())

        for env_file in env_files:
            if debug:
                print('-->', env_file)
            if env_file and os.path.isfile(env_file):
                load_dotenv(env_file, override=override_cmd_env)

        for key in arguments_cmd:
            key = key.upper()  # windows is not case sensitive, but linux is.
            if key not in os.environ:
                continue

            if debug:
                print(key, os.environ[key])

            if arguments_cmd[key] is None or priority_cmd < priority_env:
                arguments_cmd[key] = advanced_env_var(os.environ[key])
        if debug:
            print('\n^^^^ env ^^^^\n\n')

    if enable_conf:
        priority_conf = metadata['configuration'].get('priority')
        arguments_conf = Arguments()

        conf_files = metadata['configuration']['options'].get('conf_file', [])
        if arguments_cmd['conf_file_'] is not None:
            conf_files.extend(arguments_cmd['conf_file_'].values())

        for conf_file in conf_files:
            if debug:
                print('--->', conf_file)
            if not (conf_file and os.path.isfile(conf_file)):
                continue

            ext = conf_file.split('.')[-1]
            with open(conf_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if ext == 'json':
                arguments_conf.update(json.loads(content))
            elif ext in ('yaml', 'yml', ):
                arguments_conf.update(yaml.load(content, Loader=yaml.FullLoader))
            elif ext == 'toml':
                try:
                    arguments_conf.update(toml.load(content))
                except NameError:
                    raise Exception('toml conf file not supported, please install get_args[toml]')
            else:
                raise Exception(f'configuration format [{ext}] cannot load.')

        for key in arguments_cmd:
            if key not in arguments_conf:
                continue

            if debug:
                print(arguments_conf[key])

            if arguments_cmd[key] is None or priority_cmd < priority_conf:
                arguments_cmd[key] = arguments_conf[key]
        if debug:
            print('\n^^^^ conf ^^^^\n\n')

    if debug:
        print(arguments_cmd)

    return arguments_cmd


def main():
    get_args(os.getenv('GET_ARGS_FILE', './get_args.yml'), True)


if __name__ == '__main__':
    main()
