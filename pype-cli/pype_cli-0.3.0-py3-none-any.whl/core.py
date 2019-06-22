# -*- coding: utf-8 -*-
"""Pype core initializer."""

from importlib import import_module
from os import environ, remove, sep
from os.path import abspath, dirname, isfile, join
from re import sub
from shutil import copyfile
from sys import argv, path as syspath

from colorama import Fore, Style

from pype.config_handler import PypeConfigHandler
from pype.constants import ENV_CONFIG_FILE
from pype.exceptions import PypeException
from pype.type_plugin import Plugin
from pype.util.cli import print_error, print_success, print_warning
from pype.util.iotools import resolve_path
from pype.util.misc import get_from_json_or_default

from tabulate import tabulate


class PypeCore():
    """Pype core initializer."""

    def __init__(self):
        """Public constructor."""
        self.__set_environment_variables()
        self.__config = PypeConfigHandler()
        # load all external plugins
        self.plugins = [
            Plugin(plugin, self.get_config_filepath())
            for plugin in get_from_json_or_default(
                self.__config.get_json(), 'plugins', [])
        ]
        # filter plugins not valid for current environment
        self.plugins = [plugin for plugin in self.plugins if plugin.active]
        # append internal plugins
        self.plugins.append(Plugin({
            'name': 'config',
            'users': []
        }, self.get_config_filepath()))

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
            print('{}{}PLUGIN: {}{}\n{}\n@ {}'.format(
                Style.BRIGHT, Fore.BLUE, plugin.name.upper(),
                Fore.LIGHTBLACK_EX, plugin.doc,
                'Built-in' if plugin.internal else plugin.abspath))
            print('{}{}– PYPES:'.format(Style.BRIGHT, Fore.BLUE))
            for pype in plugin.pypes:
                print('  {}{}{}{} – {}'.format(
                    Style.BRIGHT, Fore.BLUE, sub('_', '-', pype.name),
                    Style.RESET_ALL, pype.doc
                ))
            print()

    def list_aliases(self):
        """Print list of aliases to console."""
        aliases = self.get_config_json().get('aliases')
        sorted_alias_keys = sorted([alias['alias'] for alias in aliases])
        alias_table = []

        def find_alias(aliases, key):
            for alias in aliases:
                if key == alias['alias']:
                    return alias

        for alias in sorted_alias_keys:
            alias_table.append([
                '{}{}{}'.format(Style.BRIGHT, Fore.BLUE, alias),
                Style.RESET_ALL + '=',
                '{}{}{}'.format(Style.BRIGHT, Fore.LIGHTBLACK_EX,
                                find_alias(aliases, alias)['command'])
            ])
        print(tabulate(alias_table, tablefmt='plain'))

    def create_pype_or_exit(self, pype_name, plugin, minimal):
        """Create a new pype inside the given plugin."""
        if plugin.internal:
            print_error('Creating internal pypes is not supported.')
            exit(1)
        # Normalize filename to be PEP8-conform
        target_name = sub('-', '_', sub(r'\.py$', '', pype_name))
        # Create absolute path
        target_file = join(plugin.abspath, target_name + '.py')
        if isfile(target_file):
            print_warning('Pype already present')
            exit(1)
        # Depending on user input create a documented or simple template
        template_name = ('template_minimal.py' if minimal
                         else 'template.py')
        source_name = join(dirname(__file__), template_name)
        copyfile(source_name, target_file)
        print_success('Created new pype ' + target_file)
        return target_file

    def delete_pype(self, pype_name, plugin):
        """Delete pype from the given plugin."""
        if plugin.internal:
            print_error('Deleting internal pypes is not supported.')
            return
        source_name = sub('-', '_', sub(r'\.py$', '', pype_name))
        source_name = join(plugin.abspath, source_name + '.py')
        try:
            remove(source_name)
        except FileNotFoundError:
            print_error('No such pype')
            return
        print_success('Deleted pype', source_name)

    def get_abspath_to_pype(self, plugin, name):
        """Get absoulte path to pype Python script."""
        for pype in plugin.pypes:
            if name == pype.name:
                return pype.abspath
        return None

    SHELL_INIT_PREFIX = '.pype-initfile-'
    SUPPORTED_RC_FILES = [
        resolve_path('~/.bashrc'),
        resolve_path('~/.bash_profile'),
        resolve_path('~/.zshrc')
    ]

    def __write_init_file(self, init_file, shell_command, aliases,
                          silent=False):
        target_file = resolve_path('~/' + self.SHELL_INIT_PREFIX + init_file)
        self.__print_if('Writing init-file ' + target_file, silent)
        with open(resolve_path(target_file), 'w+') as ifile:
            # Write pype sourcing command
            ifile.write('if [ ! -z "$( command -v '
                        + shell_command
                        + ' )" ]; then\n')
            source_cmd = 'eval "$(_{}_COMPLETE=source{} {})"'.format(
                shell_command.upper(),
                '_zsh' if init_file == 'zsh' else '',
                shell_command
            )
            ifile.write('\t' + source_cmd + '\n')
            # Write configured aliases
            for alias in aliases:
                alias_cmd = '\talias {}="{}"\n'.format(
                    alias['alias'], alias['command'])
                ifile.write(alias_cmd)
            # Close if
            ifile.write('fi\n')

    def __remove_init_file(self, init_file, silent):
        target_file = resolve_path('~/' + self.SHELL_INIT_PREFIX + init_file)
        self.__print_if('Removing init-file ' + target_file, silent)
        try:
            remove(target_file)
        except FileNotFoundError:
            pass  # Silent ignore to make function idempotent

    def install_to_shell(self, silent=False):
        """Install shell features."""
        # Clean up first
        self.uninstall_from_shell(silent)
        print_success('Successfully cleaned up existing configurations')
        # Write new init-files
        config_json = self.__config.get_json()
        shell_command = self.get_core_config('shell_command', 'pype')
        aliases = get_from_json_or_default(config_json, 'aliases', [])
        self.__print_if('Using shell command "{}"'.format(shell_command),
                        silent)
        self.__write_init_file('bsh', shell_command, aliases, silent)
        self.__write_init_file('zsh', shell_command, aliases, silent)
        self.__print_if('Add link to init-file in rc-files if present', silent)
        for file in self.SUPPORTED_RC_FILES:
            if not isfile(file):
                continue
            self.__print_if(' - "{}"'.format(file), silent)
            # Append link to init-file and set config file
            file_handle = open(file, 'a+')
            init_file = '~/' + self.SHELL_INIT_PREFIX
            init_file = (init_file + 'zsh' if 'zshrc' in file
                         else init_file + 'bsh')
            file_handle.write('export {}="{}" # {}\n'.format(
                ENV_CONFIG_FILE,
                resolve_path(self.get_config_filepath()),
                self.SHELL_INIT_PREFIX
            ))
            file_handle.write('. ' + init_file + '\n')
            file_handle.close()
        print_success('Successfully written init-files')

    def uninstall_from_shell(self, silent=False):
        """Uninstall shell features."""
        # Remove init files
        self.__remove_init_file('bsh', silent)
        self.__remove_init_file('zsh', silent)
        self.__print_if('Remove link to init-file from rc-files if present',
                        silent)
        for file in self.SUPPORTED_RC_FILES:
            if not isfile(file):
                continue
            file_handle = open(file, 'r')
            content = file_handle.readlines()
            file_handle.close()
            # Don't rewrite if rc file does not link to initfile
            if not any(list(filter(
                    lambda x: self.SHELL_INIT_PREFIX in x, content))):
                continue
            # Delete initfile-links from rc file
            self.__print_if(' - "{}"'.format(file), silent)
            file_handle = open(file, 'w')
            [file_handle.write(cn)
             for cn in content if self.SHELL_INIT_PREFIX not in cn]
            file_handle.close()

    def register_alias(self, ctx):
        """Register a new alias."""
        alias = ctx.parent.register_alias
        # Combine the current context's command path with remaining CL-args
        cmd_path = ctx.command_path.split(' ')
        cmd_path_last = cmd_path[-1]
        found_entry = False
        for arg in argv:
            if found_entry:
                cmd_path.append(arg)
            if arg.strip() == cmd_path_last:
                found_entry = True
        cmd_line = ' '.join(cmd_path)
        if not alias:
            return
        alias_cmd = '{}="{}"'.format(alias, cmd_line.strip())
        # store to internal config
        config_json = self.__config.get_json()
        if not config_json.get('aliases', None):
            config_json['aliases'] = []
        if self._alias_present(config_json, alias):
            print_warning('Alias already registered.')
            return
        config_json.get('aliases').append({
            'alias': alias,
            'command': cmd_line
        })
        print_success('Installed alias: {}'.format(alias_cmd))
        self.__config.set_json(config_json)
        # update install script
        self.install_to_shell(silent=True)

    def unregister_alias(self, alias):
        """Unregister the provided alias."""
        if not alias:
            return
        # store to internal config
        config_json = self.__config.get_json()
        if not config_json.get('aliases', None):
            print_warning('No aliases registered.')
            return
        if not self._alias_present(config_json, alias):
            print_warning('Alias not registered.')
            return
        for obj in enumerate(config_json['aliases']):
            if obj[1]['alias'] != alias:
                continue
            del config_json['aliases'][obj[0]]
        self.__config.set_json(config_json)
        # update install script
        print_success('Uninstalled alias "{}"'.format(alias))
        self.install_to_shell(silent=True)

    def _alias_present(self, config_json, alias):
        return any(
            [existing_alias for existing_alias in config_json.get('aliases')
             if existing_alias['alias'] == alias])

    def __print_if(self, message, silent):
        if not silent:
            print(message)

    def get_core_config(self, key, default=None):
        """Return a key from the core configuration of the config file."""
        return get_from_json_or_default(
            self.get_config_json(), 'core_config.' + key, default)


def fname_to_name(fname):
    """Use the filename as command name."""
    return sub('_', '-', fname[:-3].split(sep)[-1])


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


def print_context_help(ctx, level=0):
    """Print help page for current context with some slight improvements."""
    default_help = ctx.get_help()
    if level == 1:
        print(sub('Commands:', 'Plugins:', default_help))
    elif level == 2:
        print(sub('Commands:', 'Pypes:', default_help))
    else:
        print(default_help)
