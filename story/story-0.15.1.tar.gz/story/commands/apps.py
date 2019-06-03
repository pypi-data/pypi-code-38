# -*- coding: utf-8 -*-
import os
import subprocess
import sys

from blindspin import spinner

import click

import emoji

from .. import api
from .. import awesome
from .. import cli
from .. import options
from ..helpers.datetime import parse_psql_date_str, reltime


def maintenance(enabled: bool) -> str:
    if enabled:
        return 'in maintenance'
    else:
        return 'running'


@cli.cli.group()
def apps():
    """Create, list, and manage apps on Storyscript Cloud."""
    pass


@apps.command(name='list')
def list_command():
    """List apps that you have access to."""
    from texttable import Texttable

    cli.user()

    with spinner():
        res = api.Apps.list()

    count = 0
    # Heads up! Texttable does not like colours.
    # So don't use click.style here.
    table = Texttable(max_width=800)
    table.set_deco(Texttable.HEADER)
    table.set_cols_align(['l', 'l', 'l'])
    all_apps = [['NAME', 'STATE', 'CREATED']]
    for app in res:
        count += 1
        date = parse_psql_date_str(app['timestamp'])
        all_apps.append(
            [app['name'], maintenance(app['maintenance']), reltime(date)]
        )

    table.add_rows(rows=all_apps)

    if count == 0:
        click.echo('No application found. Create your first app with')
        click.echo(click.style('$ story apps create', fg='magenta'))
    else:
        click.echo(table.draw())


@apps.command()
@click.argument('name', nargs=1, required=False)
@click.option(
    '--team', type=str, help='Team name that owns this new Application'
)
def create(name, team):
    """Create a new app."""

    cli.user()
    story_yaml = cli.find_story_yml()

    if story_yaml is not None:
        click.echo(
            click.style(
                'There appears to be an Storyscript Cloud project in '
                f'{story_yaml} already.\n',
                fg='red',
            )
        )
        click.echo(
            click.style(
                'Are you trying to deploy? ' 'Try the following:', fg='red'
            )
        )
        click.echo(click.style('$ story deploy', fg='magenta'))
        sys.exit(1)

    # _is_git_repo_good()

    name = name or awesome.new()

    # Sanity check.
    if len(name) < 4:
        click.echo(
            click.style(
                'The name you specified is too short. \n'
                'Please use at least 4 charecters in your app name.',
                fg='red',
            )
        )
        sys.exit(1)

    click.echo('Creating application… ', nl=False)

    with spinner():
        api.Apps.create(name=name, team=team)

    click.echo(
        '\b' + click.style(emoji.emojize(':heavy_check_mark:'), fg='green')
    )

    # click.echo('Adding git-remote... ', nl=False)
    # cli.run(f'git remote add asyncy https://git.asyncy.com/{name}')
    # click.echo(click.style(emoji.emojize(':heavy_check_mark:'), fg='green'))

    click.echo('Creating story.yml… ', nl=False)
    cli.settings_set(f'app_name: {name}\n', 'story.yml')

    click.echo(
        '\b' + click.style(emoji.emojize(':heavy_check_mark:'), fg='green')
    )

    click.echo('\nApp Name: ' + click.style(name, bold=True))
    click.echo(
        'App URL:  '
        + click.style(f'https://{name}.storyscriptapp.com/', fg='blue')
        + '\n'
    )

    click.echo(
        'You are now ready to write your first Storyscript! '
        f'{emoji.emojize(":party_popper:")}'
    )
    click.echo()

    cli.track('App Created', {'App name': name})

    click.echo(' - [ ] Write a Story:')
    click.echo(
        '       $ '
        + click.style('story write http > http.story', fg='magenta')
    )
    click.echo()
    click.echo(' - [ ] Deploy to Storyscript Cloud:')
    click.echo('       $ ' + click.style('story deploy', fg='magenta'))
    click.echo()
    click.echo('We hope you enjoy your deployment experience!')


@apps.command()
@options.app()
def url(app):
    """Display the full URL of an app.

    Great to use with $(story apps url) in bash.
    """
    cli.user()
    print_nl = False

    if os.isatty(sys.stdout.fileno()):
        print_nl = True

    click.echo(f'https://{app}.storyscriptapp.com/', nl=print_nl)


@apps.command()
@options.app()
@click.option(
    '--confirm', is_flag=True, help='Do not prompt to confirm destruction.'
)
def destroy(confirm, app):
    """Destroy an app."""

    cli.user()

    if confirm or click.confirm(
        f'Do you want to destroy {app!r}?', abort=True
    ):
        click.echo(f'Destroying application {app!r}… ', nl=False)

        with spinner():
            api.Apps.destroy(app=app)
            cli.track('App Destroyed', {'App name': app})

        click.echo(
            '\b' + click.style(emoji.emojize(':heavy_check_mark:'), fg='green')
        )
