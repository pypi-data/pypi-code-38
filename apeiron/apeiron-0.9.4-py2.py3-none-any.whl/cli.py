from typing import List
from pathlib import Path

import click

from apeiron.bootstrap import check
from apeiron.constants import OBJECTS_DIR
from apeiron.exceptions import ManifestError
from apeiron.exceptions import ModpackError
from apeiron.manifest import bootstrap_source_manifest
from apeiron.models import SourceManifest
from apeiron.modpack import get_modpack, get_modpacks, enable_modpack, build_modpack, disable_modpack, delete_modpack
from apeiron.view import print_modpack, print_modpacks, print_source_manifest


@click.group()
@click.option(
    '--config',
    expose_value=True,
    default=None,
    help="Additional cfg",
    type=click.Path(exists=True, resolve_path=True)
)
def cli(config: str):
    """Simple CLI for modpack management"""
    check(config)


@cli.command(name="list")
def _list():
    """Lists all modpacks"""

    click.echo(click.style("Available modpacks", fg="blue", bold=True))
    click.echo(print_modpacks(get_modpacks()))


@cli.command(name="show")
@click.argument("name", metavar="<name>")
def show(name: str):
    """Show detailed info about modpack <name>"""

    click.echo(print_modpack(get_modpack(name)))


@cli.command(name="create")
def create():
    """Create new empty modpack"""

    name: str = click.prompt("Enter modpack name (internal identifier)")
    title: str = click.prompt("Enter modpack displayed title", default=name.capitalize())
    game_version: str = click.prompt("Enter modpack version", default="1.10.2")
    libraries_url: str = click.prompt("Specify libraries URL", default=None)
    objects_dir: str = click.prompt("Specify objects location for this modpack", default=OBJECTS_DIR)

    source_manifest: SourceManifest = SourceManifest(
        name=name,
        title=title,
        gameVersion=game_version,
        librariesLocation=libraries_url,
        objectsLocation=objects_dir
    )

    click.echo()
    click.echo(click.style("Check generated modpack stub below:", bold=True))
    click.echo(print_source_manifest(source_manifest))

    if not click.confirm("Is this correct?"):
        return click.echo(click.style("Aborted", fg='red'))

    try:
        path: Path = bootstrap_source_manifest(source_manifest)
    except ManifestError as e:
        click.echo(click.style(str(e), fg="red"))
    else:
        click.echo(click.style("Bootstrapped new modpack!", fg="green", bold=True))
        click.echo(f"You can now edit modpack details in {click.style(path.as_posix(), bold=True)}")


@cli.command(name="enable")
@click.argument("name", metavar="<name>")
def enable(name: str):
    """Enables modpack <name>"""

    click.echo(f"Enabling modpack «{click.style(name, bold=True)}»")
    try:
        enable_modpack(name)
    except ModpackError as e:
        click.echo(click.style(str(e), fg="yellow"))
    else:
        click.echo(click.style(f"Enabled modpack «{click.style(name, bold=True)}»", fg="green"))


@cli.command(name="disable")
@click.argument("name", metavar="<name>")
def disable(name: str):
    """Disables modpack <name>"""

    click.echo(f"Disabling modpack «{click.style(name, bold=True)}»")
    try:
        disable_modpack(name)
    except ModpackError as e:
        click.echo(click.style(str(e), fg="yellow"))
    else:
        click.echo(click.style(f"Disabled modpack «{click.style(name, bold=True)}»", fg="green"))


@cli.command(name="delete")
@click.option('--prune', is_flag=True, expose_value=True, default=False, help="Prunes sources as well as built files")
@click.argument("name", metavar="<name>")
@click.pass_context
def delete(ctx: click.core.Context, name: str, prune: bool):
    """Deletes modpack <name>"""

    ctx.invoke(disable, name=name)
    click.echo(f"Deleting files for modpack «{click.style(name, bold=True)}»")
    try:
        result: List[ManifestError] = delete_modpack(name, prune)
    except ModpackError as e:
        click.echo(click.style(str(e), fg='red'))
    else:
        for exc in result:
            click.echo(click.style(str(exc), fg='yellow'))
        if prune:
            click.echo(click.style(f"Completely removed modpack «{click.style(name, bold=True)}»", fg="green"))
        else:
            click.echo(click.style(f"Deleted built files for modpack «{click.style(name, bold=True)}»", fg="green"))


@cli.command(name="build")
@click.option('--debug', is_flag=True, expose_value=True, default=False, help="Print some debug info")
@click.option('--strict', is_flag=True, expose_value=True, default=False, help="Strict check for pre-existing files")
@click.argument("name", metavar="<name>")
@click.pass_context
def build(ctx: click.core.Context, name: str, strict: bool, debug: bool):
    """Build modpack <name>"""

    click.echo(f"Building modpack «{click.style(name, bold=True)}»…")
    try:
        build_modpack(name, strict, debug)
    except ModpackError as e:
        click.echo(click.style(str(e), fg="yellow"))
    except ManifestError as e:
        click.echo(click.style(str(e), fg="red"))
    else:
        click.echo(click.style(f"Successfully build modpack «{click.style(name, bold=True)}»", fg="green"))
        ctx.invoke(show, name=name)


if __name__ == '__main__':
    cli()
