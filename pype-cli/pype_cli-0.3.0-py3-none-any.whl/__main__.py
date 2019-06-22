#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pype main entry point."""

from os import listdir, path
from re import sub
from sys import path as syspath

import click

from colorama import init

from pype.core import PypeCore, fname_to_name, print_context_help
from pype.exceptions import PypeException
from pype.util.cli import print_error
from pype.util.iotools import open_with_default


@click.group(
    invoke_without_command=True,
    context_settings=dict(help_option_names=['-h', '--help']),
    help='PYPE - A command-line tool for command-line tools'
)
@click.option('--list-pypes', '-l', is_flag=True,
              help='Print all available pypes')
@click.option('--aliases', '-a', is_flag=True,
              help='Print all available aliases')
@click.option('--open-config', '-o', is_flag=True,
              help='Open config file in default editor')
@click.option('--register-alias', '-r', metavar='ALIAS',
              help='Register alias for following pype')
@click.option('--unregister-alias', '-u', metavar='ALIAS',
              help='Register alias for following pype')
@click.pass_context
def main(ctx, list_pypes, aliases,
         open_config, register_alias, unregister_alias):
    """Pype main entry point."""
    if not _process_alias_configuration(
            ctx, list_pypes, open_config, register_alias, unregister_alias):
        print_context_help(ctx, level=1)
        return
    if open_config:
        open_with_default(PYPE_CORE.get_config_filepath())
    elif list_pypes:
        PYPE_CORE.list_pypes()
        return
    elif aliases:
        PYPE_CORE.list_aliases()
        return
    elif unregister_alias:
        PYPE_CORE.unregister_alias(unregister_alias)
        return
    elif ctx.invoked_subcommand is None:
        print_error('No pype selected.')
        print_context_help(ctx, level=1)


def _bind_plugin(plugin_name, plugin):

    class PypeCLI(click.MultiCommand):

        def __init__(self, *args, **kwargs):
            click.MultiCommand.__init__(
                self,
                invoke_without_command=True,
                *args, **kwargs)

        def list_commands(self, ctx):
            rv = []
            for filename in listdir(plugin.abspath):
                if filename.endswith('.py') and '__' not in filename:
                    rv.append(fname_to_name(filename))
            rv.sort()
            return rv

        def get_command(self, ctx, name):
            name = sub('-', '_', name)
            try:
                syspath.append(path.dirname(plugin.abspath))
                mod = __import__(plugin.name + '.' + name,
                                 None, None, ['main'])
            except ImportError as import_error:
                print_error(str(import_error))
                exit(1)
            return mod.main

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
    def _plugin_bind_plugin_function(
            ctx, create_pype, minimal, edit, delete_pype, open_pype):
        if (minimal or edit) and not create_pype:
            print_error(
                '"-m" and "-e" can only be used with "-c" option.')
            print_context_help(ctx, level=2)
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
                print_error('Opening internal pypes is not supported.')
                return
            # Resolve either an existing or a newly created pype
            pype_abspath = (PYPE_CORE.get_abspath_to_pype(
                plugin, sub('-', '_', open_pype))
                if open_pype else created_pype_abspath)
            if not pype_abspath:
                print_error(
                    'Pype "{}" could not be found.'.format(open_pype))
                return
            open_with_default(pype_abspath)
            toggle_invoked = True
        if ctx.parent.register_alias:
            PYPE_CORE.register_alias(ctx)
            exit(0)
        # Handle case that no toggles were used and no commands selected
        if not toggle_invoked and not ctx.invoked_subcommand:
            print_context_help(ctx, level=2)
    _plugin_bind_plugin_function.__name__ = plugin_name
    main.command(cls=PypeCLI,
                 help=plugin.doc)(_plugin_bind_plugin_function)
    return _plugin_bind_plugin_function


def _process_alias_configuration(
        ctx, list_pypes, open_config, register_alias, unregister_alias):
    if register_alias and unregister_alias:
        print_error('Options -r and -u cannot be combined.')
        return False
    other_options = open_config or list_pypes
    if register_alias and other_options:
        print_error('Option -r cannot be combined with other options.')
        return False
    if unregister_alias and other_options:
        print_error('Option -u cannot be combined with other options.')
        return False
    # piggy-back context
    ctx.register_alias = register_alias
    return True


init(autoreset=True)  # Initialize colorama
try:
    PYPE_CORE = PypeCore()
    [
        _bind_plugin(plugin.name, plugin)
        for plugin in PYPE_CORE.get_plugins()
    ]
except PypeException as pype_exception:
    print_error(str(pype_exception))
    exit(1)
