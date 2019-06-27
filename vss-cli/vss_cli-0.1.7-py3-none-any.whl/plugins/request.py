"""Request Management plugin for VSS CLI (vss-cli)."""
import click
from vss_cli.cli import pass_context
from vss_cli.config import Configuration


@click.group(
    'request',
    short_help='Manage various requests'
)
@pass_context
def cli(ctx: Configuration):
    """Useful to track request status and details."""
    with ctx.spinner(disable=ctx.debug):
        ctx.load_config()


from vss_cli.plugins.request_plugins import (
    snapshot, image, new, change,
    export, folder, inventory
)  # pylint: disable=unused-import
