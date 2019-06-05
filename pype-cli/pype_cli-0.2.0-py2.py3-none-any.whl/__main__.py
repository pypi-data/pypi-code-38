#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pype main entry point."""

import subprocess
from os import environ, path
from re import sub
from sys import executable
from sys import path as syspath

import click

from colorama import Fore, init

from pype.core import PypeCore
from pype.exceptions import PypeException
from pype.util.iotools import open_with_default


@click.group(
    invoke_without_command=True,
    context_settings=dict(help_option_names=['-h', '--help']),
    help='PYPE - A command-line tool for command-line tools'
)
@click.option('--list-pypes', '-l', is_flag=True,
              help='Print all available pypes')
@click.option('--open-config', '-o', is_flag=True,
              help='Open config file in default editor')
@click.option('--register-alias', '-r', metavar='ALIAS',
              help='Register alias for following pype')
@click.option('--unregister-alias', '-u', metavar='ALIAS',
              help='Register alias for following pype')
@click.pass_context
def main(ctx, list_pypes, open_config, register_alias, unregister_alias):
    """Pype main entry point."""
    if not _process_alias_configuration(
            ctx, list_pypes, open_config, register_alias, unregister_alias):
        print(ctx.get_help())
        return
    if open_config:
        open_with_default(PYPE_CORE.get_config_filepath())
    elif list_pypes:
        PYPE_CORE.list_pypes()
        return
    elif unregister_alias:
        PYPE_CORE.unregister_alias(unregister_alias)
        return
    elif ctx.invoked_subcommand is None:
        _print_red('No pype selected.')
        print(ctx.get_help())


def _process_alias_configuration(
        ctx, list_pypes, open_config, register_alias, unregister_alias):
    if register_alias and unregister_alias:
        _print_red('Options -r and -u cannot be combined.')
        return False
    other_options = open_config or list_pypes
    if register_alias and other_options:
        _print_red('Option -r cannot be combined with other options.')
        return False
    if unregister_alias and other_options:
        _print_red('Option -u cannot be combined with other options.')
        return False
    # piggy-back context
    ctx.register_alias = register_alias
    return True


def _bind_plugin(name, plugin):
    @click.option('--create-pype', '-c',
                  help='Create new pype with provided name')
    @click.option('--minimal', '-m', is_flag=True,
                  help='Use a minimal template with less boilerplate '
                  + '(only used along with "-c" option')
    @click.option('--edit', '-e', is_flag=True,
                  help='Open new pype immediatly for editing '
                  + '(only used along with "-c" option')
    @click.option('--delete-pype', '-d',
                  help='Deletes pype for provided name')
    @click.option('--open-pype', '-o',
                  help='Open selected pype in default editor')
    @click.pass_context
    def _plugin_bind_function(
            ctx, create_pype, minimal, edit, delete_pype, open_pype):
        if (minimal or edit) and not create_pype:
            _print_red(
                '"-m" and "-e" can only be used with "-c" option.')
            print(ctx.get_help())
            return
        toggle_invoked = False
        if create_pype:  # Handle creation of pypes
            created_pype_abspath = PYPE_CORE.create_pype_or_exit(
                create_pype, plugin, minimal)
            toggle_invoked = True
        if delete_pype:  # Handle deletion of pypes
            PYPE_CORE.delete_pype(delete_pype, plugin)
            toggle_invoked = True
        if open_pype or edit:  # Handle opening existing or new pypes
            if plugin.internal:
                _print_red('Opening internal pypes is not supported.')
                return
            # Resolve either an existing or a newly created pype
            pype_abspath = (PYPE_CORE.get_abspath_to_pype(
                plugin, sub('-', '_', open_pype))
                if open_pype else created_pype_abspath)
            if not pype_abspath:
                _print_red(
                    'Pype "{}" could not be found.'.format(open_pype))
                return
            open_with_default(pype_abspath)
            toggle_invoked = True
        # Handle case that no toggles were used and no commands selected
        if not toggle_invoked and not ctx.invoked_subcommand:
            print(ctx.get_help())
    _plugin_bind_function.__name__ = _normalize_command_name(name)
    return _plugin_bind_function


def _bind_pype(name, plugin, pype):
    @click.pass_context
    @click.argument('extra_args', nargs=-1, type=click.UNPROCESSED)
    @click.option('--help', '-h', is_flag=True)
    def _pype_bind_function(ctx, extra_args, help):  # noqa: A002
        if ctx.parent.parent.register_alias:
            PYPE_CORE.register_alias(
                ctx, extra_args, ctx.parent.parent.register_alias)
            return
        # else spawn selected pype
        syspath.append(path.dirname(plugin.abspath))
        sub_environment = environ.copy()
        sub_environment['PYTHONPATH'] = ':'.join(syspath)
        extra_args = ['--help'] if help else list(ctx.params['extra_args'])
        command = [executable, '-m', plugin.name +
                   '.' + pype.name] + extra_args
        try:
            subprocess.run(command, env=sub_environment)
        except KeyboardInterrupt:
            pass  # Be silent if keyboard interrupt was catched
    _pype_bind_function.__name__ = _normalize_command_name(name)
    return _pype_bind_function


def _normalize_command_name(name):
    return sub('_', '-', name)


def _print_red(message):
    print(Fore.RED + message)


init(autoreset=True)
try:
    PYPE_CORE = PypeCore()
except PypeException as err:
    print(err)
    exit(1)

# Go through all configured plugins and their pypes and setup command groups
for plugin in PYPE_CORE.get_plugins():
    _plugin_bind_function = _bind_plugin(plugin.name, plugin)
    plugin_click_group = main.group(
        invoke_without_command=True, help=plugin.doc)(
            _plugin_bind_function)
    ctx_settings = dict(
        ignore_unknown_options=True,
        allow_extra_args=True
    )
    for pype in plugin.pypes:
        plugin_click_group.command(
            context_settings=ctx_settings, help=pype.doc)(
            _bind_pype(pype.name, plugin, pype))


if __name__ == '__main__':
    main()
