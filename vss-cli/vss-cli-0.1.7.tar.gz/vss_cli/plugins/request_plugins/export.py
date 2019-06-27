"""Vm Export Request Management plugin for VSS CLI (vss-cli)."""
import logging

import click

from vss_cli import const, rel_opts as so
import vss_cli.autocompletion as autocompletion
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.plugins.request import cli

_LOGGING = logging.getLogger(__name__)


@cli.group('export', short_help='Manage virtual machine export requests')
@pass_context
def request_mgmt_export(ctx: Configuration):
    """Manage virtual machine export requests."""
    pass


@request_mgmt_export.command('ls', short_help='list vm export requests')
@so.filter_opt
@so.sort_opt
@so.all_opt
@so.count_opt
@so.page_opt
@pass_context
def request_mgmt_export_ls(
    ctx: Configuration, filter_by, page, sort, show_all, count
):
    """List requests based on:

        Filter list in the following format <field_name> <operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status eq,PROCESSED

            vss-cli request export ls -f status eq,PROCESSED

        Sort list in the following format <field_name> <asc|desc>. For example:

            vss-cli request export ls -s created_on desc

    """
    columns = ctx.columns or const.COLUMNS_REQUEST_EXPORT_MIN
    params = dict()
    if all(filter_by):
        params['filter'] = f'{filter_by[0]},{filter_by[1]}'
    if all(sort):
        params['sort'] = f'{sort[0]},{sort[1]}'
    # make request
    with ctx.spinner(disable=ctx.debug):
        _requests = ctx.get_export_requests(
            show_all=show_all, per_page=count, **params
        )

    output = format_output(ctx, _requests, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)


@request_mgmt_export.command('get', short_help='Export request')
@click.argument(
    'rid',
    type=click.INT,
    required=True,
    autocompletion=autocompletion.export_requests,
)
@pass_context
def request_mgmt_export_get(ctx: Configuration, rid):
    # make request
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_export_request(rid)
    columns = ctx.columns or const.COLUMNS_REQUEST_EXPORT
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
