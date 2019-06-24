"""Check command."""
import os
from typing import List, Optional, Tuple

import arrow
import click
import docker
from docker import DockerClient
from docker.errors import ImageNotFound
from loguru import logger

from megalus.main import Megalus

client = docker.from_env()


def get_services_to_check(meg: Megalus, service: str, service_list: List[str], ignore_list: List[str], tree: List[str],
                          compose_data: dict) -> Optional[Tuple[List, List]]:
    """Get services to check.

    Recursively get all services to check and ignore.

    :param meg: click context object
    :param service: service to inspect
    :param service_list: services to check list
    :param ignore_list: services to ignore list
    :param tree: current service dependencies list
    :param compose_data: docker-compose data
    :return: Tuple
    """
    if service in service_list or service in ignore_list:
        return  # type: ignore

    service_list.append(service) if compose_data.get('build', None) else ignore_list.append(  # type: ignore
        service)
    if compose_data.get('depends_on', None):
        tree = compose_data['depends_on']

    if tree:
        for key in tree:
            key_data = meg.find_service(key)
            get_services_to_check(meg, key, service_list, ignore_list, tree, key_data['compose_data'])
    return service_list, ignore_list


def get_docker_image(compose_data: dict) -> Optional[DockerClient]:  # type: ignore
    """Get docker image data.

    :param compose_data: compose parsed data.
    :return: DockerClient image instance or None
    """
    if compose_data.get('image', None) and compose_data.get('build', None):
        try:
            return client.images.get(compose_data['image'])
        except ImageNotFound:
            return None


def has_old_image(ctx: Megalus, service: str, show_logs) -> bool:
    """Check if image is outdated.

    :param show_logs: Show logs in terminal
    :param ctx: Megalus instance
    :param service: docker service selected
    :return: bool
    """

    def get_date_from_file(file: str) -> arrow:
        """Get date from file.

        :param file: file full path
        :return: Arrow instance
        """
        date = arrow.get(os.path.getmtime(os.path.join(data['working_dir'], file))).to('local')
        if show_logs:
            logger.debug("Last update for file {} was {}".format(file, date.humanize()))
        return date

    data = ctx.find_service(service)
    image = get_docker_image(data['compose_data'])
    if not image:
        return False
    else:
        image_date_created = arrow.get(image.attrs['Created']).to('local')
        if show_logs:
            logger.debug("Last docker build was {}".format(image_date_created.humanize()))
        global_files_to_watch = ctx.config_data['defaults'].get('check_for_build', [])
        list_dates = [
            get_date_from_file(file)
            for file in global_files_to_watch
            if os.path.isfile(os.path.join(data['working_dir'], file))
        ]
        if list_dates and image_date_created < max(list_dates):
            return True
        return False


@click.command()
@click.argument('services', nargs=-1, required=True)
@click.pass_obj
def check(meg: Megalus, services) -> None:
    """Check services.

    This command will check the selected services for:

    * Need build because does not have image
    * Need build because his image is outdated

    To find out if the image needs updating,
    add the list of files in the megalus.yml file,
    whose update date should be compared to the build date of the image.

    Example: if you add the 'Dockerfile', 'requirements.txt' and 'Pipfile'
    inside the 'check_for_build: files:' section in megalus.yml, this command will compare,
    for each file, his last modification date against docker image build date
    for the service.

    :param meg: click context object
    :param services: services list to be inspected
    :return: None
    """

    for service in services:
        logger.info("Checking {}...".format(service))
        service_data = meg.find_service(service)
        logger.debug("Docker Compose file is located at: {}".format(service_data['working_dir']))
        check_docker_image(meg, service_data, show_logs=True)


def check_docker_image(meg, service_data, show_logs=False) -> bool:
    """Check docker image for selected service.

    :param show_logs: Show logs on terminal
    :param meg: Megalus instance
    :param service_data: service data for docker service
    :return: Bool
    """

    need_image = service_data['compose_data'].get('image', None) and service_data['compose_data'].get('build', None)
    if not need_image:
        if show_logs:
            logger.info("Service {} does not need image. Skipping check...".format(service_data['name']))
        return True

    has_image = get_docker_image(service_data['compose_data'])
    if not has_image:
        if show_logs:
            logger.warning("Service {} does not have image.".format(service_data['name']))
        return True

    service_has_old_image = has_old_image(meg, service_data['name'], show_logs=show_logs)
    if service_has_old_image:
        if show_logs:
            logger.warning("Service {} has a old image.".format(service_data['name']))
        return False

    if show_logs:
        logger.success("Service {} pass image check.".format(service_data['name']))
    return True
