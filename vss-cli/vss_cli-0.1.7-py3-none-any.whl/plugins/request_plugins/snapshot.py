"""Vm Snapshot Request Management plugin for VSS CLI (vss-cli)."""
import logging

import click

from vss_cli import const, rel_opts as so
import vss_cli.autocompletion as autocompletion
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.plugins.request import cli

_LOGGING = logging.getLogger(__name__)


@cli.group('snapshot', short_help='Manage virtual machine snapshot requests')
@pass_context
def snapshot(ctx: Configuration):
    """ Creating, deleting and reverting virtual machine
    snapshots will produce a virtual machine snapshot request."""


@snapshot.command('ls', short_help='list snapshot requests')
@so.filter_opt
@so.sort_opt
@so.all_opt
@so.count_opt
@so.page_opt
@pass_context
def snapshot_ls(ctx: Configuration, filter_by, page, sort, show_all, count):
    """List requests based on:

        Filter list in the following format <field_name> <operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status eq,PROCESSED

            vss-cli request snapshot ls -f status eq,PROCESSED

        Sort list in the following format <field_name> <asc|desc>. For example:

            vss-cli request snapshot ls -s created_on desc

    """
    columns = ctx.columns or const.COLUMNS_REQUEST
    if not ctx.columns:
        columns.extend(
            [
                ('VM_NAME', 'vm_name'),
                ('VM_UUID', 'vm_uuid'),
                ('ACTION', 'action'),
            ]
        )
    params = dict()
    if all(filter_by):
        params['filter'] = f'{filter_by[0]},{filter_by[1]}'
    if all(sort):
        params['sort'] = f'{sort[0]},{sort[1]}'
    # make request
    with ctx.spinner(disable=ctx.debug):
        _requests = ctx.get_snapshot_requests(
            show_all=show_all, per_page=count, **params
        )

    output = format_output(ctx, _requests, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)


@snapshot.command('get', help='Snapshot request')
@click.argument(
    'rid',
    type=click.INT,
    required=True,
    autocompletion=autocompletion.snapshot_requests,
)
@pass_context
def snapshot_get(ctx, rid):
    # make request
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_snapshot_request(rid)
    columns = ctx.columns or const.COLUMNS_REQUEST
    if not ctx.columns:
        columns.extend(const.COLUMNS_REQUEST_SNAP)
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@snapshot.group('set', help='Update snapshot request')
@click.argument(
    'rid',
    type=click.INT,
    required=True,
    autocompletion=autocompletion.snapshot_requests,
)
@pass_context
def snapshot_set(ctx: Configuration, rid):
    ctx.rid = rid


@snapshot_set.command('duration')
@click.option(
    '-l',
    '--lifetime',
    type=click.IntRange(1, 72),
    help='Number of hours the snapshot will live.',
    required=True,
)
@pass_context
def snapshot_set_duration(ctx: Configuration, lifetime):
    """Extend snapshot lifetime"""
    # make request
    with ctx.spinner(disable=ctx.debug):
        _, obj = ctx.extend_snapshot_request(ctx.rid, lifetime)
    columns = ctx.columns or const.COLUMNS_REQUEST
    if not ctx.columns:
        columns.extend(const.COLUMNS_REQUEST_SNAP)
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
