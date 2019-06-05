import re
import docker
from docker.errors import NotFound
from docker.models.containers import Container
from docker.models.images import Image
from typing import List, Union, Dict, Iterable, Callable
from swimlane_platform.lib.debug_decorators import debug_function_args, debug_function_return
from swimlane_platform.lib.expected_exceptions import ValidationException
from swimlane_platform.lib.logger import SplitStreamLogger


class DockerManager:

    def __init__(self, logger):
        # type: (SplitStreamLogger) -> DockerManager
        self.client = docker.from_env()
        self.logger = logger

    @debug_function_args
    def image_run_command(self, image_name, command, name, env=None, volumes=None, network=None):
        # type: (str, Union[str, List[str]], str, Union[List[str], Dict[str, str]], Dict[str, object], str) -> Iterable
        """
        Docker run command with stderr and stream set to true by default. And forced parameters.
        :param image_name: Image name
        :param command: Command
        :param name: Container name. Needed for later removing.
        :param env: Environmental variables.
        :param volumes: Volumes.
        :param network: Network name.
        :return: Logs.
        """
        return self.client.containers.run(image_name,
                                          command=command,
                                          name=name,
                                          stderr=True,
                                          stream=True,
                                          environment=env,
                                          volumes=volumes,
                                          network=network)

    @debug_function_args
    def image_pull(self, image_name):
        # type: (str) -> None
        """
        Pulls image from repository.
        :param image_name: Repository+Image Tag
        """
        return self.client.images.pull(image_name)

    @debug_function_args
    def container_remove(self, name):
        # type: (str) -> None
        """
        Removes used container.
        :param name: Name of a container.
        """
        try:
            container = self.client.containers.get(name)
            container.remove(force=True)
        except NotFound:
            pass

    @debug_function_args
    def container_stop(self, container):
        # type: (Container) -> None
        """
        Stops container if it is running.
        :param container: The container.
        """
        if container.status == 'running':
            container.stop()

    @debug_function_args
    def container_start(self, container):
        # type: (Container) -> None
        """
        Starts container if it was stopped.
        :param container: The container.
        """
        if container.status != 'running':
            container.start()

    @debug_function_return
    @debug_function_args
    def container_get_network_name(self, container_name):
        # type: (str) -> str
        """
        Gets the name of the network specified container connected to.
        :param container_name: container name.
        :return: network name.
        """
        container = self.container_get(container_name)
        return container.attrs["HostConfig"]["NetworkMode"] if container else None

    @debug_function_return
    @debug_function_args
    def container_get_dotnet_env(self, container_name):
        # type: (str) -> List[str]
        """
        Gets the environment variables related to dotnet in the specified container.
        :param container_name: container name.
        :return: List of environment variables key=value.
        """
        container = self.container_get(container_name)
        if not container:
            return []
        return [env for env in (container.attrs["Config"]["Env"]) if re.search("__.+(?==)", env)]

    @debug_function_return
    @debug_function_args
    def container_check_volume_mapped(self, container, folder_path):
        # type: (Container, str) -> bool
        """
        Checks if pre-requisite volume is attached.
        :param container: Docker container.
        :param folder_path: path the volume is mapped to.
        """
        mounts = container.attrs['Mounts']
        mount = [mount for mount in mounts if mount['Destination'] == folder_path]
        return bool(mount)

    @debug_function_args
    def containers_run(self, func, *names):
        # type: (Callable, str) -> None
        """Runs specified function on the specified containers.
        :param func: Function to run.
        :param names: arg list of container names (could be partials)
        """
        for container in self.containers_get(*names):
            func(container)

    @debug_function_return
    @debug_function_args
    def containers_get(self, *names):
        # type: (str) -> List[Container]
        """
        Returns containers (running and stopped) by name.
        :param names: Names of containers.
        :return: Containers.
        """
        containers = self.client.containers.list(all=True)
        return [container for name in names for container in containers if str(container.name).find(name) != -1]

    @debug_function_return
    @debug_function_args
    def container_get(self, name):
        # type: (str) -> Union[Container, None]
        """
        Returns container (running and stopped) by name.
        :param name: Name of container.
        :return: Container.
        """
        try:
            return self.client.containers.get(name)
        except NotFound:
            return None

    @debug_function_args
    def containers_exists_validate(self, *names):
        # type: (str) -> None
        """
        Throws validation exceptions if one of the names is not found.
        :param names: Names of the containers.
        """
        result = self.containers_get(*names)
        if len(result) != len(names):
            found = [container.name for container in result]
            not_found = ','.join([name for name in names if name not in found])
            raise ValidationException("Container(s) {name} not found.".format(name=not_found))

    @debug_function_return
    @debug_function_args
    def containers_get_state(self, *names):
        # type: (str) -> Dict[str, str]
        """
        Returns dictionary of container names and their statuses.
        :param names: Container names.
        :return: Container statuses.
        """
        return dict(((container.name, container.status) for container in self.containers_get(*names)))

    @debug_function_return
    @debug_function_args
    def container_restore_state(self, states):
        # type: (Dict[str, str]) -> None
        """
        Starts containers that were running and stops the ones that weren't
        :param states: Container statuses.
        """
        if not states:
            return
        running = 'running'
        containers = self.containers_get(*states.keys())
        for container in containers:
            existing = container.status
            pre_existing = states[container.name]
            if pre_existing != running and existing == running:
                self.container_stop(container)
            elif pre_existing == running and existing != running:
                self.container_start(container)

    @property
    def images(self):
        # type: () -> List[Image]
        """
        All available images on the host.
        :return: List of images (info)
        """
        return self.client.images.list(all=True)

    @debug_function_return
    def images_get_tags(self):
        # type: () -> List[str]
        """
        Get all available images tags.
        :return: List of tag names.
        """
        return [image.tags[0] for image in self.images if image.tags]

    @debug_function_return
    def images_get_tags(self):
        # type: () -> List[str]
        """
        Get all available images tags.
        :return: List of tag names.
        """
        return [image.tags[0] for image in self.images if image.tags]

    @debug_function_args
    def image_remove(self, image_name):
        # type: (str) -> None
        try:
            self.client.images.remove(image_name)
        except NotFound:
            pass

    @debug_function_args
    def volume_remove(self, volume_name):
        # type: (str) -> None
        """
        Removes volume (running and stopped) by name.
        :param volume_name: The name of the volume.
        """
        try:
            volume = self.client.volumes.get(volume_name)
            volume.remove()
        except NotFound:
            pass
