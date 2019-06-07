import riptide.lib.cross_platform.cppty as pty
from typing import List, Union

from docker.errors import NotFound, APIError, ImageNotFound

from riptide.config.document.command import Command
from riptide.config.document.project import Project
from riptide.config.document.service import Service
from riptide.config.files import CONTAINER_SRC_PATH, get_current_relative_src_path
from riptide.engine.abstract import ExecError

from riptide_engine_docker.container_builder import get_cmd_container_name, get_network_name, \
    get_service_container_name, ContainerBuilder, EENV_USER, EENV_GROUP, EENV_RUN_MAIN_CMD_AS_USER, \
    EENV_NO_STDOUT_REDIRECT
from riptide.lib.cross_platform.cpuser import getuid, getgid


def exec_fg(client, project: Project, service_name: str, cols=None, lines=None, root=False) -> None:
    """Open an interactive shell to one running service container"""
    if service_name not in project["app"]["services"]:
        raise ExecError("Service not found.")

    container_name = get_service_container_name(project["name"], service_name)
    service_obj = project["app"]["services"][service_name]

    user = getuid()
    user_group = getgid()

    try:
        container = client.containers.get(container_name)
        if container.status == "exited":
            container.remove()
            raise ExecError('The service is not running. Try starting it first.')

        # TODO: The Docker Python API doesn't seem to support interactive exec - use pty.spawn for now
        shell = ["docker", "exec", "-it"]
        if not root:
            shell += ["-u", str(user) + ":" + str(user_group)]
        if cols and lines:
            # Add COLUMNS and LINES env variables
            shell += ['-e', 'COLUMNS=' + str(cols), '-e', 'LINES=' + str(lines)]
        if "src" in service_obj["roles"]:
            # Service has source code, set workdir in container to current workdir
            shell += ["-w", CONTAINER_SRC_PATH + "/" + get_current_relative_src_path(project)]
        shell += [container_name, "sh", "-c", "if command -v bash >> /dev/null; then bash; else sh; fi"]
        pty.spawn(shell, win_repeat_argv0=True)

    except NotFound:
        raise ExecError('The service is not running. Try starting it first.')
    except APIError as err:
        raise ExecError('Error communicating with the Docker Engine.') from err


def service_fg(client, project: Project, service_name: str, arguments: List[str]) -> None:
    """Run a service in foreground"""
    if service_name not in project["app"]["services"]:
        raise ExecError("Service not found.")

    container_name = get_service_container_name(project['name'], service_name)
    command_obj = project["app"]["services"][service_name]

    fg(client, project, container_name, command_obj, arguments)


def cmd_fg(client, project: Project, command_name: str, arguments: List[str]) -> int:
    """Run a command in foreground, returns the exit code"""
    if command_name not in project["app"]["commands"]:
        raise ExecError("Command not found.")

    container_name = get_cmd_container_name(project['name'], command_name)
    command_obj = project["app"]["commands"][command_name]

    return fg(client, project, container_name, command_obj, arguments)


def fg(client, project: Project, container_name: str, exec_object: Union[Command, Service], arguments: List[str]) -> int:
    # TODO: Piping | <
    # TODO: Not only /src into container but everything

    # Check if image exists
    try:
        image = client.images.get(exec_object["image"])
        image_config = client.api.inspect_image(exec_object["image"])["Config"]
    except NotFound:
        print("Riptide: Pulling image... Your command will be run after that.")
        try:
            client.api.pull(exec_object['image'] if ":" in exec_object['image'] else exec_object['image'] + ":latest")
            image = client.images.get(exec_object["image"])
            image_config = client.api.inspect_image(exec_object["image"])["Config"]
        except ImageNotFound as ex:
            print("Riptide: Could not pull. The image was not found. Your command will not run :(")
            return
        except APIError as ex:
            print("Riptide: There was an error pulling the image. Your command will not run :(")
            print('    ' + str(ex))
            return

    builder = ContainerBuilder(
        exec_object["image"],
        exec_object["command"] if "command" in exec_object else image_config["Cmd"]
    )

    builder.set_workdir(CONTAINER_SRC_PATH + "/" + get_current_relative_src_path(project))
    builder.set_name(container_name)
    builder.set_network(get_network_name(project["name"]))

    builder.set_env(EENV_NO_STDOUT_REDIRECT, "yes")
    builder.set_args(arguments)

    if isinstance(exec_object, Service):
        builder.init_from_service(exec_object, image_config)
        builder.service_add_main_port(exec_object)
    else:
        builder.init_from_command(exec_object, image_config)
        builder.set_env(EENV_RUN_MAIN_CMD_AS_USER, "yes")
        builder.set_env(EENV_USER, str(getuid()))
        builder.set_env(EENV_GROUP, str(getgid()))

    # XXX: Needs to be shifted by 1 byte because the return value of os.waitpid is shifted for some reason???
    return pty.spawn(builder.build_docker_cli(), win_repeat_argv0=True) >> 8
