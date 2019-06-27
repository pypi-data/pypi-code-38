import logging

import click

from vss_cli import const, rel_opts as so
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.plugins.compute import cli

_LOGGING = logging.getLogger(__name__)


@cli.group('iso', short_help='Manage ISO images.')
@pass_context
def compute_iso(ctx: Configuration):
    """Available ISO images in both the VSS central store and your personal
    VSKEY-STOR space."""


@compute_iso.group('public', short_help='Browse public images')
@pass_context
def compute_iso_public(ctx: Configuration):
    """Available ISO images in the VSS central store"""


@compute_iso_public.command('ls', short_help='list public ISO images')
@so.filter_opt
@so.sort_opt
@so.all_opt
@so.page_opt
@pass_context
def compute_iso_public_ls(ctx: Configuration, filter_by, show_all, sort, page):
    """List available ISO images in the VSS central store.

    Filter by name and sort desc. For example:

        vss-cli compute iso public ls -f name like,Cent% -s path asc
    """
    params = dict(expand=1)
    if all(filter_by):
        params['filter'] = f'{filter_by[0]},{filter_by[1]}'
    if all(sort):
        params['sort'] = f'{sort[0]},{sort[1]}'
    # get objects
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_isos(show_all=show_all, **params)
    # format
    columns = ctx.columns or const.COLUMNS_IMAGE
    output = format_output(ctx, obj, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)


@compute_iso.group('personal', short_help='Browse current user images')
@pass_context
def compute_iso_personal(ctx: Configuration):
    """Available ISO images in your personal VSKEY-STOR space."""
    pass


@compute_iso_personal.command('ls', short_help='list personal ISO images')
@click.option(
    '-p', '--page', is_flag=True, help='page results in a less-like format'
)
@pass_context
def compute_iso_personal_ls(ctx: Configuration, page):
    """List available ISO images stored in your personal VSKEY-STOR space.
    If the image you uploaded is not listing here, use the sync and try again.

        vss-cli compute iso personal sync
        vss-cli compute iso personal ls
    """
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_user_isos()
    # format
    columns = ctx.columns or const.COLUMNS_IMAGE
    output = format_output(ctx, obj, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)


@compute_iso_personal.command('sync', short_help='Sync personal ISO images')
@pass_context
def compute_iso_personal_sync(ctx: Configuration):
    """Synchronize ISO images stored in your personal VSKEY-STOR space. Once
    processed it should be listed with the ls command."""
    obj = ctx.sync_user_isos()
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
