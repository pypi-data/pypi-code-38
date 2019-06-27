# -*- coding: utf-8 -*-
import os

import click

import click_completion

from .. import cli


def custom_startswith(string, incomplete):
    """A custom completion matching that supports case insensitive matching"""
    if os.environ.get('_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE'):
        string = string.lower()
        incomplete = incomplete.lower()
    return string.startswith(incomplete)


click_completion.core.startswith = custom_startswith
click_completion.init()


@cli.cli.command()
@click.option(
    '-i',
    '--case-insensitive',
    is_flag=True,
    help='Case insensitive completion',
)
@click.option(
    '--install',
    is_flag=True,
    help='Install completion code into shell startup file',
)
@click.argument(
    'shell',
    required=False,
    type=click_completion.DocumentedChoice(click_completion.core.shells),
)
@click.argument('path', required=False)
def completion(path, shell, install, case_insensitive):
    """Show or install shell completion code"""
    extra_env = (
        {'_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE': 'ON'}
        if case_insensitive
        else {}
    )
    if install:
        shell, path = click_completion.core.install(
            shell=shell, path=path, append=True, extra_env=extra_env
        )
        click.echo('%s completion installed in %s' % (shell, path))
    else:
        click.echo(click_completion.core.get_code(shell, extra_env=extra_env))
