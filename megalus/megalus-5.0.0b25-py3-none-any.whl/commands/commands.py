"""Megalus configuration file commands."""
import sys
from typing import Optional

import click
from loguru import logger

from megalus.main import Megalus


def find_and_run_command(meg: Megalus, service: Optional[str], action: str):
    """Find and run command.

    :param meg: Megalus instance
    :param service: service for command
    :param action: install or config
    :return: None or sys.exit(1)
    """
    if not service:
        config_command = meg.config_data['defaults'].get('{}_commands'.format(action), {}).get('default')
    else:
        config_command = meg.config_data['defaults'].get('{}_commands'.format(action), {}).get(service)
    if config_command:
        if "{service}" in config_command:
            meg.run_command(config_command.format(service=service))
        else:
            meg.run_command(config_command)
    else:
        logger.error("No command defined in configuration.")
        sys.exit(1)


@click.command()
@click.argument('service', required=False)
@click.pass_obj
def config(meg: Megalus, service: Optional[str]) -> None:
    """Run Config commands.

    :param meg: Megalus instance
    :param service: service for config command
    :return: None
    """
    find_and_run_command(meg, service, "config")


@click.command()
@click.argument('service', required=False)
@click.pass_obj
def install(meg: Megalus, service: Optional[str]) -> None:
    """Run Install commands.

    :param meg: Megalus instance
    :param service: service for install command
    :return: None
    """
    find_and_run_command(meg, service, "install")
