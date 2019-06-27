import logging

import click
from vss_cli import const
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.plugins.compute import cli

_LOGGING = logging.getLogger(__name__)


@cli.group(
    'template',
    short_help='List virtual machine templates'
)
@pass_context
def compute_template(ctx):
    """List virtual machine templates"""
    pass


@compute_template.command(
    'ls',
    short_help='List virtual machine templates'
)
@click.option(
    '-f', '--filter',
    multiple=True,
    type=(click.STRING, click.STRING),
    help='Filter list by name, ip, dns or path.'
)
@click.option(
    '-s', '--summary', is_flag=True,
    help='Display summary'
)
@click.option(
    '-p', '--page', is_flag=True,
    help='Page results in a less-like format'
)
@pass_context
def compute_template_ls(
        ctx: Configuration,
        filter, summary, page
):
    """List virtual machine templates.

    Filter list by name, ip address dns or path. For example:

        vss-cli compute template ls -f name VMTemplate1

    """
    query = dict()
    if summary:
        query['summary'] = 1
    if filter:
        for f in filter:
            query[f[0]] = f[1]
    # get templates
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_templates(**query)
    # including additional attributes?
    if summary:
        columns = ctx.columns or const.COLUMNS_VM
        for t in obj:
            t['folder'] = '{parent} > {name}'.format(**t['folder'])
    else:
        columns = ctx.columns or const.COLUMNS_VM_MIN
    # format output
    output = format_output(
        ctx,
        obj,
        columns=columns
    )
    # page
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)
