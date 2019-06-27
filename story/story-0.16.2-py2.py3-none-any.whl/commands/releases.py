# -*- coding: utf-8 -*-
import sys

from blindspin import spinner

import click

import emoji

from .. import api
from .. import cli
from .. import options
from ..helpers.datetime import parse_psql_date_str, reltime


@cli.cli.group()
def releases():
    """Manage releases for your app (including rollback)."""
    pass


@releases.command(name='list')
@click.option(
    '--limit', '-n', nargs=1, default=20, help='List N latest releases'
)
@options.app()
def list_command(app, limit):
    """List application releases."""
    cli.user()

    # click.echo(click.style('Releases', fg='magenta'))
    # click.echo(click.style('========', fg='magenta'))

    with spinner():
        res = api.Releases.list(app, limit=limit)

    res = sorted(res, key=lambda elem: elem['id'])

    if res:
        from texttable import Texttable

        table = Texttable(max_width=800)
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(['l', 'l', 'l', 'l'])
        all_releases = [['VERSION', 'STATUS', 'CREATED', 'MESSAGE']]
        for release in res:
            date = parse_psql_date_str(release['timestamp'])
            all_releases.append(
                [
                    f'v{release["id"]}',
                    release['state'].capitalize(),
                    reltime(date),
                    release['message'],
                ]
            )
        table.add_rows(rows=all_releases)
        click.echo(table.draw())
    else:
        click.echo(f'No releases yet for app {app}.')


@releases.command()
@click.argument('version', nargs=1, required=False)
@options.app()
def rollback(version, app):
    """Rollback release to a previous release."""
    cli.user()

    if version and version[0] == 'v':
        version = version[1:]

    if not version:
        click.echo(f'Getting latest release for app {app}…  ', nl=False)
        with spinner():
            res = api.Releases.get(app=app)
            version = int(res[0]['id']) - 1
        click.echo(
            click.style('\b' + emoji.emojize(':heavy_check_mark:'), fg='green')
        )

    try:
        if int(version) == 0:
            click.echo('Unable to rollback a release before v1.')
            sys.exit(1)
    except ValueError:
        click.echo(
            click.style('Invalid release specified.', fg='red'), err=True
        )
        sys.exit(1)

    click.echo(f'Rolling back to v{version}…  ', nl=False)

    with spinner():
        res = api.Releases.rollback(version=version, app=app)

    click.echo(
        click.style('\b' + emoji.emojize(':heavy_check_mark:'), fg='green')
    )
    click.echo(
        f'Deployed new release… '
        + click.style(f'v{res["id"]}', bold=True, fg='magenta')
    )
