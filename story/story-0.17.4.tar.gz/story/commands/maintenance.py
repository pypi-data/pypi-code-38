# -*- coding: utf-8 -*-
from blindspin import spinner

import click

import emoji

from .. import api
from .. import cli
from .. import options


@cli.cli.group()
def maintenance():
    """Manage the availability of your apps."""
    pass


@maintenance.command()
@options.app()
def check(app):
    """Displays current maintenance status."""
    cli.user()
    click.echo(f'Fetching maintenance mode for {app}… ', nl=False)
    with spinner():
        enabled = api.Apps.maintenance(app=app, maintenance=None)
    if enabled:
        click.echo(
            click.style('ON. Application is disabled.', bold=True, fg='red')
        )
    else:
        click.echo(
            click.style('off. Application is running.', bold=True, fg='green')
        )


@maintenance.command()
@options.app()
def on(app):
    """Turns maintenance–mode on."""

    cli.user()
    click.echo(f'Enabling maintenance mode for app {app}… ', nl=False)
    with spinner():
        app = api.Apps.maintenance(app=app, maintenance=True)
    click.echo(
        '\b' + click.style(emoji.emojize(':heavy_check_mark:'), fg='green')
    )
    click.echo(
        click.style('Application is now in maintenance–mode.', dim=True)
    )


@maintenance.command()
@options.app()
def off(app):
    """Turns maintenance–mode off."""

    cli.user()
    click.echo(f'Disabling maintenance mode for app {app}… ', nl=False)
    with spinner():
        app = api.Apps.maintenance(app=app, maintenance=False)
    click.echo(
        click.style('\b' + emoji.emojize(':heavy_check_mark:'), fg='green')
    )
    click.echo(click.style('Application is now running.', dim=True))
