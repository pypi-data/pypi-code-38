import logging

import click
from vss_cli import const
import vss_cli.autocompletion as autocompletion
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.plugins.compute import cli

_LOGGING = logging.getLogger(__name__)


@cli.group(
    'inventory',
    short_help='Manage inventory reports'
)
@pass_context
def cli(ctx: Configuration):
    """Create or download an inventory file of your virtual machines
    hosted. Inventory files are created and transferred to your VSKEY-STOR
    space and are also available through the API."""


@cli.command(
    'dl',
    short_help='download inventory report'
)
@click.argument(
    'request_id',
    type=click.INT,
    required=True,
    autocompletion=autocompletion.inventory_requests
)
@click.option(
    '-d', '--directory', type=click.STRING,
    help='report destination',
    required=False, default=None
)
@click.option(
    '-l', '--launch',
    is_flag=True,
    help='Launch link in default application'
)
@pass_context
def compute_inventory_dl(
        ctx: Configuration, request_id,
        directory, launch
):
    """Downloads given inventory request to current directory or
    provided path. Also, it's possible to open downloaded file in
    default editor."""
    with ctx.spinner(disable=ctx.debug):
        file_path = ctx.download_inventory_result(
            request_id=request_id,
            directory=directory
        )
    obj = {'file': file_path}

    click.echo(
        format_output(
            ctx,
            [obj],
            columns=[('FILE', 'file')],
            single=True
        )
    )
    # to launch or not
    if launch:
        click.launch(file_path)


@cli.command(
    'mk',
    short_help='create inventory report'
)
@click.argument(
    'attribute',
    nargs=-1,
    default=None,
    autocompletion=autocompletion.inventory_properties
)
@click.option(
    '-f', '--fmt',
    type=click.Choice(['json', 'csv']),
    default='csv', help='hide header'
)
@click.option(
    '-a', '--all',
    is_flag=True,
    help='include all attributes'
)
@pass_context
def compute_inventory_mk(ctx: Configuration, fmt, all, attribute):
    """Submits an inventory report request resulting in a file with your
    virtual machines and more than 30 attributes in either JSON or CSV
    format.

    The following attributes can be requested in the report:

    status, domain, diskCount, uuid, nics, state, hostName, vmtRunning,
    memory, provisionedSpace, osId, folder, snapshot,
    requested, networkIds, hardwareVersion, changeLog,
    haGroup, usedSpace, nicCount, uncommittedSpace,
    name, admin, disks, vmtVersion, inform, client,
    guestOsId, clientNotes, ipAddress, cpu
    """
    attributes = ctx.get_inventory_properties() if all else list(attribute)
    obj = ctx.create_inventory_file(fmt=fmt, props=attributes)
    # format output
    click.echo(
        format_output(
            ctx,
            [obj],
            columns=const.COLUMNS_REQUEST_SUBMITTED,
            single=True
        )
    )
