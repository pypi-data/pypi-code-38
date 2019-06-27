"""Token Management plugin for VSS CLI (vss-cli)."""
import click

from vss_cli import const, rel_opts as so
import vss_cli.autocompletion as autocompletion
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output


@click.group('message', short_help='Manage VSS Messages.')
@pass_context
def cli(ctx: Configuration):
    """Manage VSS Messages."""
    with ctx.spinner(disable=ctx.debug):
        ctx.load_config()


@cli.command('ls', short_help='list user message')
@so.filter_opt
@so.sort_opt
@so.all_opt
@so.count_opt
@so.page_opt
@pass_context
def message_ls(ctx: Configuration, filter_by, page, sort, show_all, count):
    """List messages based on:

        Filter list in the following format <field_name> <operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: kind eq,Notice

            vss-cli message ls -f kind eq,Notice

        Sort list in the following format <field_name> <asc|desc>. For example:

            vss-cli message ls -s created_on desc

    """
    columns = ctx.columns or const.COLUMNS_MESSAGE_MIN
    params = dict()
    if all(filter_by):
        params['filter'] = f'{filter_by[0]},{filter_by[1]}'
    if all(sort):
        params['sort'] = f'{sort[0]},{sort[1]}'
    # make request
    with ctx.spinner(disable=ctx.debug):
        _requests = ctx.get_user_messages(
            show_all=show_all, per_page=count, **params
        )
    # format output
    output = format_output(ctx, _requests, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)


@cli.command('get', help='Display user message info.')
@click.argument(
    'message_id',
    type=click.INT,
    required=True,
    autocompletion=autocompletion.account_messages,
)
@pass_context
def message_get(ctx: Configuration, message_id):
    """Get given user message id info"""
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_user_message(message_id)
    columns = ctx.columns or const.COLUMNS_MESSAGE
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@cli.group('set', short_help='Set given user message attribute.')
@pass_context
def message_set(ctx):
    """Update given user message id info"""


@message_set.command('ack', short_help='Acknowledge user message')
@click.argument(
    'message_id',
    type=click.INT,
    required=True,
    nargs=-1,
    autocompletion=autocompletion.account_messages,
)
@click.option('-s', '--summary', is_flag=True, help='Print request summary')
@pass_context
def message_set_ack(ctx, message_id, summary):
    result = []
    with click.progressbar(message_id) as ids:
        for i in ids:
            result.append(ctx.ack_user_message(i))
    if summary:
        for res in result:
            click.echo(
                format_output(
                    ctx, [res], columns=[('STATUS', 'status')], single=True
                )
            )
