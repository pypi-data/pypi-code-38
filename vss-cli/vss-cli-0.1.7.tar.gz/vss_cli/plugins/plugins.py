"""Plugins plugin for VSS CLI (vss-cli)."""
import logging

import click
from vss_cli.cli import pass_context
from vss_cli.config import Configuration

from pkg_resources import iter_entry_points
from click_plugins import with_plugins

_LOGGING = logging.getLogger(__name__)


@with_plugins(
    iter_entry_points('vss_cli.contrib.plugins')
)
@click.group(
    'plugins',
    short_help='External plugins.'
)
@pass_context
def cli(ctx: Configuration):
    """External CLI plugins."""
    with ctx.spinner(disable=ctx.debug):
        ctx.load_config()
