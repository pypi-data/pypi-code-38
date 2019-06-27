"""SSH Key Management plugin for VSS CLI (vss-cli)."""
import logging
import os

import click

from vss_cli import const, rel_opts as so
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.exceptions import VssCliError
from vss_cli.helper import format_output

_LOGGING = logging.getLogger(__name__)


@click.group('key', short_help='Manage your SSH Public Keys.')
@pass_context
def cli(ctx: Configuration):
    """Manage your SSH Public Keys."""
    with ctx.spinner(disable=ctx.debug):
        ctx.load_config()


@cli.command('ls', short_help='List user SSH Public Keys.')
@so.filter_opt
@so.sort_opt
@so.all_opt
@so.count_opt
@so.page_opt
@pass_context
def key_ls(ctx: Configuration, filter_by, page, sort, show_all, count):
    """List ssh public keys based on:

        Filter list in the following format <field_name> <operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: type eq,ssh-rsa

            vss-cli key ls -f type eq,ssh-rsa

        Sort list in the following format <field_name> <asc|desc>. For example:

            vss-cli key ls -s created_on desc

    """
    columns = ctx.columns or const.COLUMNS_SSH_KEY_MIN
    params = dict()
    if all(filter_by):
        params['filter'] = f'{filter_by[0]},{filter_by[1]}'
    if all(sort):
        params['sort'] = f'{sort[0]},{sort[1]}'
    # make request
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_user_ssh_keys(
            show_all=show_all, per_page=count, **params
        )
    # format output
    output = format_output(ctx, obj, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)


@cli.command('get', help='Display user key info.')
@click.argument('kid', type=int, required=True)
@pass_context
def key_get(ctx: Configuration, kid):
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_user_ssh_key(kid)
    columns = ctx.columns or const.COLUMNS_SSH_KEY
    # format output
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@cli.command('mk', help='Create SSH Public Key.')
@click.argument('path_or_key', type=click.STRING, required=True, nargs=1)
@pass_context
def key_mk(ctx, path_or_key):
    with ctx.spinner(disable=ctx.debug):
        if os.path.isfile(path_or_key):
            obj = ctx.create_user_ssh_key_path(path_or_key)
        else:
            obj = ctx.create_user_ssh_key(path_or_key)
    # defining columns
    columns = ctx.columns or const.COLUMNS_SSH_KEY_MIN
    # if key has been created print
    if obj:
        # format output
        click.echo(format_output(ctx, [obj], columns=columns, single=True))
    else:
        raise VssCliError(
            'Cloud not create key. '
            'Verify if a valid SSH Public Key'
            ' has been provided.'
        )


@cli.command('rm', help='Delete SSH Public Key.')
@click.argument('kid', type=int, required=True, nargs=-1)
@click.option('-s', '--summary', is_flag=True, help='Print request summary')
@pass_context
def key_rm(ctx: Configuration, kid, summary):
    result = []
    with click.progressbar(kid) as ids:
        for i in ids:
            result.append(ctx.delete_user_ssh_key(i))
    if summary:
        for res in result:
            click.echo(
                format_output(
                    ctx, [res], columns=[('STATUS', 'status')], single=True
                )
            )
