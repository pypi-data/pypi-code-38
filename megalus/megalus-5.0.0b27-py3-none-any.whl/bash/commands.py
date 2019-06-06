"""meg bash command."""

import click
from buzio import console
from loguru import logger

from megalus.compose.commands import run_compose_command
from megalus.main import Megalus
from megalus.utils import client, find_containers


@click.command()
@click.argument('service', nargs=1, required=True)
@click.pass_obj
def bash(meg: Megalus, service: str) -> None:
    """'bash' command.

    Use this command to open a bash session in current running container,
    or start one for select service.

    :param meg: click context object
    :param service: docker-compose service name
    :return: None
    """
    service_data = meg.find_service(service)

    container_id = None
    eligible_containers = find_containers(service_data['name'])
    if not eligible_containers:
        logger.info("Running /bin/bash in service {}".format(service_data['name']))
        run_compose_command(meg, action="run", options=["rm", "service-ports"], service_data=service_data,
                            command_args="/bin/bash")
    elif len(eligible_containers) == 1:
        container_id = eligible_containers[0].short_id
    else:
        container_names = [c.name for c in eligible_containers]
        container = console.choose(container_names, 'Please select the container')
        if container:
            container_id = client.containers.get(container).short_id
    if container_id:
        logger.info(
            "Running /bin/bash in service {} in container {}".format(service_data['name'], container_id))
        meg.run_command(
            'cd {} && docker exec -ti {} /bin/bash'.format(service_data['working_dir'], container_id)
        )
