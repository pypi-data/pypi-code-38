#!/usr/bin/env python

import click

from kudu.api import authenticate
from kudu.commands.init import init
from kudu.commands.link import link
from kudu.commands.pull import pull
from kudu.commands.push import push
from kudu.config import ConfigOption


@click.group()
@click.option('--username', '-u', cls=ConfigOption, prompt=True, envvar='KUDU_USERNAME')
@click.option('--password', '-p', cls=ConfigOption, prompt=True, hide_input=True, envvar='KUDU_PASSWORD')
@click.option('--token', '-t', cls=ConfigOption, envvar='KUDU_TOKEN')
@click.pass_context
def cli(ctx, username, password, token):
    if not token:
        try:
            token = authenticate(username, password)
        except ValueError:
            click.echo('Invalid username or password', err=True)
            exit(1)

    ctx.obj = {
        'username': username,
        'password': password,
        'token': token
    }


cli.add_command(init)
cli.add_command(pull)
cli.add_command(push)
cli.add_command(link)

if __name__ == '__main__':
    cli()
