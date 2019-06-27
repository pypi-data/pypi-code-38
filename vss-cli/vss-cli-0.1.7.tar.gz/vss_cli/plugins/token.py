"""Token Management plugin for VSS CLI (vss-cli)."""
import click

from vss_cli import const, rel_opts as so
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output


@click.group('token', short_help='Manage access tokens')
@pass_context
def cli(ctx: Configuration):
    """Manage access tokens."""
    with ctx.spinner(disable=ctx.debug):
        ctx.load_config()


@cli.command('ls', short_help='list user tokens')
@so.filter_opt
@so.sort_opt
@so.all_opt
@so.count_opt
@so.page_opt
@pass_context
def token_ls(ctx: Configuration, filter_by, page, sort, show_all, count):
    """List tokens based on:

        Filter list in the following format <field_name> <operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: valid eq,false

            vss-cli token ls -f valid eq,false

        Sort list in the following format <field_name> <asc|desc>. For example:

            vss-cli token ls -s created_on desc

    """
    columns = ctx.columns or const.COLUMNS_TK_MIN
    params = dict()
    if all(filter_by):
        params['filter'] = f'{filter_by[0]},{filter_by[1]}'
    if all(sort):
        params['sort'] = f'{sort[0]},{sort[1]}'
    # make request
    with ctx.spinner(disable=ctx.debug):
        _requests = ctx.get_user_tokens(
            show_all=show_all, per_page=count, **params
        )
    # format output
    output = format_output(ctx, _requests, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)


@cli.command('get', help='Token')
@click.argument('tid', type=click.INT, required=True)
@pass_context
def token_get(ctx: Configuration, tid):
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_user_token(tid)
    columns = ctx.columns or const.COLUMNS_TK
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@cli.command('rm', help='Delete user token.')
@click.argument('tid', type=int, required=True, nargs=-1)
@click.option('-s', '--summary', is_flag=True, help='Print request summary')
@pass_context
def token_rm(ctx: Configuration, tid, summary):
    result = []
    with click.progressbar(tid) as ids:
        for i in ids:
            result.append(ctx.delete_user_token(i))
    if summary:
        for res in result:
            click.echo(
                format_output(
                    ctx, [res], columns=[('STATUS', 'status')], single=True
                )
            )
