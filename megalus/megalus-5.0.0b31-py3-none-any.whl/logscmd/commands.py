"""Megalus commands log module."""
import re
import sys
from time import sleep

import arrow
import click
from buzio import console
from loguru import logger

from megalus.compose.commands import run_compose_command
from megalus.main import Megalus
from megalus.utils import find_containers


def show_log(name: str, line: str) -> None:
    """Show docker container log in loguru.

    :param name: service name
    :param line: service log line
    :return: None
    """
    config = {
        "handlers": [
            {
                "sink": sys.stderr,
                "format": "<d><lvl>{level: <8}</lvl> | <cyan>{extra[container]}</cyan> "
                          "| <blue>{extra[docker_timestamp]}</blue></d> | <lvl>{message}</lvl>",
                "colorize": True
            }
        ],
        "extra": {
            "container": name,
            "docker_timestamp": arrow.get(line[:22]).to('local')
        }
    }
    logger.configure(**config)
    if "ERROR:" in line or "FATAL:" in line or "CRITICAL:" in line:
        logger.error(line[31:])
    elif "WARNING:" in line:
        logger.warning(line[31:])
    elif "DEBUG:" in line:
        logger.debug(line[31:])
    else:
        logger.info(line[31:])


@click.command()
@click.argument('services', nargs=-1, required=True)
@click.option('--regex')
@click.pass_obj
def logs(meg: Megalus, services: list, regex: str):
    """Log docker services containers.

    :param meg: Megalus instance
    :param services: selected docker services
    :param regex: regex to filter logs
    :return: None
    """
    try:
        time_to_fetch = 2
        services_data_to_log = [
            meg.find_service(service_to_find)
            for service_to_find in services
        ]
        logger.info(f"Show log info for services: {', '.join([service['name'] for service in services_data_to_log])}")
        while True:
            for service_data in services_data_to_log:
                if len(services_data_to_log) > 1:
                    console.section(service_data['name'])
                containers = find_containers(service_data['name'])
                if containers:
                    for container in containers:
                        run_stream = container.status == "running"
                        log_data = container.logs(timestamps=True, stream=run_stream, since=time_to_fetch)
                        for data in log_data:
                            if data:
                                line = data.decode('UTF-8').replace("\n", "")
                                if regex:
                                    ret = re.search(regex, line)
                                    if not ret:
                                        continue
                                show_log(container.name, line)
                    sleep(time_to_fetch)
                else:
                    logger.warning(
                        f"No running containers found for service: {service_data['name']}. Show last 100 lines.")
                    action = "logs"
                    options = ['tail=100']
                    run_compose_command(meg, action, service_data, options)
                    raise KeyboardInterrupt()
    except KeyboardInterrupt:
        sys.exit(0)
