"""Raw plugin for VSS CLI (vss-cli)."""
import json as json_
import logging

import click
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output

_LOGGING = logging.getLogger(__name__)


@click.command(
    'raw',
    short_help='Make a raw call to the API'
)
@click.argument(
    'method',
    default='GET',
    type=click.Choice(
        ['GET', 'POST', 'PUT',
         'DELETE', 'PATCH']
    )
)
@click.argument(
    'uri',
)
@click.option(
    '--json', '-j',
    help='JSON payload',
    default=None
)
@pass_context
def cli(ctx: Configuration, method, uri, json):
    """Call the raw API (advanced)."""
    ctx.load_config()
    ctx.auto_output("data")
    req = dict(url=uri, method=method.upper())
    if json:
        data = json_.loads(json)
        req['payload'] = data
    # make request
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.request(**req)
    ctx.echo(
        format_output(
            ctx,
            obj
        )
    )
