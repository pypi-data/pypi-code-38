import logging

import click
from vss_cli import const
import vss_cli.autocompletion as autocompletion
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.exceptions import VssCliError
from vss_cli.helper import format_output
from vss_cli.plugins.compute import cli

_LOGGING = logging.getLogger(__name__)


@cli.group('net',
           short_help='List available virtual networks')
@pass_context
def cli(ctx: Configuration):
    """List available virtual networks."""


@cli.command(
    'ls',
    short_help='list virtual networks.'
)
@click.option(
    '-f', '--filter',
    multiple=True, type=(click.STRING, click.STRING),
    help='filter list by name or moref'
)
@click.option(
    '-s', '--sort', type=click.STRING,
    help='sort by name or moref attributes.'
)
@click.option(
    '-p', '--page',
    is_flag=True,
    help='page results in a less-like format')
@pass_context
def network_ls(
        ctx: Configuration, filter,
        sort, page
):
    """List available virtual networks.

    Filter by path or name name=<name> or moref=<moref>.
    For example:

        vss-cli compute net ls -f name public
    """
    query = dict(summary=1)
    if filter:
        for f in filter:
            query[f[0]] = f[1]
    if sort:
        query['sort'] = sort
    # query
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_networks(**query)
    # set columns
    columns = ctx.columns or const.COLUMNS_NET_MIN
    # format
    output = format_output(
        ctx,
        obj,
        columns=columns
    )
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)


@cli.group(
    'get',
    help='Given virtual network info.',
    invoke_without_command=True
)
@click.argument(
    'name_or_moref',
    type=click.STRING,
    required=True,
    autocompletion=autocompletion.networks
)
@pass_context
def network_get(ctx: Configuration, name_or_moref):
    _net = ctx.get_network_by_name_or_moref(
        name_or_moref
    )
    ctx.moref = _net[0]['moref']
    if click.get_current_context().invoked_subcommand is None:
        columns = ctx.columns or const.COLUMNS_NET
        obj = ctx.get_network(ctx.moref)
        click.echo(
            format_output(
                ctx,
                [obj],
                columns=columns,
                single=True
            )
        )


@network_get.command(
    'vms',
    help='List vms on network.'
)
@click.option(
    '-p', '--page', is_flag=True,
    help='page results in a less-like format'
)
@pass_context
def net_get_vms(ctx: Configuration, page):
    """List virtual machines using current network."""
    obj = ctx.get_network(ctx.moref, summary=1)
    if not obj:
        raise VssCliError(
            f'Either network {ctx.moref} does not exist, '
            f'or you do not have permission to access.'
        )
    objs = obj['vms']
    columns = ctx.columns or const.COLUMNS_VM_MIN
    output = format_output(
        ctx,
        objs,
        columns=columns
    )
    # page
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)


@network_get.command(
    'perm',
    help='List network permissions.'
)
@click.option(
    '-p', '--page', is_flag=True,
    help='page results in a less-like format'
)
@pass_context
def net_get_permission(ctx: Configuration, page):
    """Obtain network group or user permissions."""
    obj = ctx.get_network_permission(ctx.moref)
    if not obj:
        raise VssCliError(
            f'Either network {ctx.moref} does not exist, '
            f'or you do not have permission to access.'
        )
    columns = ctx.columns or const.COLUMNS_PERMISSION
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
