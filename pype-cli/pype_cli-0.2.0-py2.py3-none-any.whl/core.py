# -*- coding: utf-8 -*-
"""Pype core initializer."""

from importlib import import_module
from os import environ, remove
from os.path import abspath, basename, dirname, expanduser, isfile, join
from re import sub
from shutil import copyfile
from sys import path as syspath

from colorama import Fore, Style

from pype.config_handler import PypeConfigHandler
from pype.exceptions import PypeException
from pype.type_plugin import Plugin
from pype.util.iotools import resolve_path
from pype.util.misc import get_from_json_or_default


class PypeCore():
    """Pype core initializer."""

    SHELL_INIT_PREFIX = '.pype-initfile'

    def __init__(self):
        """Public constructor."""
        self.__set_environment_variables()
        self.__config = PypeConfigHandler()
        # load all external plugins
        self.plugins = [
            Plugin(plugin)
            for plugin in get_from_json_or_default(
                self.__config.get_json(), 'plugins', [])
        ]
        # filter plugins not valid for current environment
        self.plugins = [plugin for plugin in self.plugins if plugin.active]
        # append internal plugins
        self.plugins.append(Plugin({
            'name': 'config',
            'users': []
        }))

    def __set_environment_variables(self):
        environ['LC_ALL'] = 'C.UTF-8'
        environ['LANG'] = 'C.UTF-8'

    def get_plugins(self):
        """Get list of configured plugins."""
        return self.plugins

    def get_config_json(self):
        """Get pype configuration as JSON object."""
        return self.__config.get_json()

    def set_config_json(self, json):
        """Set configuration from JSON object."""
        self.__config.set_json(json)

    def get_config_filepath(self):
        """Get absolute filepath to configuration JSON file."""
        return self.__config.get_filepath()

    def list_pypes(self):
        """Print list of pypes to console."""
        for plugin in self.plugins:
            print('{}{}– {}{}\n{}\n@ {}'.format(
                Style.BRIGHT, Fore.RED, plugin.name.upper(),
                Fore.LIGHTBLACK_EX, plugin.doc,
                'Built-in' if plugin.internal else plugin.abspath))
            for pype in plugin.pypes:
                print('{}{}{}{} – {}'.format(
                    Style.BRIGHT, Fore.RED, sub('_', '-', pype.name),
                    Style.RESET_ALL, pype.doc
                ))
            print()

    def create_pype_or_exit(self, pype_name, plugin, minimal):
        """Create a new pype inside the given plugin."""
        if plugin.internal:
            print('Creating internal pypes is not supported.')
            exit(1)
        # Normalize filename to be PEP8-conform
        target_name = sub('-', '_', sub(r'\.py$', '', pype_name))
        # Create absolute path
        target_file = join(plugin.abspath, target_name + '.py')
        if isfile(target_file):
            print('Pype already present')
            exit(1)
        # Depending on user input create a documented or simple template
        template_name = ('template_minimal.py' if minimal
                         else 'template.py')
        source_name = join(dirname(__file__), template_name)
        copyfile(source_name, target_file)
        print('Created new pype', target_file)
        return target_file

    def delete_pype(self, pype_name, plugin):
        """Delete pype from the given plugin."""
        if plugin.internal:
            print('Deleting internal pypes is not supported.')
            return
        source_name = sub('-', '_', sub(r'\.py$', '', pype_name))
        source_name = join(plugin.abspath, source_name + '.py')
        try:
            remove(source_name)
        except FileNotFoundError:
            print('No such pype')
            return
        print('Deleted pype', source_name)

    def get_abspath_to_pype(self, plugin, name):
        """Get absoulte path to pype Python script."""
        for pype in plugin.pypes:
            if name == pype.name:
                return pype.abspath
        return None

    def install_to_shell(self, shell_config):
        """Install current configuration to shell."""
        config_json = self.__config.get_json()
        init_file = self.get_core_config('init_file',
                                         shell_config['init_file'])
        shell_command = self.get_core_config('shell_command', 'pype')
        print('Using shell command', shell_command)
        aliases = get_from_json_or_default(config_json, 'aliases', [])
        print('Writing init-file', init_file)
        with open(resolve_path(init_file), 'w+') as ifile:
            # Write pype sourcing command
            ifile.write('if [ ! -z "$( command -v ' +
                        shell_command + ' )" ]; then\n')
            ifile.write('\t' + shell_config['source_cmd'] + '\n')
            # Write configured aliases
            for alias in aliases:
                alias_cmd = '\talias {}="{}"\n'.format(
                    alias['alias'], alias['command'])
                ifile.write(alias_cmd)
            ifile.write('fi\n')
        # Only add source link to target file if not present yet
        target_file = shell_config.get('target_file', None)
        if not target_file:
            return
        try:
            rc_file_content = open(
                target_file, 'r').readlines()
        except FileNotFoundError:
            rc_file_content = []
        already_present = [line for line in rc_file_content
                           if basename(init_file) in line]
        if not already_present:
            print('Adding init-file sourcing to', target_file)
            with open(target_file, 'a+') as rc_file_handle:
                rc_file_handle.write('. ' + init_file + '\n')

    def uninstall_from_shell(self, shell_config):
        """Remove current configuration from shell."""
        if isfile(shell_config['init_file']):
            remove(shell_config['init_file'])
        if not isfile(shell_config['target_file']):
            return
        with open(shell_config['target_file'], 'r') as f:
            lines = f.readlines()
        with open(shell_config['target_file'], 'w') as f:
            for line in lines:
                if self.SHELL_INIT_PREFIX not in line.strip('\n'):
                    f.write(line)

    def register_alias(self, ctx, extra_args, alias):
        """Register a new alias."""
        if not alias:
            return
        cmd_line = ctx.command_path + ' ' + ' '.join(extra_args)
        alias_cmd = '{}="{}"'.format(alias, cmd_line.strip())
        # store to internal config
        config_json = self.__config.get_json()
        if not config_json.get('aliases', None):
            config_json['aliases'] = []
        if self._alias_present(config_json, alias):
            print('Alias already registered.')
            return
        config_json.get('aliases').append({
            'alias': alias,
            'command': cmd_line
        })
        self.__config.set_json(config_json)
        # update install script
        self.install_to_shell(self.get_shell_config())
        print('Installed alias "{}"'.format(alias_cmd))

    def unregister_alias(self, alias):
        """Unregister the provided alias."""
        if not alias:
            return
        # store to internal config
        config_json = self.__config.get_json()
        if not config_json.get('aliases', None):
            print('No aliases registered.')
            return
        if not self._alias_present(config_json, alias):
            print('Alias not registered.')
            return
        for obj in enumerate(config_json['aliases']):
            if obj[1]['alias'] != alias:
                continue
            del config_json['aliases'][obj[0]]
        self.__config.set_json(config_json)
        # update install script
        self.install_to_shell(self.get_shell_config())
        print('Uninstalled alias "{}"'.format(alias))

    def _alias_present(self, config_json, alias):
        return any(
            [existing_alias for existing_alias in config_json.get('aliases')
             if existing_alias['alias'] == alias])

    def get_core_config(self, key, default=None):
        """Return a key from the core configuration of the config file."""
        return get_from_json_or_default(
            self.get_config_json(), 'core_config.' + key, default)

    def get_shell_config(self):
        """Construct a shell configuration by guessing the running shell."""
        shell_command = self.get_core_config('shell_command', 'pype')
        supported_shells = {
            'bash': {
                'init_file':
                join(expanduser('~'), self.SHELL_INIT_PREFIX + '-bash'),
                'source_cmd': 'eval "$(_' + shell_command.upper() +
                '_COMPLETE=source ' + shell_command + ')"'
            },
            'zsh': {
                'init_file': join(expanduser('~'),
                                  self.SHELL_INIT_PREFIX + '-zsh'),
                'source_cmd': 'eval "$(_' + shell_command.upper() +
                '_COMPLETE=source_zsh ' + shell_command + ')"'
            }
        }
        shell = basename(environ.get('SHELL', None))
        if not any(
            [supported for supported in supported_shells
             if shell == supported]
        ):
            print('Unsupported shell "{}".'.format(shell))
            return None
        return supported_shells[shell]


def load_module(name, path):
    """Try to import the module at the provided path using classloader."""
    syspath.append(abspath(path))
    try:
        return import_module(name)
    except ModuleNotFoundError as e:  # noqa: F821
        raise PypeException(e)


def get_pype_basepath():
    """Get directory filename of this pype installation."""
    return dirname(dirname(__file__))
