"""Stop command."""
from typing import List

import click

from megalus.compose.commands import run_compose_command
from megalus.main import Megalus


def stop_all(meg: Megalus) -> None:
    """Stop all containers.

    :param meg: Megalus instance
    :return: None
    """
    all_projects = []  # type: List[dict]
    service_data_list = []
    for service in meg.all_services:
        if service['compose'] not in all_projects:
            service['name'] = ""
            service_data_list.append(service)
            all_projects.append(service['compose'])
    for service_data in service_data_list:
        run_compose_command(meg, "stop", service_data)


@click.command()
@click.argument('services', nargs=-1)
@click.pass_obj
def stop(meg: Megalus, services: List[str]) -> None:
    """Stop selected services.

    :param meg: Megalus instance
    :param services: services to be stopped
    :return: None
    """
    if not services:
        stop_all(meg)
    for service in services:
        service_data = meg.find_service(service)
        run_compose_command(meg, "stop", service_data)
