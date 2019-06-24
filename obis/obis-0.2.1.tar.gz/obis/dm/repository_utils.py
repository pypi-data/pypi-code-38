import os
import socket
from .commands.openbis_command import CommandResult
from .utils import run_shell


def copy_repository(ssh_user, host, path):
    # abort if local folder already exists
    repository_folder = path.split('/')[-1]
    if os.path.exists(repository_folder):
        return CommandResult(returncode=-1, output="Folder for repository to clone already exists: " + repository_folder)
    # check if local or remote
    location = get_repository_location(ssh_user, host, path)
    # copy repository
    return run_shell(["rsync", "--progress", "-av", location, "."])


def delete_repository(ssh_user, host, path):
    if is_local(host):
        result = run_shell(["chmod", "-R",  "u+w", path])
        if result.failure():
            return result
        return run_shell(["rm", "-rf", path])
    else:
        location = ssh_user + "@" if ssh_user is not None else ""
        location += host
        return run_shell(["ssh", location, "rm -rf " + path])


def is_local(host):
    return host == socket.gethostname()


def get_repository_location(ssh_user, host, path):
    if is_local(host):
        location = path
    else:
        location = ssh_user + "@" if ssh_user is not None else ""
        location += host + ":" + path
    return location
