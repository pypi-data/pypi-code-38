import copy
import json
from time import sleep
import threading

from docker import DockerClient
from docker.errors import NotFound, APIError, ContainerError
from json import JSONDecodeError

from riptide.config.document.config import Config
from riptide.config.document.service import Service

from riptide_engine_docker.container_builder import get_network_name, get_service_container_name, \
    ContainerBuilder, RIPTIDE_DOCKER_LABEL_IS_RIPTIDE, EENV_NO_STDOUT_REDIRECT, EENV_ORIGINAL_ENTRYPOINT
from riptide.engine.results import ResultQueue, ResultError, StartStopResultStep
from riptide.lib.cross_platform.cpuser import getuid, getgid

start_lock = threading.Lock()


def start(project_name: str, service: Service, client: DockerClient, queue: ResultQueue):
    """
    Starts the given service by starting the container (if not already started).

    Finishes when service was successfully started or an error occured.
    Updates the ResultQueue with status messages for this service, as specified by ResultStart.
    If an error during start occurs, an ResultError is added to the queue, indicating the kind of error.
    On errors, tries to execute stop after updating the queue.


    :param client:          Docker Client
    :param project_name:    Name of the project to start
    :param service:         Service object defining the service
    :param queue:           ResultQueue to update, or None
    """

    name = get_service_container_name(project_name, service["$name"])
    needs_to_be_started = False

    # 1. Check if already running
    queue.put(StartStopResultStep(current_step=1, steps=None, text='Checking...'))
    try:
        container = client.containers.get(name)
        if container.status != "running":
            container.remove()
            needs_to_be_started = True
    except NotFound:
        needs_to_be_started = True
    except APIError as err:
        queue.end_with_error(ResultError("ERROR checking container status.", cause=err))
        stop(project_name, service["$name"], client)
        return

    if needs_to_be_started:

        # Number of steps for progress bar:
        # check + image pull + start + check + 1 for each pre_start/post_start + "started"
        step_count = 5 + len(service["pre_start"]) + len(service["post_start"])
        current_step = 2

        # 2. Pulling image
        queue.put(StartStopResultStep(current_step=current_step, steps=step_count, text="Checking image... "))
        # Check if image exists
        try:
            client.images.get(service["image"])
        except NotFound:
            try:
                queue.put(StartStopResultStep(current_step=current_step, steps=step_count, text="Pulling image... "))
                image_name_full = service['image'] if ":" in service['image'] else service['image'] + ":latest"
                for line in client.api.pull(image_name_full, stream=True):
                    try:
                        status = json.loads(line)
                        if "progress" in status:
                            queue.put(StartStopResultStep(current_step=current_step, steps=step_count, text="Pulling image... " + status["status"] + " : " + status["progress"]))
                        else:
                            queue.put(StartStopResultStep(current_step=current_step, steps=step_count, text="Pulling image... " + status["status"]))
                    except JSONDecodeError:
                        queue.put(StartStopResultStep(current_step=current_step, steps=step_count, text="Pulling image... " + str(line)))
            except APIError as err:
                queue.end_with_error(ResultError("ERROR pulling image.", cause=err))
                stop(project_name, service["$name"], client)
                return

        # 2.5. Prepare container
        try:
            image_config = client.api.inspect_image(service["image"])["Config"]
            builder = ContainerBuilder(
                service["image"],
                service["command"] if "command" in service else image_config["Cmd"]
            )

            builder.set_name(name)
            builder.init_from_service(service, image_config)
            builder.set_hostname(service['$name'])
            # If src role is set, change workdir
            builder.set_workdir(service.get_working_directory())
        except Exception as ex:
            queue.end_with_error(ResultError("ERROR preparing container.", cause=ex))
            return

        # 3. Run pre start commands
        cmd_no = -1
        for cmd in service["pre_start"]:
            cmd_no = cmd_no + 1
            current_step += 1
            queue.put(StartStopResultStep(current_step=current_step, steps=step_count, text="Pre Start: " + cmd))
            try:
                # Remove first, just to be sure
                try:
                    client.containers.get(name + "__pre_start" + str(cmd_no)).stop()
                except APIError:
                    pass
                try:
                    client.containers.get(name + "__pre_start" + str(cmd_no)).remove()
                except APIError:
                    pass

                # Fork built container configuration and adjust it for pre start container
                pre_start_config = copy.deepcopy(builder.build_docker_api())
                pre_start_config.update({
                    'name': name + "__pre_start" + str(cmd_no),
                    'network': get_network_name(project_name),
                    # Don't use ports and labels of actual service container
                    'ports': None,
                    'labels': {RIPTIDE_DOCKER_LABEL_IS_RIPTIDE: '1'}
                })
                pre_start_config['environment'][EENV_NO_STDOUT_REDIRECT] = '1'
                pre_start_config['environment'][EENV_ORIGINAL_ENTRYPOINT] = '/bin/sh -c "' + cmd + '"'

                # RUN
                client.containers.run(**pre_start_config)
            except (APIError, ContainerError) as err:
                queue.end_with_error(ResultError("ERROR running pre start command '" + cmd + "'.", cause=err))
                stop(project_name, service["$name"], client)
                return

        # 4. Starting the container
        current_step += 1
        queue.put(StartStopResultStep(current_step=current_step, steps=step_count, text="Starting Container..."))

        try:
            # Lock here to prevent race conditions with port assignment
            with start_lock:
                builder.service_add_main_port(service)
                # RUN
                container = client.containers.run(**builder.build_docker_api(detach=True, remove=False))
                # Add container to network
                client.networks.get(get_network_name(project_name)).connect(container, aliases=[service["$name"]])
        except (APIError, ContainerError) as err:
            queue.end_with_error(ResultError("ERROR starting container.", cause=err))
            return

        # 4b. Checking if it actually started or just crashed immediately
        current_step += 1
        queue.put(StartStopResultStep(current_step=current_step, steps=step_count, text="Checking..."))
        sleep(3)
        try:
            container = client.containers.get(name)
            if container.status == "exited":
                extra = " Try 'run_as_current_user': false" if service["run_as_current_user"] else ""
                queue.end_with_error(ResultError("ERROR: Container crashed." + extra, details=container.logs().decode("utf-8")))
                container.remove()
                return
        except NotFound:
            queue.end_with_error(ResultError("ERROR: Container went missing."))
            return

        # 5. Execute Post Start commands via docker exec.
        cmd_no = -1
        for cmd in service["post_start"]:
            cmd_no = cmd_no + 1
            current_step += 1
            queue.put(StartStopResultStep(current_step=current_step, steps=step_count, text="Post Start: " + cmd))
            try:
                container.exec_run(
                    cmd=["/bin/sh", "-c", cmd],
                    detach=False,
                    tty=True,
                    user=str(getuid()) if service['run_as_current_user'] else None
                )
            except (APIError, ContainerError) as err:
                queue.end_with_error(ResultError("ERROR running post start command '" + cmd + "'.", cause=err))
                stop(project_name, service["$name"], client)
                return

        # 6. Done!
        current_step += 1
        queue.put(StartStopResultStep(current_step=current_step, steps=step_count, text="Started!"))
    else:
        queue.put(StartStopResultStep(current_step=2, steps=2, text='Already started!'))
    queue.end()


