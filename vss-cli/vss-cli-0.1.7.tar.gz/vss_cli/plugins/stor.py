"""VSS Storage Management plugin for VSS CLI (vss-cli)."""
import logging
import os

import click
from vss_cli import const
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output
from vss_cli.utils.emoji import EMOJI_UNICODE

_LOGGING = logging.getLogger(__name__)


@click.group(
    'stor',
    short_help='Manage your VSS storage account.'
)
@pass_context
def cli(ctx: Configuration):
    """Manage your VSS storage account."""
    with ctx.spinner(disable=ctx.debug):
        ctx.load_config()


@cli.command(
    'ls',
    short_help='list remote dir contents'
)
@click.argument(
    'remote_path',
    type=click.STRING,
    default="/"
)
@pass_context
def stor_ls(ctx: Configuration, remote_path):
    columns = ctx.columns or const.COLUMNS_WEBDAV
    ctx.get_vskey_stor()
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.vskey_stor.list(remote_path)
    click.echo(
        format_output(
            ctx,
            obj,
            columns=columns
        )
    )


@cli.command(
    'get',
    short_help='get remote info'
)
@click.argument(
    'remote_path',
    type=click.STRING,
    required=True
)
@pass_context
def stor_get(ctx, remote_path):
    ctx.get_vskey_stor()
    columns = ctx.columns or const.COLUMNS_WEBDAV_INFO
    obj = ctx.vskey_stor.info(remote_path)
    click.echo(
        format_output(
            ctx,
            [obj],
            columns=columns,
            single=True
        )
    )


@cli.command(
    'dl',
    short_help='download file'
)
@click.argument(
    'remote_path',
    type=click.STRING,
    required=True
)
@click.option(
    '-d', '--dir',
    type=click.STRING,
    help='Local target directory',
    default=os.getcwd()
)
@click.option(
    '-n', '--name',
    type=click.STRING,
    help='Local target name'
)
@pass_context
def stor_dl(
        ctx: Configuration,
        remote_path, dir, name
):
    """Download remote file."""
    ctx.get_vskey_stor()
    local_dir = os.path.expanduser(dir) or os.getcwd()
    local_name = name or os.path.basename(remote_path)
    local_path = os.path.join(local_dir, local_name)
    # check if remote path exists
    if not ctx.vskey_stor.check(remote_path):
        raise _LOGGING.warning(f'Remote path not found {remote_path}')
    ctx.log(
        f'Download {remote_path} to {local_path} in '
        f'progress {EMOJI_UNICODE.get(":fast_down_button:")} '
    )
    with ctx.spinner(disable=ctx.debug):
        ctx.vskey_stor.download_sync(
            remote_path=remote_path,
            local_path=local_path
        )
    ctx.log(
        f'Download complete to {local_path} '
        f'{EMOJI_UNICODE.get(":white_heavy_check_mark:")}')


@cli.command(
    'ul',
    short_help='upload file'
)
@click.argument(
    'file_path',
    type=click.Path(exists=True),
    required=True
)
@click.option(
    '-d', '--dir',
    type=click.STRING,
    help='Remote target directory',
    default='/'
)
@click.option(
    '-n', '--name',
    type=click.STRING,
    help='Remote target name'
)
@pass_context
def stor_ul(ctx: Configuration, file_path, name, dir):
    """Upload given file to your VSKEY-STOR space.
    This command is useful when, for instance, a required ISO is
    not available in the VSS central repository and needs to be
    mounted to a virtual machine.
    """
    ctx.get_vskey_stor()
    file_name = name or os.path.basename(file_path)
    remote_base = dir
    # check if remote path exists
    if not ctx.vskey_stor.check(remote_base):
        _LOGGING.debug(f'Creating {remote_base}.')
        ctx.vskey_stor.mkdir(remote_base)
        _LOGGING.debug(f'Created {remote_base}.')
    # upload
    remote_path = os.path.join(remote_base, file_name)
    ctx.log(f'Upload {file_path} to {remote_path} '
            f'in progress {EMOJI_UNICODE.get(":fast_up_button:")}')
    with ctx.spinner(disable=ctx.debug):
        ctx.vskey_stor.upload_sync(
            remote_path=remote_path,
            local_path=file_path)
    ctx.echo(
        f'Upload complete to {remote_path} '
        f'{EMOJI_UNICODE.get(":white_heavy_check_mark:")}'
    )
