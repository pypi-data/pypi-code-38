# -*- coding: utf-8 -*-
from blindspin import spinner

import click

import emoji

from .. import api
from .. import cli
from .. import options


@cli.cli.group()
def config():
    """Update the configuration for your app."""
    pass


@config.command(name='list')
@options.app()
def list_command(app):
    """List environment variables."""

    cli.user()
    click.echo('Fetching config… ', nl=False)

    with spinner():
        config = api.Config.get(app)

    click.echo(
        click.style('\b' + emoji.emojize(':heavy_check_mark:'), fg='green')
    )

    if config:
        click.echo(click.style('Storyscript variables:', dim=True))
        for name, value in config.items():
            if not isinstance(value, dict):
                click.echo(click.style(name, fg='green') + f':  {value}')

        click.echo('')
        click.echo(click.style('Service variables:', dim=True))
        for name, value in config.items():
            if isinstance(value, dict):
                click.echo(click.style(name, bold=True))
                for _name, _value in value.items():
                    click.echo(
                        '  ' + click.style(_name, fg='green') + f':  {_value}'
                    )

    else:
        click.echo(click.style('No configuration set yet.', bold=True))
        click.echo(
            '\nSet Storyscript environment '
            + click.style('$ ', dim=True)
            + click.style('story config set key=value', fg='magenta')
        )
        click.echo(
            'Set service environment '
            + click.style('$ ', dim=True)
            + click.style('story config set service.key=value', fg='magenta')
        )


@config.command(name='set')
@click.argument('variables', nargs=-1)
@click.option(
    '--message',
    '-m',
    nargs=1,
    default=None,
    help='(optional) Message why variable(s) were created.',
)
@options.app()
def set_command(variables, app, message):
    """
    Set one or more environment variables.

        $ story config set key=value foo=bar

    To set an environment variable for a specific service use

        $ story config set twitter.oauth_token=value

    """
    cli.user()

    click.echo('Fetching config… ', nl=False)
    with spinner():
        config = api.Config.get(app=app)
    click.echo(
        click.style('\b' + emoji.emojize(':heavy_check_mark:'), fg='green')
    )

    if variables:
        for keyval in variables:
            try:
                key, val = tuple(keyval.split('=', 1))
            except ValueError:
                click.echo(
                    f'Config variables must be of the form name=value.'
                    f'\nGot unexpected pair "{keyval}"',
                    err=True,
                )
                click.echo(set_command.__doc__.strip())
                return
            # TODO validate against a regexp pattern
            if '.' in key:
                service, key = tuple(key.split('.', 1))
                config.setdefault(service.lower(), {})[key.upper()] = val
            else:
                config[key.upper()] = val

            click.echo()
            click.echo(f" {click.style(key.upper(), fg='green')}: {val}")

        click.echo('\nSetting config and deploying new release…  ', nl=False)
        with spinner():
            release = api.Config.set(config=config, app=app, message=message)
        click.echo(
            click.style('\b' + emoji.emojize(':heavy_check_mark:'), fg='green')
        )
        click.echo(
            f'Deployed new release… '
            + click.style(f'v{release["id"]}', bold=True, fg='magenta')
        )

    else:
        click.echo(set_command.__doc__.strip())


@config.command()
@click.argument('variables', nargs=-1)
@options.app()
def get(variables, app):
    """Get one or more environment variables."""

    cli.user()

    if variables:
        click.echo(f'Fetching config for {app}… ', nl=False)

        with spinner():
            config = api.Config.get(app=app)

        click.echo(
            click.style(emoji.emojize(':heavy_check_mark:'), fg='green')
        )

        for name in variables:
            if '.' in name:
                service, name = tuple(name.split('.', 1))
                value = config[service.lower()].get(name.upper(), None)
            else:
                if name in config:
                    # could be a service here
                    value = config[name]
                else:
                    value = config.get(name.upper(), None)

            if value:
                if isinstance(value, dict):
                    for name, value in value.items():
                        click.echo(
                            click.style(name.upper(), fg='green')
                            + f':  {value}'
                        )
                else:
                    click.echo(
                        click.style(name.upper(), fg='green') + f':  {value}'
                    )
            else:
                click.echo(
                    click.style(
                        f'No variable named "{name.upper()}".', fg='red'
                    )
                )
    else:
        click.echo(get.__doc__.strip())


@config.command(name='del')
@click.argument('variables', nargs=-1)
@click.option(
    '--message',
    '-m',
    nargs=1,
    default=None,
    help='(optional) Message why variable(s) were deleted.',
)
@options.app()
def del_command(variables, app, message):
    """
    Delete one or more environment variables
    """
    cli.user()
    if variables:

        click.echo('Fetching config… ', nl=False)
        with spinner():
            config = api.Config.get(app=app)
        click.echo(
            click.style(emoji.emojize(':heavy_check_mark:'), fg='green')
        )

        for key in variables:
            removed = False
            if key in config:
                if type(config.pop(key)) is dict:
                    click.echo(
                        click.style('Removed service', fg='red') + f': {key}'
                    )
                else:
                    removed = True
            elif key.upper() in config:
                config.pop(key.upper())
                removed = True
            elif '.' in key:
                service, key = tuple(key.split('.', 1))
                if service in config and key.upper() in config[service]:
                    config[service].pop(key.upper())
                    removed = True

            if removed:
                click.echo(
                    click.style('Removed', fg='red') + f': {key.upper()}'
                )

        click.echo('\nSetting config and deploying new release… ', nl=False)
        with spinner():
            release = api.Config.set(config=config, app=app, message=message)
        click.echo(
            click.style('\b' + emoji.emojize(':heavy_check_mark:'), fg='green')
        )
        click.echo(
            f'Deployed new release… '
            + click.style(f'v{release["id"]}', bold=True, fg='magenta')
        )

    else:
        click.echo(del_command.__doc__.strip())