def stop(project_name: str, service_name: str, client: DockerClient, queue: ResultQueue=None):
    """
    Stops the given service by stopping the container (if not already started).

    Finishes when service was successfully stopped or an error occured.
    Updates the ResultQueue with status messages for this service, as specified by ResultStop.
    If an error during stop occurs, an ResultError is added to the queue, indicating the kind of error.

    The queue is optional.

    :param project_name:    Name of the project to start
    :param service_name:    Name of the service to start
    :param queue:           ResultQueue to update, or None
    """
    name = get_service_container_name(project_name, service_name)
    # 1. Check if already running
    if queue:
        queue.put(StartStopResultStep(current_step=1, steps=None, text='Checking...'))
    try:
        container = client.containers.get(name)
        # 2. Stop
        if queue:
            queue.put(StartStopResultStep(current_step=2, steps=3, text='Stopping...'))
        container.stop()
        container.remove()
        if queue:
            queue.put(StartStopResultStep(current_step=3, steps=3, text='Stopped!'))
    except NotFound:
        if queue:
            queue.put(StartStopResultStep(current_step=2, steps=2, text='Already stopped!'))
    except APIError as err:
        if queue:
            queue.end_with_error(ResultError("ERROR checking container status.", cause=err))
        return

    if queue:
        queue.end()


def status(project_name: str, service: Service, client: DockerClient, system_config: Config):
    # Get Container
    name = get_service_container_name(project_name, service["$name"])
    container_is_running = False
    try:
        container = client.containers.get(name)
        if container.status != "exited":
            container_is_running = True
    except NotFound:
        pass

    return container_is_running
