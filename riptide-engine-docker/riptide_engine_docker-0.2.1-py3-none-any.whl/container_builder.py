"""Container builder module."""
from collections import OrderedDict

import os
import platform
from typing import List, Union

from docker.types import Mount

from riptide.config.document.command import Command
from riptide.config.document.service import Service
from riptide.config.service.ports import find_open_port_starting_at
from riptide.lib.cross_platform.cpuser import getgid, getuid
from riptide_engine_docker.assets import riptide_engine_docker_assets_dir

ENTRYPOINT_SH = 'entrypoint.sh'

RIPTIDE_DOCKER_LABEL_IS_RIPTIDE = 'riptide'
RIPTIDE_DOCKER_LABEL_SERVICE = "riptide_service"
RIPTIDE_DOCKER_LABEL_PROJECT = "riptide_project"
RIPTIDE_DOCKER_LABEL_MAIN = "riptide_main"
RIPTIDE_DOCKER_LABEL_HTTP_PORT = "riptide_port"

ENTRYPOINT_CONTAINER_PATH = '/entrypoint_riptide.sh'
EENV_DONT_RUN_CMD = "RIPTIDE__DOCKER_DONT_RUN_CMD"
EENV_USER = "RIPTIDE__DOCKER_USER"
EENV_USER_RUN = "RIPTIDE__DOCKER_USER_RUN"
EENV_GROUP = "RIPTIDE__DOCKER_GROUP"
EENV_RUN_MAIN_CMD_AS_USER = "RIPTIDE__DOCKER_RUN_MAIN_CMD_AS_USER"
EENV_ORIGINAL_ENTRYPOINT = "RIPTIDE__DOCKER_ORIGINAL_ENTRYPOINT"
EENV_COMMAND_LOG_PREFIX = "RIPTIDE__DOCKER_CMD_LOGGING_"
EENV_NO_STDOUT_REDIRECT = "RIPTIDE__DOCKER_NO_STDOUT_REDIRECT"

# For services map HTTP main port to a host port starting here
DOCKER_ENGINE_HTTP_PORT_BND_START = 30000


