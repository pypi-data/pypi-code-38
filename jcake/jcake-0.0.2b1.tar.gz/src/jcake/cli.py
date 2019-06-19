#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Console script for jcake."""

from __future__ import absolute_import

import click
import crayons

from .meta import __version__
from .options import CONTEXT_SETTINGS, JCakeGroup
from .cli_utils import format_help


@click.group(cls=JCakeGroup, invoke_without_command=True,
             context_settings=CONTEXT_SETTINGS)
@click.version_option(prog_name=crayons.yellow("jcake", bold=True),
                      version=__version__)
@click.pass_context
def cli(ctx, **kwargs):
    if ctx.invoked_subcommand is None:
        click.echo(format_help(ctx.get_help()))


@cli.command(
    short_help="Create new Java Project based Maven.",
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True),
)
@click.option('--ms', help="MicroService Project", is_flag=True)
def create(ms, **kwargs):
    from .commands import create

    project_dir = create(ms)

    click.echo(u'\n\nThe target project is: {}\n'.format(project_dir))


if __name__ == "__main__":
    cli()  # pragma: no cover
