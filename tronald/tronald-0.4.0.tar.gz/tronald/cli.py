import click
import shelve
import inquirer
import configparser
from time import sleep

from .config import MetaData, TronaldConfig, DOTFILE_NAME
from .controllers import RemoteController, LocalController
from .initial import (
    KEY_PATH_SETUP,
    DEFAULT_DATABASE_SETUP,
    CONTAINER_PREFIX,
    CONTAINER_SUFFIX,
    perform_initial_setup,
)


@click.group()
def cli():
    pass


@cli.command(name="settings")
@click.option("--prefix", "prefix")
@click.option("--suffix", "suffix")
@click.option("--key", "key_path")
@click.option("--db", "db_name")
def configure(prefix, suffix, key_path, db_name):
    config = TronaldConfig()
    if not prefix and not suffix and not key_path and not db_name:
        click.echo("Current settings:\n")
        for key, value in config.configuration.items():
            click.echo("{}: {}".format(key, value))
        return

    if key_path:
        config.set_value("keypath", key_path)

    if db_name:
        config.set_value("defaultdatabase", db_name)

    if prefix:
        config.set_value("prefix", prefix)

    if suffix:
        config.set_value("suffix", suffix)


@cli.command()
@click.option("--container", "container")
@click.option("--ssh-user", "ssh_user")
@click.option("--postgres-user", "postgres_user")
@click.option("--postgres-db", "postgres_db")
@click.argument("host")
@click.argument("target")
def dump(host, container, ssh_user, postgres_user, postgres_db, target):
    meta_params = {
        "host": host,
        "ssh_user": ssh_user,
        "postgres_user": postgres_user,
        "postgres_db": postgres_db or "app",
        "container": container,
        "target": target,
    }
    meta_data = MetaData(**meta_params)
    controller = RemoteController(meta_data)
    controller.dump_and_transfer()


@cli.command(name="import")
@click.argument("dump_path")
@click.argument("container_identifier")
@click.option("--postgres-user", "postgres_user")
@click.option("--postgres-db", "postgres_db")
def import_dump(dump_path, container_identifier, postgres_user, postgres_db):
    configuration_parameters = {
        "dump_path": dump_path,
        "container_identifier": container_identifier,
        "postgres_user": postgres_user or "django",
        "postgres_db": postgres_db or "app",
    }
    controller = LocalController(**configuration_parameters)
    controller.import_dump()


def run_cli():
    perform_initial_setup()
    cli()


if __name__ == "__main__":
    perform_initial_setup()
    cli()