class ContainerBuilder:
    """
    ContainerBuilder.
    Builds Riptide Docker containers for use with the Python API and
    the Docker CLI
    """
    def __init__(self, image: str, command: Union[List, str, None]) -> None:
        """Create a new container builder. Specify image and command to run."""
        self.env = OrderedDict()
        self.labels = OrderedDict()
        self.mounts = OrderedDict()
        self.ports = OrderedDict()
        self.network = None
        self.name = None
        self.entrypoint = None
        self.command = command
        self.args = []
        self.work_dir = None
        self.image = image
        self.set_label(RIPTIDE_DOCKER_LABEL_IS_RIPTIDE, "1")
        self.run_as_root = False
        self.hostname = None

    def set_env(self, name: str, val: str):
        self.env[name] = val
        return self

    def set_label(self, name: str, val: str):
        self.labels[name] = val
        return self

    def set_mount(self, host_path: str, container_path: str, mode='rw'):
        self.mounts[host_path] = Mount(
            target=container_path,
            source=host_path,
            type='bind',
            read_only=mode == 'ro',
            consistency='delegated'  # Performance setting for Docker Desktop on Mac
        )
        return self

    def set_port(self, cnt: int, host: int):
        self.ports[cnt] = host
        return self

    def set_network(self, network: str):
        self.network = network
        return self

    def set_name(self, name: str):
        self.name = name
        return self

    def set_entrypoint(self, entrypoint: str):
        self.entrypoint = entrypoint
        return self

    def set_args(self, args: List[str]):
        self.args = args
        return self

    def set_workdir(self, work_dir: str):
        self.work_dir = work_dir
        return self

    def set_hostname(self, hostname: str):
        self.hostname = hostname
        return self

    def enable_riptide_entrypoint(self, image_config):
        """Add the Riptide entrypoint script and configure it."""
        # The original entrypoint of the image is replaced with
        # this custom entrypoint script, which may call the original entrypoint
        # if present

        # If the entrypoint is enabled, then run the entrypoint
        # as root. It will handle the rest.
        self.run_as_root = True
        entrypoint_script = os.path.join(riptide_engine_docker_assets_dir(), ENTRYPOINT_SH)
        self.set_mount(entrypoint_script, ENTRYPOINT_CONTAINER_PATH, 'ro')

        # Collect entrypoint settings
        for key, val in parse_entrypoint(image_config["Entrypoint"]).items():
            self.set_env(key, val)

        self.set_entrypoint(ENTRYPOINT_CONTAINER_PATH)

        return self

    def _init_common(self, doc: Union[Service, Command], image_config):
        self.enable_riptide_entrypoint(image_config)
        # Add volumes
        for host, volume in doc.collect_volumes().items():
            self.set_mount(host, volume['bind'], volume['mode'] or 'rw')
        # Collect environment
        for key, val in doc.collect_environment().items():
            self.set_env(key, val)

    def init_from_service(self, service: Service, image_config):
        """
        Initialize some data of this builder with the given service object.
        You need to call service_add_main_port separately.
        """
        self._init_common(service, image_config)
        # Collect labels
        labels = service_collect_labels(service, service.get_project()["name"])
        # Collect (and process!) additional_ports
        ports = service.collect_ports()
        # All command logging commands are added as environment variables for the
        # riptide entrypoint
        environment_updates = service_collect_logging_commands(service)
        # User settings for the entrypoint
        environment_updates.update(service_collect_entrypoint_user_settings(service, getuid(), getgid(), image_config))
        # Add to builder
        for key, value in environment_updates.items():
            self.set_env(key, value)
        for name, val in labels.items():
            self.set_label(name, val)
        for container, host in ports.items():
            self.set_port(container, host)
        return self

    def service_add_main_port(self, service: Service):
        """
        Add main service port.
        Not thread-safe!
        If starting multiple services in multiple threads:
            This has to be done separately, right before start,
            and with a lock in place, so that multiple service starts don't reserve the
            same port.
        """
        if "port" in service:
            main_port = find_open_port_starting_at(DOCKER_ENGINE_HTTP_PORT_BND_START)
            self.set_label(RIPTIDE_DOCKER_LABEL_HTTP_PORT, str(main_port))
            self.set_port(service["port"], main_port)

    def init_from_command(self, command: Command, image_config):
        """
        Initialize some data of this builder with the given command object.
        """
        self._init_common(command, image_config)
        return self

    def build_docker_api(self, detach=False, remove=True) -> dict:
        """
        Build the docker container in the form of Docker API containers.run arguments.

        :param detach: Whether or not to set the detach option.
        :param remove: Whether or not to set the remove option.
        """
        args = {
            'detach': detach,
            'remove': remove,
            'image': self.image
        }

        if self.command is None:
            args['command'] = None
        elif isinstance(self.command, str):

            # COMMAND IS STRING
            args['command'] = self.command
            if len(self.args) > 0:
                args['command'] += " " + " ".join('"{0}"'.format(w) for w in self.args)

        else:

            list_command = self.command.copy()
            # COMMAND IS LIST
            if len(self.args) > 0:
                list_command += self.args

            # Strange Docker API Bug (?) requires args with spaces to be quoted...
            args['command'] = []
            for item in list_command:
                if " " in item:
                    args['command'].append('"' + item + '"')
                else:
                    args['command'].append(item)

        if self.name:
            args['name'] = self.name
        if self.network:
            args['network'] = self.network
        if self.entrypoint:
            args['entrypoint'] = [self.entrypoint]
        if self.work_dir:
            args['working_dir'] = self.work_dir
        if self.run_as_root:
            args['user'] = 0
        if self.hostname:
            args['hostname'] = self.hostname

        args['environment'] = self.env
        args['labels'] = self.labels
        args['ports'] = self.ports
        args['mounts'] = list(self.mounts.values())

        return args

    def build_docker_cli(self) -> List[str]:
        """
        Build the docker container in the form of a Docker CLI command.
        """
        shell = [
            "docker", "run", "--rm", "-it"
        ]
        if self.name:
            shell += ["--name", self.name]
        if self.network:
            shell += ["--network", self.network]
        if self.entrypoint:
            shell += ["--entrypoint", self.entrypoint]
        if self.work_dir:
            shell += ["-w", self.work_dir]
        if self.run_as_root:
            shell += ["-u", str(0)]
        if self.hostname:
            shell += ["--hostname", self.hostname]

        for key, value in self.env.items():
            shell += ['-e', key + '=' + value]

        for key, value in self.labels.items():
            shell += ['--label', key + '=' + value]

        for container, host in self.ports.items():
            shell += ['-p', str(host) + ':' + str(container)]

        # Mac: Add delegated
        mac_add = ':delegated' if platform.system().lower().startswith('mac') else ''
        for mount in self.mounts.values():
            mode = 'ro' if mount['ReadOnly'] else 'rw'
            shell += ['-v',
                      mount['Source'] + ':' + mount['Target'] + ':' + mode + mac_add]

        command = self.command
        if command is None:
            command = ""
        if isinstance(command, list):
            command = self.command[0]
            # If the command itself contains arguments, they have to be joined with
            # quotes, just like self.args
            if len(self.command) > 1:
                command += " " + " ".join('"{0}"'.format(w) for w in self.command[1:])

        shell += [
            self.image,
            (command + " " + " ".join('"{0}"'.format(w) for w in self.args)).rstrip()
        ]
        return shell


