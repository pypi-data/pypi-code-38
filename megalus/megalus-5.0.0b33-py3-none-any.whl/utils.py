"""Utils Module."""
import datetime
import hashlib
import os
import re
import shutil
from pathlib import Path
from typing import List

import docker
from docker import DockerClient
from loguru import logger

client = docker.from_env()


def find_containers(service: str) -> List[DockerClient]:
    """Find eligible containers for selected service.

    :param service: docker service to run command.
    :return: list of DockerClient containers.
    """
    eligible_containers = [
        container
        for container in client.containers.list()
        if "_{}_".format(service) in container.name
    ]
    return eligible_containers


def backup_folder(folder_path: str) -> None:
    """Backup service context folder.

    :param folder_path: service context folder path
    :return: None
    """
    folders = list(Path(folder_path).parts)
    folder_hash = hashlib.md5(datetime.datetime.now().isoformat().encode("utf-8")).hexdigest()
    last_folder = "{}_{}".format(folders[-1], folder_hash[:10])
    folders.remove(folders[-1])
    folders.append(last_folder)
    backup_path = os.path.join(*folders)
    logger.warning('Directory already exists. Moving folder to {}'.format(backup_path))
    shutil.move(folder_path, backup_path)


def get_path(path: str, base_path: str) -> str:
    """Return real path from string.

    Converts environment variables to path
    Converts relative path to full path
    """

    def _convert_env_to_path(env_in_path):
        s = re.search(r"\${(\w+)}", env_in_path)
        if not s:
            s = re.search(r"(\$\w+)", env_in_path)
        if s:
            env = s.group(1).replace("$", "")
            name = os.environ.get(env)
            if not name:
                raise ValueError("Can't find value for {}".format(env))
            path_list = [
                part if "$" not in part else name
                for part in env_in_path.split("/")
            ]
            path = os.path.join(*path_list)
        else:
            raise ValueError("Cant find path for {}".format(env_in_path))
        return path

    if "$" in base_path:
        base_path = _convert_env_to_path(base_path)
    if "$" in path:
        path = _convert_env_to_path(path)
    if path.startswith("."):
        list_path = os.path.join(base_path, path)
        path = os.path.abspath(list_path)
    return path
