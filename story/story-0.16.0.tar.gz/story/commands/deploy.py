# -*- coding: utf-8 -*-
import sys
from time import sleep

from blindspin import spinner

import click

import emoji

from .test import compile_app
from .. import cli, options
from ..api import Apps, Config, Releases


@cli.cli.command()
@click.option('--message', is_flag=True, help='Deployment message')
@options.app(allow_option=False)
def deploy(app, message):
    """Deploy your app to Storyscript Cloud."""
    cli.user()

    payload = compile_app(app, False)  # Also adds a spinner.

    if payload is None:
        sys.exit(1)  # Error already printed by compile_app.

    click.echo(f'Deploying app {app}... ', nl=False)

    with spinner():
        config = Config.get(app)
        release = Releases.create(config, payload, app, message)

    url = f'https://{app}.storyscriptapp.com/'
    click.echo()
    click.echo(
        click.style('\b' + emoji.emojize(':heavy_check_mark:'), fg='green')
        + f' Version {release["id"]} of your app has '
        f'been queued for deployment.\n'
    )

    click.echo('Waiting for deployment to complete…  ', nl=False)
    with spinner():
        if Apps.maintenance(app, maintenance=None):
            click.echo()
            click.echo()
            click.echo(
                'Your app is in maintenance mode.\n'
                'Run the following to turn off it off:'
            )
            cli.print_command('story maintenance off')
            click.echo()
            click.echo(
                'Once maintenance mode is turned off, '
                'your app will be deployed immediately.'
            )
            return

        state = 'QUEUED'
        while state in ['DEPLOYING', 'QUEUED']:
            state = Releases.get(app)[0]['state']
            sleep(0.5)

    click.echo()
    if state == 'DEPLOYED':
        click.echo(
            click.style('\b' + emoji.emojize(':heavy_check_mark:'), fg='green')
            + ' Deployment successful!'
        )
        click.echo(
            f'If your Story responds to HTTP requests, please visit:\n  {url}'
        )
    elif state == 'FAILED':
        click.echo(
            click.style('X', fg='red') + ' Deployment failed!', err=True
        )
        click.echo(
            'Please use the following command to view your app\'s logs:',
            err=True,
        )
        cli.print_command('story logs')
    else:
        click.echo(
            f'An unhandled state of your app has been encountered - {state}',
            err=True,
        )
        click.echo(f'Please shoot an email to support@storyscript.io')
