"""Compute plugin for VSS CLI (vss-cli)."""
import click
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from pkg_resources import iter_entry_points
from click_plugins import with_plugins


@with_plugins(
    iter_entry_points('vss_cli.contrib.compute')
)
@click.group(
    'compute',
    short_help='Manage VMs, networks, folders, etc.'
)
@pass_context
def cli(ctx: Configuration):
    """Compute related resources such as virtual machines, networks
       supported operating systems, logical folders, OVA/OVF images,
       floppy images, ISO images and more."""
    with ctx.spinner(disable=ctx.debug):
        ctx.load_config()


from vss_cli.plugins.compute_plugins import (
    domain, inventory, net, os as compute_os,
    image, iso, floppy, folder, template, vm
)  # pylint: disable=unused-import
