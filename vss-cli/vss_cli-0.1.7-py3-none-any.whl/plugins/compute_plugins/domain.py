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


@cli.group(
    'domain',
    short_help='List compute domains.'
)
@pass_context
def cli(ctx: Configuration):
    """A fault domain consists of one or more ESXI hosts and
    Datastore Clusters grouped together according to their
    physical location in the datacenter."""


@cli.command(
    'ls',
    short_help='list fault domains'
)
@click.option(
    '-f', '--filter',
    multiple=True,
    type=(click.STRING, click.STRING),
    help='filter list by name or moref'
)
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@pass_context
def domain_ls(
        ctx: Configuration, filter, page
):
    columns = ctx.columns or const.COLUMNS_MOID
    query_params = dict(summary=1)
    if filter:
        for f in filter:
            query_params[f[0]] = f[1]
    # query
    with ctx.spinner(disable=ctx.debug):
        objs = ctx.get_domains(**query_params)
    # format output
    output = format_output(
        ctx,
        objs,
        columns=columns,
    )
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)


@cli.group(
    'get',
    help='Given domain info.',
    invoke_without_command=True
)
@click.argument(
    'name_or_moref',
    type=click.STRING,
    required=True,
    autocompletion=autocompletion.domains
)
@pass_context
def domain_get(ctx: Configuration, name_or_moref):
    _domain = ctx.get_domain_by_name_or_moref(
        name_or_moref
    )
    ctx.moref = _domain[0]['moref']
    if click.get_current_context().invoked_subcommand is None:
        columns = ctx.columns or const.COLUMNS_MOID
        if not ctx.columns:
            columns.extend([
                ('HOSTS', 'hostsCount'),
                ('STATUS', 'status')
            ])
        with ctx.spinner(disable=ctx.debug):
            obj = ctx.get_domain(ctx.moref)
        click.echo(
            format_output(
                ctx,
                [obj],
                columns=columns,
                single=True
            )
        )


@domain_get.command(
    'vms',
    help='Given domain vms.'
)
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@pass_context
def domain_get_vms(ctx: Configuration, page):
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_domain(ctx.moref, summary=1)
    if not obj:
        raise VssCliError(
            f'Either domain {ctx.moref} does not exist, '
            f'or you do not have permission to access.'
        )
    objs = obj['vms']
    output = format_output(
        ctx,
        objs,
        columns=const.COLUMNS_VM_MIN
    )
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)
