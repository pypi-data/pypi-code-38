from pathlib import Path
from typing import Optional

import click
from yaml import YAMLError
from yamlcfg import YAMLConfig

from apeiron.config import cfg
from apeiron.config import DEFAULTS
from apeiron.constants import SOURCES_DIR, PACKAGES_DIR
from apeiron.models import ManifestIndex
from apeiron.manifest import get_manifest_index_path
from apeiron.manifest import save_manifests


from apeiron.view import print_config


def create_dir_if_not_exist(path: Path, name: str):
    if not path.exists():
        click.echo(click.style(f"{name.capitalize()} not found, creating…", fg="yellow"))
        try:
            path.mkdir(parents=True)
        except IOError as e:
            click.echo(click.style(f"Failed to create {name}, reason: {str(e)}", fg="red"))
            exit(1)
        else:
            click.echo(click.style(f"Created empty {name}: {path.as_posix()}", fg="green"))


# noinspection PyProtectedMember
def check(extra_config_path: Optional[str]):
    local_config: Path = Path(cfg._paths[0])
    if not local_config.exists():
        click.echo(click.style(f"Config not found, writing defaults…", fg="yellow"))
        cfg._data = DEFAULTS
        try:
            cfg.write()
        except IOError as e:
            click.echo(click.style(f"Failed to write default config, reason: {str(e)}", fg="red"))
            exit(1)
        else:
            click.echo(click.style(f"Wrote defaults to: {local_config.as_posix()}", fg="green"))
    if extra_config_path is not None:
        try:
            augmented_config: YAMLConfig = YAMLConfig(path=extra_config_path)
        except YAMLError as e:
            click.echo(click.style(
                f"Failed to update config with values from {extra_config_path}, reason: {str(e)}", fg="red"
            ))
            exit(1)
        else:
            cfg._data.update(augmented_config._data)
            click.echo(click.style(f"Loaded extra config from: {extra_config_path}", fg="green"))
    click.echo(click.style("Application config", fg="blue", bold=True))
    click.echo(print_config(cfg))

    base_storage: Path = Path(cfg.storage_dir)
    create_dir_if_not_exist(base_storage, "base storage")

    source_dir: Path = base_storage / SOURCES_DIR
    create_dir_if_not_exist(source_dir, "source dir")

    package_dir: Path = base_storage / PACKAGES_DIR
    create_dir_if_not_exist(package_dir, "package dir")

    manifest_index_path: Path = get_manifest_index_path()
    if not manifest_index_path.exists():
        click.echo(click.style(f"Manifests index not found, writing stub…", fg="yellow"))
        try:
            save_manifests(ManifestIndex())
        except IOError as e:
            click.echo(click.style(f"Failed to write manifests index, reason: {e}", fg="red"))
            exit(1)
        else:
            click.echo(click.style(f"Wrote empty manifest index to: {manifest_index_path.as_posix()}", fg="green"))
