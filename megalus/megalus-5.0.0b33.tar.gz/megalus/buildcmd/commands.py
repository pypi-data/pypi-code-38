"""Build command."""
from typing import List

import click
from loguru import logger

from megalus.compose.commands import run_compose_command
from megalus.main import Megalus


@click.command()
@click.argument('services', nargs=-1, required=True)
@click.option('--force', is_flag=True)
@click.pass_obj
def build(meg: Megalus, services: List, force: bool) -> None:
    """Run the build command on selected services.

    Use this command to build the selected services.

    :param meg: click context object
    :param services: services list to build
    :param force: use the --force to add the --no-cache option in build
    :return:
    """
    for service_to_find in services:
        logger.info('Looking for Service: {}'.format(service_to_find))
        service_data = meg.find_service(service_to_find, build_only=True)

        options = ["force-rm"]
        if force:
            options.append("no-cache")
        command_args = "| pv -lft -D 2 >> {log}".format(log=meg.logfile)
        run_compose_command(meg, action="build", options=options, service_data=service_data, command_args=command_args)
        logger.success('Service {} builded.'.format(service_data['name']))