def get_cmd_container_name(project_name: str, command_name: str):
    return 'riptide__' + project_name + '__cmd__' + command_name + '__' + str(os.getpid())


def get_network_name(project_name: str):
    return 'riptide__' + project_name


def get_service_container_name(project_name: str, service_name: str):
    return 'riptide__' + project_name + '__' + service_name


def parse_entrypoint(entrypoint):
    """
    Parse the original entrypoint of an image and return a map of variables for the riptide entrypoint script.
    RIPTIDE__DOCKER_ORIGINAL_ENTRYPOINT: Original entrypoint as string to be used with exec.
                                         Empty if original entrypoint is not set.
    RIPTIDE__DOCKER_DONT_RUN_CMD:        true or unset.
                                         When the original entrypoint is a string, the command does not get run.
                                         See table at https://docs.docker.com/engine/reference/builder/#shell-form-entrypoint-example
    """
    # Is the original entrypoint set?
    if not entrypoint:
        return {EENV_ORIGINAL_ENTRYPOINT: ""}
    # Is the original entrypoint shell or exec format?
    if isinstance(entrypoint, list):
        # exec format
        # Turn the list into a string, but quote all arguments
        command = entrypoint.pop(0)
        arguments = " ".join(['"%s"' % entry for entry in entrypoint])
        return {
            EENV_ORIGINAL_ENTRYPOINT: command + " " + arguments
        }
    else:
        # shell format
        return {
            EENV_ORIGINAL_ENTRYPOINT: "/bin/sh -c " + entrypoint,
            EENV_DONT_RUN_CMD: "true"
        }
    pass


def service_collect_logging_commands(service: Service) -> dict:
    """Collect logging commands environment variables for this service"""
    environment = {}
    if "logging" in service and "commands" in service["logging"]:
        for cmdname, command in service["logging"]["commands"].items():
            environment[EENV_COMMAND_LOG_PREFIX + cmdname] = command
    return environment


def service_collect_entrypoint_user_settings(service: Service, user, user_group, image_config) -> dict:
    environment = {}

    if not service["dont_create_user"]:
        environment[EENV_USER] = str(user)
        environment[EENV_GROUP] = str(user_group)

    if service["run_as_current_user"]:
        # Run with the current system user
        environment[EENV_RUN_MAIN_CMD_AS_USER] = "yes"
    elif "User" in image_config and image_config["User"] != "":
        # If run_as_current_user is false and an user is configured in the image config, tell the entrypoint to run
        # with this user
        environment[EENV_RUN_MAIN_CMD_AS_USER] = "yes"
        environment[EENV_USER_RUN] = image_config["User"]

    return environment


def service_collect_labels(service: Service, project_name):
    labels = {
        RIPTIDE_DOCKER_LABEL_IS_RIPTIDE: '1',
        RIPTIDE_DOCKER_LABEL_PROJECT: project_name,
        RIPTIDE_DOCKER_LABEL_SERVICE: service["$name"],
        RIPTIDE_DOCKER_LABEL_MAIN: "0"
    }
    if "roles" in service and "main" in service["roles"]:
        labels[RIPTIDE_DOCKER_LABEL_MAIN] = "1"
    return labels
