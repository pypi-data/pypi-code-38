"""Docker-Compose commands module."""
import os
from typing import List, Optional
from urllib.parse import urlparse

import click
import docker
import requests
from loguru import logger

from megalus.main import Megalus

client = docker.from_env()


def get_ngrok_address(service_data: dict, only_domain: bool = False) -> list:
    """Get Ngrok address for selected port.

    :param only_domain: Return only login or full url
    :param service_data: service parsed data
    :return: List
    """
    ngrok_config = service_data['compose_project'].get('ngrok')
    if not ngrok_config:
        return []
    port = ngrok_config['port']
    secure = ngrok_config['secure']
    env = ngrok_config['env']
    protocol = "https" if secure else "http"

    try:
        ret = requests.get(
            "http://127.0.0.1:4040/api/tunnels",
            timeout=1
        )
        ret.raise_for_status()
        api_data = ret.json()
        http_url = [
            obj['public_url']
            for obj in api_data['tunnels']
            if obj['proto'] == protocol and str(port) in obj['config']['addr']
        ]
        if http_url:
            if only_domain:
                return urlparse(http_url[0]).netloc
            else:
                return [
                    "{}={}".format(env, http_url[0])
                ]
        else:
            logger.warning("Ngrok port {} not found. Skipping...".format(port))
            return []
    except requests.exceptions.RequestException as e:
        logger.error("Status Error trying to get ngrok address for port {}: {}".format(port, e))
        return []


def get_env_from_project(service_data: dict) -> list:
    """Get environment variable from yaml.

    Get value from yaml or from memory.

    :param service_data: service parsed data
    :return: List
    """
    project_envs = service_data['compose_project'].get('environment')
    if not project_envs:
        return []
    return [
        "{}={}".format(env, project_envs.get(env, os.getenv(env)))
        for env in project_envs
    ]


def check_for_docker_network(meg: Megalus, service_data: dict) -> None:
    """Check and create External Docker Networks.

    :param meg: Megalus instance
    :param service_data: Dict
    :return: None
    """
    external_network_list = [
        network_name
        for network_name in service_data['all_compose_data'].get('networks', {})
        if service_data['all_compose_data'].get('networks', {}).get(network_name).get('external', False)
    ]
    for external_network in external_network_list:
        network_found = [
            docker_network
            for docker_network in client.networks.list()
            if docker_network.name == external_network
        ]
        if not network_found:
            logger.warning(f"External network '{external_network}' not found. Creating...")
            meg.run_command(command="docker network create {}".format(external_network))


def run_compose_command(meg: Megalus, action: str, service_data: dict,
                        options: Optional[List[str]] = None, command_args: str = "",
                        all_services: bool = False) -> None:
    """Run docker-compose command.

    :param all_services: The command will be used for all services?
    :param command_args: Command arguments to send after service name in docker-compose command.
    :param meg: Megalus instance
    :param action: docker-compose command
    :param service_data: docker service parsed data
    :param options: docker-compose command options
    :return: None
    """
    environment = []  # type: list
    if service_data['compose_project'].get('ngrok'):
        ngrok_url_env = get_ngrok_address(service_data=service_data)
        ngrok_domain_env = get_ngrok_address(service_data=service_data, only_domain=True)
        environment = ngrok_url_env
        if ngrok_domain_env:
            environment += ["NGROK_DOMAIN={}".format(ngrok_domain_env)]
    environment += get_env_from_project(service_data=service_data)
    check_for_docker_network(meg, service_data)
    meg.run_command(
        "cd {working_dir} && {environment}docker-compose {files} {action}{options}{services}{args}".format(
            working_dir=service_data['working_dir'],
            environment="{} ".format(" ".join(environment)) if environment else "",
            files="-f {}".format(" -f ".join(service_data['compose_files'])),
            options=" --{} ".format(" --".join(options)) if options else " ",
            action=action,
            services=service_data.get('name', "") if not all_services else "",
            args=" {}".format(command_args) if command_args else ""
        )
    )


@click.command()
@click.argument('services', nargs=-1, required=True)
@click.pass_obj
def restart(meg: Megalus, services: List[str]) -> None:
    """Restart selected services.

    :param meg: Megalus instance.
    :param services: Docker services
    :return: None
    """
    for service in services:
        service_data = meg.find_service(service)
        run_compose_command(meg, "restart", service_data)


@click.command()
@click.argument('service', required=True)
@click.argument('number', required=True, default=1, type=click.INT)
@click.pass_obj
def scale(meg: Megalus, service: str, number: int) -> None:
    """Scale selected services.

    :param meg: Megalus instance
    :param service: docker service to be scaled
    :param number: number of replicas
    :return: None
    """
    service_data = meg.find_service(service)
    options = ["scale {}={}".format(service_data['name'], number)]
    run_compose_command(meg, "up -d", options=options, service_data=service_data, all_services=True)


@click.command()
@click.argument('services', nargs=-1, required=True)
@click.option('-d', is_flag=True)
@click.pass_obj
def up(meg: Megalus, services: List[str], d: bool) -> None:
    """Start selected services.

    :param meg: Megalus instance
    :param services: Services to be started up
    :param d: detached option
    :return: None
    """
    command = "up -d" if d or len(services) > 1 else "up"
    for service in services:
        service_data = meg.find_service(service)
        run_compose_command(meg, command, options=['remove-orphans'], service_data=service_data)
