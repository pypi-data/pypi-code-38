"""Command 'run' module."""

import click
from loguru import logger

from megalus.main import Megalus


@click.command()
@click.argument('command', nargs=1, required=True)
@click.pass_obj
def run(meg: Megalus, command: str) -> None:
    """Run selected script.

    :param meg: Megalus instance
    :param command: command/script to execute
    :return: None
    """
    line_to_run = meg.config_data['defaults'].get('scripts', {}).get(command, None)
    if not line_to_run:
        logger.warning('Command "{}" not found in configuration file.'.format(command))
    else:
        meg.run_command(line_to_run)
