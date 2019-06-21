import click
import pkg_resources
from click_plugins import with_plugins
from bob.extension.scripts.click_helper import AliasedGroup, ConfigCommand


@with_plugins(pkg_resources.iter_entry_points('bob.bio.htface.cli'))
@click.group(cls=AliasedGroup)
def htface():
    """Face Ongoing Commands."""

    pass

