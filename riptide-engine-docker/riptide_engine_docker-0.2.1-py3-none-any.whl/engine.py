import asyncio

import docker
import json
from json import JSONDecodeError
from typing import Tuple, Dict, Union, List

from docker.errors import APIError

from riptide.config.document.command import Command
from riptide.config.document.config import Config
from riptide.config.document.project import Project
from riptide.engine.abstract import AbstractEngine
from riptide_engine_docker import network, service, path_utils
from riptide_engine_docker.cmd_detached import cmd_detached
from riptide_engine_docker.container_builder import get_service_container_name, RIPTIDE_DOCKER_LABEL_HTTP_PORT
from riptide.engine.project_start_ctx import riptide_start_project_ctx
from riptide.engine.results import StartStopResultStep, MultiResultQueue, ResultQueue, ResultError
from riptide_engine_docker.fg import exec_fg, cmd_fg, service_fg


class DockerEngine(AbstractEngine):

    def __init__(self):
        self.client = docker.from_env()
        self.ping()

    def start_project(self, project: Project, services: List[str]) -> MultiResultQueue[StartStopResultStep]:
        with riptide_start_project_ctx(project):
            # Start network
            network.start(self.client, project["name"])

            # Start all services
            queues = {}
            loop = asyncio.get_event_loop()
            for service_name in services:
                # Create queue and add to queues
                queue = ResultQueue()
                queues[queue] = service_name
                if service_name in project["app"]["services"]:
                    # Run start task
                    loop.run_in_executor(
                        None,
                        service.start,

                        project["name"],
                        project["app"]["services"][service_name],
                        self.client,
                        queue
                    )
                else:
                    # Services not found :(
                    queue.end_with_error(ResultError("Service not found."))

            return MultiResultQueue(queues)

    def stop_project(self, project: Project, services: List[str]) -> MultiResultQueue[StartStopResultStep]:
        # Stop all services
        queues = {}
        loop = asyncio.get_event_loop()

        for service_name in services:
            # Create queue and add to queues
            queue = ResultQueue()
            queues[queue] = service_name
            # Run stop task
            loop.run_in_executor(
                None,
                service.stop,

                project["name"],
                service_name,
                self.client,
                queue
            )

        return MultiResultQueue(queues)

    def status(self, project: Project, system_config: Config) -> Dict[str, bool]:
        services = {}
        for service_name, service_obj in project["app"]["services"].items():
            services[service_name] = service.status(project["name"], service_obj, self.client, system_config)
        return services

    def address_for(self, project: Project, service_name: str) -> Union[None, Tuple[str, int]]:
        #       TODO doku BA hin und her!
        if "port" not in project["app"]["services"][service_name]:
            return None

        container_name = get_service_container_name(project["name"], service_name)
        try:
            container = self.client.containers.get(container_name)
            if container.status != "running":
                return None
            port = container.labels[RIPTIDE_DOCKER_LABEL_HTTP_PORT]
            return "127.0.0.1", port
        except KeyError:
            return None
        except APIError:
            return None

    def cmd(self, project: Project, command_name: str, arguments: List[str]) -> int:
        # Start network
        network.start(self.client, project["name"])

        return cmd_fg(self.client, project, command_name, arguments)

    def service_fg(self, project: Project, service_name: str, arguments: List[str]) -> None:
        # Start network
        network.start(self.client, project["name"])

        with riptide_start_project_ctx(project):
            service_fg(self.client, project, service_name, arguments)

    def exec(self, project: Project, service_name: str, cols=None, lines=None, root=False) -> None:
        exec_fg(self.client, project, service_name, cols, lines, root)

    def supports_exec(self):
        return True

    def ping(self):
        try:
            self.client.ping()
        except Exception as err:
            raise ConnectionError("Connection with Docker Daemon failed") from err

    def cmd_detached(self, project: 'Project', command: 'Command', run_as_root=False):
        # Start network
        network.start(self.client, project["name"])
        command.parent_doc = project["app"]

        return cmd_detached(self.client, project, command, run_as_root)

    def pull_images(self, project: 'Project', line_reset='\n', update_func=lambda msg: None) -> None:
        if "services" in project["app"]:
            for name, service in project["app"]["services"].items():
                update_func("[service/%s] Pulling '%s':\n" % (name, service["image"]))
                self.__pull_image(service['image'] if ":" in service['image'] else service['image'] + ":latest",
                                  line_reset, update_func)

        if "commands" in project["app"]:
            for name, command in project["app"]["commands"].items():
                if "image" in command:
                    update_func("[command/%s] Pulling '%s':\n" % (name, command["image"]))
                    self.__pull_image(command['image'] if ":" in command['image'] else command['image'] + ":latest",
                                      line_reset, update_func)

        update_func("Done!\n\n")

    def path_rm(self, path, project: 'Project'):
        return path_utils.rm(self, path, project)

    def path_copy(self, fromm, to, project: 'Project'):
        return path_utils.copy(self, fromm, to, project)

    def __pull_image(self, image_name, line_reset, update_func):
        try:
            for line in self.client.api.pull(image_name, stream=True):
                try:
                    status = json.loads(line)
                    if "progress" in status:
                        update = status["status"] + " : " + status[ "progress"]
                    else:
                        update = status["status"]
                except JSONDecodeError:
                    update = line
                update_func("%s    %s" % (line_reset, update))
            update_func("%s    Done!\n" % line_reset)
        except APIError as ex:
            if "404 Client Error: Not Found " in str(ex):
                update_func("%s    Warning: Image not found in repository.\n" % line_reset)
            else:
                raise
