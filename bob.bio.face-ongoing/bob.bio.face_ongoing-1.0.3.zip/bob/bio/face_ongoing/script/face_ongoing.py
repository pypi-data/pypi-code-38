import click
import pkg_resources
from click_plugins import with_plugins
from bob.extension.scripts.click_helper import AliasedGroup, ConfigCommand


@with_plugins(pkg_resources.iter_entry_points('bob.bio.face_ongoing.cli'))
@click.group(cls=AliasedGroup)
def face_ongoing():
    """Face Ongoing Commands."""

    pass

