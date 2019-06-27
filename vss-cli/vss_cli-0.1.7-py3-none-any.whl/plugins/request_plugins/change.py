"""Vm Change Request Management plugin for VSS CLI (vss-cli)."""
import logging

import click

from vss_cli import const, rel_opts as so
import vss_cli.autocompletion as autocompletion
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.plugins.request import cli

_LOGGING = logging.getLogger(__name__)


@cli.group('change', short_help='Manage virtual machine change requests')
@pass_context
def request_mgmt_change(ctx: Configuration):
    """ Updating any virtual machine attribute
    will produce a virtual machine change request."""
    pass


@request_mgmt_change.command('ls', short_help='list vm change requests')
@so.filter_opt
@so.sort_opt
@so.all_opt
@so.count_opt
@so.page_opt
@pass_context
def request_mgmt_change_ls(
    ctx: Configuration, filter_by, page, sort, show_all, count
):
    """List requests based on:

        Filter list in the following format <field_name> <operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss-cli request change ls -f status eq,PROCESSED

        Sort list in the following format <field_name> <asc|desc>. For example:

            vss-cli request change ls -s created_on desc

    """
    columns = ctx.columns or const.COLUMNS_REQUEST_CHANGE_MIN
    params = dict()
    if all(filter_by):
        params['filter'] = f'{filter_by[0]},{filter_by[1]}'
    if all(sort):
        params['sort'] = f'{sort[0]},{sort[1]}'
    # make request
    with ctx.spinner(disable=ctx.debug):
        _requests = ctx.get_change_requests(
            show_all=show_all, per_page=count, **params
        )

    output = format_output(ctx, _requests, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)


@request_mgmt_change.command('get', short_help='Change request')
@click.argument(
    'rid',
    type=click.INT,
    required=True,
    autocompletion=autocompletion.change_requests,
)
@pass_context
def request_mgmt_change_get(ctx: Configuration, rid):
    # make request
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_change_request(rid)
    columns = ctx.columns or const.COLUMNS_REQUEST_CHANGE
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@request_mgmt_change.command('retry', short_help='Retry vm change request')
@click.argument(
    'rid',
    type=click.INT,
    required=True,
    autocompletion=autocompletion.change_requests,
)
@pass_context
def request_mgmt_change_retry(ctx: Configuration, rid):
    """Retries given virtual machine change request with status
    'Error Processed'.
    """
    # make request
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.retry_change_request(rid)
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@request_mgmt_change.group(
    'set', short_help='Update vm change request', invoke_without_command=True
)
@click.argument(
    'rid',
    type=click.INT,
    required=True,
    autocompletion=autocompletion.change_requests,
)
@pass_context
def request_mgmt_change_set(ctx: Configuration, rid):
    ctx.request_id = rid
    if click.get_current_context().invoked_subcommand is None:
        raise click.UsageError('Sub command is required')


@request_mgmt_change_set.command(
    'schedule', short_help='Update scheduling settings'
)
@click.option(
    '-c', '--cancel', is_flag=True, help='Cancel scheduling', default=False
)
@click.option(
    '-d',
    '--date-time',
    type=click.DateTime(formats=const.SUPPORTED_DATETIME_FORMATS),
    required=False,
    default=None,
    help='Update datetime YYYY-MM-DD HH:MM.',
)
@pass_context
def request_mgmt_change_set_schedule(ctx: Configuration, cancel, date_time):
    # make request
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_change_request(ctx.request_id)
    if not obj:
        raise click.BadArgumentUsage(
            f'Change Request {ctx.request_id} does not exit.'
        )
    # no point of updating scheduling time if not scheduled
    if not obj.get('status') == 'Scheduled':
        raise click.BadArgumentUsage(
            f'Change Request {ctx.request_id} is not ' f'scheduled.'
        )
    # create payload
    payload = dict(request_id=ctx.request_id)
    # cancel option
    if cancel:
        ctx.cancel_scheduled_change_request(**payload)
        obj = ctx.get_change_request(ctx.request_id)
    # update datetime
    elif date_time:
        import datetime

        payload['date_time'] = datetime.datetime.strftime(
            date_time, const.DEFAULT_DATETIME_FMT
        )
        # update request
        obj = ctx.reschedule_change_request(**payload)
    else:
        raise click.BadOptionUsage(
            option_name='date-time',
            message='Provide either -c/--cancel or -d/--date-time '
            'to update request.',
        )
    # provide feedback
    columns = ctx.columns or const.COLUMNS_REQUEST_CHANGE
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
