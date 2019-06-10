# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from __future__ import print_function

import docker
import io
import json
import logging
import os
import posixpath
import re
import requests
import subprocess
import sys
import tarfile
import tempfile
import time
import traceback
import uuid

from azureml._model_management._constants import DOCKER_IMAGE_HTTP_PORT
from azureml._model_management._constants import HEALTH_CHECK_INTERVAL_SECONDS
from azureml._model_management._constants import MAX_HEALTH_CHECK_TRIES
from azureml._model_management._constants import MMS_SYNC_TIMEOUT_SECONDS
from azureml._model_management._constants import WEBSERVICE_SCORE_PATH
from azureml._restclient.artifacts_client import ArtifactsClient
from azureml._restclient.clientbase import ClientBase
from azureml._vendor.azure_storage.common.storageclient import logger
from azureml.exceptions import WebserviceException
from keyword import iskeyword
from pkg_resources import resource_string

try:
    # python 3
    from urllib.parse import urlparse
except ImportError:
    # python 2
    from urlparse import urlparse


model_payload_template = json.loads(resource_string(__name__, 'data/mms_model_payload_template.json').decode('ascii'))
image_payload_template = json.loads(resource_string(__name__,
                                                    'data/mms_workspace_image_payload_template.json').decode('ascii'))
profile_payload_template = json.loads(resource_string(__name__,
                                                      'data/mms_profile_payload_template.json').decode('ascii'))
aks_service_payload_template = json.loads(resource_string(__name__,
                                                          'data/aks_service_payload_template.json').decode('ascii'))
aci_service_payload_template = json.loads(resource_string(__name__,
                                                          'data/aci_service_payload_template.json').decode('ascii'))

logger.setLevel(logging.CRITICAL)
module_logger = logging.getLogger(__name__)
_session = None


def add_sdk_to_requirements():
    """
    Inject the SDK as a requirement for created images, since we use the SDK for schema and exception handling.
    :return: Path to the created pip-requirements file.
    :rtype: str
    """
    # always pass sdk as dependency to mms/ICE.
    generated_requirements = tempfile.mkstemp(suffix='.txt', prefix='requirements')[1]
    sdk_requirements_string = 'azureml-model-management-sdk==1.0.1b6.post1'
    with open(generated_requirements, 'w') as generated_requirements_file:
        generated_requirements_file.write(sdk_requirements_string)

    return generated_requirements


def create_tar_in_memory(files):
    """
    Construct a tar file in-memory.
    :param files: Sequence of (path, data) tuples.
    :type files: list
    :return: Tar file.
    :rtype: File-like object.
    """
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode='w') as tarf:
        def add_entry(name, content):
            tarinfo = tarfile.TarInfo(name)
            tarinfo.mtime = time.time()
            tarinfo.size = len(content)
            tarf.addfile(tarinfo, io.BytesIO(content))

        for path, data in files:
            if isinstance(data, bytes):
                add_entry(path, data)
            elif isinstance(data, str):
                # Assume data is a local path.
                if os.path.isdir(data):
                    for dirpath, _, filenames in os.walk(data):
                        for filename in filenames:
                            fullpath = os.path.join(dirpath, filename)
                            relpath = os.path.relpath(fullpath, start=data)

                            with open(fullpath, 'rb') as f:
                                add_entry(posixpath.join(path, *relpath.split(os.sep)), f.read())
                else:
                    # Assume data is a path to a regular file.
                    with open(data, 'rb') as f:
                        add_entry(path, f.read())
            else:
                # Assume data is file-like.
                add_entry(path, data.read())

    # Rewind so read() starts from the beginning
    output.seek(0)

    return output


def upload_dependency(workspace, dependency, create_tar=False, arcname=None):
    """
    :param workspace: AzureML workspace
    :type workspace: workspace: azureml.core.workspace.Workspace
    :param dependency: path (local, http[s], or wasb[s]) to dependency
    :type dependency: str
    :param create_tar: tar creation flag. Defaults to False
    :type create_tar: bool
    :param arcname: arcname to use for tar
    :type arcname: str
    :return: (str, str): uploaded_location, dependency_name
    """
    artifact_client = ArtifactsClient(workspace.service_context)
    if dependency.startswith('http') or dependency.startswith('wasb'):
        return dependency, urlparse(dependency).path.split('/')[-1]
    if not os.path.exists(dependency):
        raise WebserviceException('Error resolving dependency: '
                                  'no such file or directory {}'.format(dependency), logger=module_logger)

    dependency = dependency.rstrip(os.sep)
    dependency_name = os.path.basename(dependency)
    dependency_path = dependency

    if create_tar:
        dependency_name = str(uuid.uuid4())[:8] + '.tar.gz'
        tmpdir = tempfile.mkdtemp()
        dependency_path = os.path.join(tmpdir, dependency_name)
        dependency_tar = tarfile.open(dependency_path, 'w:gz')
        dependency_tar.add(dependency, arcname=arcname) if arcname else dependency_tar.add(dependency)
        dependency_tar.close()

    origin = 'LocalUpload'
    container = '{}'.format(str(uuid.uuid4())[:8])
    result = artifact_client.upload_artifact_from_path(dependency_path, origin, container, dependency_name)
    artifact_content = result.artifacts[dependency_name]
    dependency_name = artifact_content.path
    uploaded_location = "aml://artifact/" + artifact_content.artifact_id
    return uploaded_location, dependency_name


def wrap_execution_script_with_source_directory(source_directory, execution_script, log_aml_debug):
    """
    Wrap the user's execution script in our own in order to provide schema validation.
    :param execution_script: str path to execution script
    :param schema_file: str path to schema file
    :param dependencies: list of str paths to dependencies
    :return: str path to wrapped execution script
    """
    new_script_loc = tempfile.mkstemp(suffix='.py')[1]

    execution_script = os.path.join(source_directory, execution_script).replace(os.sep, '/')

    return generate_main(execution_script, '', new_script_loc, log_aml_debug, source_directory)


def wrap_execution_script(execution_script, schema_file, dependencies, log_aml_debug):
    """
    Wrap the user's execution script in our own in order to provide schema validation.
    :param execution_script: str path to execution script
    :param schema_file: str path to schema file
    :param dependencies: list of str paths to dependencies
    :return: str path to wrapped execution script
    """
    new_script_loc = tempfile.mkstemp(suffix='.py')[1]
    dependencies.append(execution_script)
    if not os.path.exists(execution_script):
        raise WebserviceException('Path to execution script {} does not exist.'.format(execution_script),
                                  logger=module_logger)
    if not schema_file:
        schema_file = ''
    else:
        # Fix path references in schema file,
        # since the container it will run in is a Linux container
        path_components = schema_file.split(os.sep)
        schema_file = "/".join(path_components)
    return generate_main(execution_script, schema_file, new_script_loc, log_aml_debug)


def generate_main(user_file, schema_file, main_file_name, log_aml_debug, source_directory=None):
    """

    :param user_file: str path to user file with init() and run()
    :param schema_file: str path to user schema file
    :param main_file_name: str full path of file to create
    :return: str filepath to generated file
    """

    data_directory = os.path.join(os.path.dirname(__file__), 'data')
    source_directory_import = ''
    if source_directory:
        source_directory_import = "sys.path.append(\'./{}\')".format(source_directory)
    main_template_path = os.path.join(data_directory, 'main_template.txt')

    with open(main_template_path) as template_file:
        main_src = template_file.read()

    main_src = main_src.replace('<user_script>', user_file)\
        .replace('<schema_file>', schema_file)\
        .replace('<log_debug_statements>', str(log_aml_debug))\
        .replace('<source_directory_import>', source_directory_import)
    with open(main_file_name, 'w') as main_file:
        main_file.write(main_src)
    return main_file_name


def _validate_schema_version(schema_file):
    with open(schema_file, 'r') as outfile:
        schema_json = json.load(outfile)

    if "input" in schema_json:
        for key in schema_json["input"]:
            _check_inout_item_schema_version(schema_json["input"][key])
            break
    elif "output" in schema_json:
        for key in schema_json["input"]:
            _check_inout_item_schema_version(schema_json["output"][key])
            break


def _check_inout_item_schema_version(item_schema):
    _pup_version = "0.1.0a11"
    _schema_version_error_format = "The given schema cannot be loaded because it was generated on a SDK version - " \
                                   "{} that is not compatible with the one used to create the ML service - {}. " \
                                   "Please either update the SDK to the version for which the schema was generated, " \
                                   "or regenerate the schema file with the currently installed version of the SDK.\n" \
                                   "You can install the latest SDK with:\n" \
                                   "\t pip install azureml-model-management-sdk --upgrade\n " \
                                   "or upgrade to an earlier version with:\n" \
                                   "\t pip install azureml-model-management-sdk=<version>"
    if "version" not in item_schema:
        schema_version = _pup_version
    else:
        schema_version = item_schema["version"]

    # Check here if the schema version matches the current running SDK version (major version match)
    # and error out if not, since we do not support cross major version backwards compatibility.
    # Exception is given if schema is assumed to be _pup_version since the move from that to 1.0 was
    # not considered a major version release, and we should not fail for all PUP customers.
    sdk_version = '1.0.1b6'
    current_major = int(sdk_version.split('.')[0])
    deserialized_schema_major = int(schema_version.split('.')[0])
    if schema_version != _pup_version and current_major != deserialized_schema_major:
        error_msg = _schema_version_error_format.format(schema_version, sdk_version)
        raise ValueError(error_msg)

    return schema_version


def get_paginated_results(payload, headers):
    if 'value' not in payload:
        raise WebserviceException('Error, invalid paginated response payload, missing "value":\n'
                                  '{}'.format(payload), logger=module_logger)
    items = payload['value']
    while 'nextLink' in payload:
        next_link = payload['nextLink']

        try:
            resp = ClientBase._execute_func(get_requests_session().get, next_link, headers=headers,
                                            timeout=MMS_SYNC_TIMEOUT_SECONDS)
        except requests.Timeout:
            raise WebserviceException('Error, request to Model Management Service timed out to URL:\n'
                                      '{}'.format(next_link), logger=module_logger)
        if resp.status_code == 200:
            content = resp.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            payload = json.loads(content)
        else:
            raise WebserviceException('Received bad response from Model Management Service while retrieving paginated'
                                      'results:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)
        if 'value' not in payload:
            raise WebserviceException('Error, invalid paginated response payload, missing "value":\n'
                                      '{}'.format(payload), logger=module_logger)
        items += payload['value']

    return items


def _get_mms_url(workspace):
    from azureml._restclient.assets_client import AssetsClient
    assets_client = AssetsClient(workspace.service_context)
    mms_url = assets_client.get_cluster_url()
    uri = '/api/subscriptions/{}/resourceGroups/{}/providers/' \
          'Microsoft.MachineLearningServices/workspaces/{}'.format(workspace.subscription_id,
                                                                   workspace.resource_group,
                                                                   workspace.name)
    return mms_url + uri


def get_docker_client():
    """
    Retrieves the docker client for performing docker operations
    :return:
    :rtype: docker.DockerClient
    :raises: WebserviceException
    """
    try:
        client = docker.from_env(version='auto')
    except docker.errors.DockerException as exc:
        raise WebserviceException('Failed to create Docker client. Is Docker running/installed?\n'
                                  'When you deploy locally, we download a dockerfile\n'
                                  'execute docker build on it, and docker run the built container for you\n'
                                  'Error: {}'.format(exc), logger=module_logger)

    try:
        client.version()
    except Exception as exc:
        raise WebserviceException('Unable to communicate with Docker daemon. Is Docker running/installed?\n'
                                  'When you deploy locally, we download a dockerfile\n'
                                  'execute docker build on it, and docker run the built container for you\n'
                                  '\n\nDocker Client {}'.format(exc), logger=module_logger)

    return client


def login_to_docker_registry(docker_client, username, password, location):
    """
    Logs into a Docker registry.
    :param docker_client: The Docker client.
    :type docker_client: docker.DockerClient
    :param username: Username for the Docker registry.
    :type username: str
    :param password: Password for the Docker registry.
    :type password: str
    :param location: Location of the Docker registry.
    :type location: str
    :raises: WebserviceException
    """
    try:
        print('Logging into Docker registry {}'.format(location))
        docker_client.login(username=username, password=password, registry=location)
    except Exception:
        raise WebserviceException('Unable to login to Docker registry. {}'. format(traceback.format_exc()),
                                  logger=module_logger)


def pull_docker_image(docker_client, image_location, username, password):
    """
    Pulls the docker image from the ACR
    :param docker_client:
    :type docker_client: docker.DockerClient
    :param image_location:
    :type image_location: str
    :param username:
    :type username: str
    :param password:
    :type password: str
    :return:
    :rtype: None
    """
    try:
        print('Pulling image from ACR (this may take a few minutes depending on image size)...\n')
        for outer_line in docker_client.api.pull(image_location, stream=True, auth_config={
            'username': username,
            'password': password
        }):
            sys.stdout.write(outer_line.decode("utf-8"))
    except docker.errors.APIError as e:
        raise WebserviceException('Error: docker image pull has failed:\n{}'.format(e), logger=module_logger)
    except Exception as exc:
        raise WebserviceException('Error with docker pull {}'.format(exc), logger=module_logger)


def build_docker_image(docker_client, dockerfile, tag, custom_context=False, dockerfile_path=None, pull=False):
    """
    Builds a Docker image given a Dockerfile.
    :param docker_client: Docker client instance.
    :type docker_client: docker.DockerClient
    :param dockerfile: Path to Dockerfile or file-like object containing Dockerfile or custom build context.
    :type dockerfile: str or file
    :param custom_context: Whether dockerfile is a tar file object with a custom build context. Defaults to False
    :type custom_context: bool
    :param dockerfile_path: Path of Dockerfile within custom build context.
    :type dockerfile_path: str
    :param pull: Update base images in Dockerfile. Defaults to False
    :type pull: bool
    """
    try:
        print('Building Docker image from Dockerfile...')

        for status in docker_client.api.build(
                path=dockerfile if isinstance(dockerfile, str) else None,
                fileobj=dockerfile if not isinstance(dockerfile, str) else None,
                tag=tag,
                custom_context=custom_context,
                pull=pull,
                dockerfile=dockerfile_path,
                decode=True):
            if 'stream' in status:
                print(status['stream'], end='', flush=True)

            if 'error' in status:
                print(status, flush=True)
                raise WebserviceException('Error: docker image build has failed: {}'.format(status['error']),
                                          logger=module_logger)

        return docker_client.images.get(tag)
    except docker.errors.APIError as e:
        raise WebserviceException('Error: docker image build has failed:\n{}'.format(e), logger=module_logger)
    except Exception as e:
        if isinstance(e, WebserviceException):
            raise

        raise WebserviceException('Error with docker build: {}'.format(e), logger=module_logger)


def create_docker_container(docker_client, image_location, container_name, auto_remove=False, environment=None,
                            labels=None, ports=None, volumes=None):
    """
    Creates (but does not start) a docker container given the image location and container name.
    """
    try:
        labels = labels or {}
        labels['containerName'] = container_name

        return docker_client.containers.create(image_location,
                                               auto_remove=auto_remove,
                                               detach=True,
                                               environment=environment,
                                               labels=labels,
                                               ports=ports,
                                               publish_all_ports=True,
                                               volumes=volumes)
    except docker.errors.APIError as exc:
        raise WebserviceException('Docker container create has failed:\n{}'.format(exc), logger=module_logger)


def create_docker_volume(docker_client, volume_name, labels=None):
    """
    Creates a Docker volume.
    """
    try:
        return docker_client.volumes.create(volume_name, labels=labels)
    except docker.errors.APIError as e:
        raise WebserviceException('Error: Docker volume create has failed: {}'.format(e), logger=module_logger)


def start_docker_container(container):
    """
    Starts an existing Docker container.
    """
    try:
        print("Starting Docker container...")

        container.start()

        print('Docker container running.')
    except docker.errors.APIError as e:
        raise WebserviceException('Docker container start has failed:\n{}'.format(e), logger=module_logger)


def run_docker_container(docker_client, image_location, container_name, **kwargs):
    """
    Creates and starts the docker container given the image location and container name
    :param docker_client:
    :type docker_client: docker.DockerClient
    :param image_location:
    :type image_location: str
    :param container_name:
    :type container_name: str
    :param ports: Mapping of container ports to host ports.
    :type ports: dict
    :return:
    :rtype: docker.Container
    """
    try:
        container = create_docker_container(docker_client, image_location, container_name, **kwargs)
        start_docker_container(container)

        return container
    except docker.errors.APIError as exc:
        raise WebserviceException('Docker container run has failed:\n{}'.format(exc), logger=module_logger)


def write_dir_in_container(container, container_path, local_path):
    """
    Copies a folder to a container's filesystem.
    """
    try:
        archive_bytes = io.BytesIO()

        with tarfile.open(fileobj=archive_bytes, mode='w') as archive_tar:
            archive_tar.add(local_path, arcname=container_path)

        archive_bytes.seek(0)

        container.put_archive('/', archive_bytes)
    except docker.errors.APIError as e:
        raise WebserviceException('Docker file copy has failed:\n{}'.format(e), logger=module_logger)


def write_file_in_container(container, path, data):
    """
    Writes data to a file in a container's filesystem.
    """
    try:
        archive_bytes = io.BytesIO()

        with tarfile.open(fileobj=archive_bytes, mode='w') as archive_tar:
            data_tarinfo = tarfile.TarInfo(name=path)
            data_tarinfo.mtime = time.time()
            data_tarinfo.size = len(data)

            archive_tar.addfile(data_tarinfo, io.BytesIO(data))

        archive_bytes.seek(0)

        container.put_archive('/', archive_bytes)
    except docker.errors.APIError as e:
        raise WebserviceException('Docker file copy has failed:\n{}'.format(e), logger=module_logger)


def get_docker_container(docker_client, container_name, all=None, limit=None):
    """
    Retrieves the container object for a local service.
    """
    try:
        containers = docker_client.containers.list(filters={'label': 'containerName={}'.format(container_name)},
                                                   all=all,
                                                   limit=limit)
    except docker.errors.DockerException as exc:
        raise WebserviceException('Failed to get Docker container:\n{}'.format(exc))

    if len(containers) == 0:
        raise WebserviceException('WebserviceNotFound: No local container with name {}'.format(container_name))

    if len(containers) != 1:
        raise WebserviceException('Error: Multiple containers with container name {}'.format(container_name))

    return containers[0]


def get_docker_containers(docker_client, label_name=None, label_value=None, all=None):
    """
    Retrieves all container objects matching the given label.
    """
    try:
        filters = {}

        if label_name is not None:
            if label_value is not None:
                filters['label'] = '{}={}'.format(label_name, label_value)
            else:
                filters['label'] = label_name

        return docker_client.containers.list(filters=filters, all=all)
    except docker.errors.DockerException as e:
        raise WebserviceException('Failed to get Docker containers:\n{}'.format(e), logger=module_logger)


def get_docker_host_container(docker_client):
    """
    Retrieves the Docker container we're currently running in, if any.
    """
    try:
        # Ask the Linux kernel.
        with open('/proc/self/cgroup') as f:
            cgroup_info = f.read()

        container_id = re.search('/docker/([0-9a-fA-F]+)', cgroup_info).groups()[0]

        return docker_client.containers.get(container_id)
    except docker.errors.APIError as e:
        raise WebserviceException('Failed to get Docker container:\n{}'.format(e), logger=module_logger)
    except:
        pass

    try:
        # HOSTNAME is set to the container short ID, by default.
        return docker_client.containers.get(os.environ['HOSTNAME'])
    except docker.errors.APIError as e:
        raise WebserviceException('Failed to get Docker container:\n{}'.format(e), logger=module_logger)
    except:
        pass

    return None


def get_docker_logs(container, num_lines=5000, raw=False):
    # Skip our pretty-printing heuristics?
    if raw:
        return container.logs(tail=num_lines).decode()

    # Try to understand and format any lines we can recognize.
    pretty_logs = []

    for line in container.logs(tail=num_lines, timestamps=True).decode().splitlines():
        try:
            timestamp, body = line.split(maxsplit=1)
            parsed_body = json.loads(body)

            content = parsed_body['message']
            source = parsed_body['logger']

            stack_trace = parsed_body.get('exc_info', None)

            if source == 'root':
                message = json.loads(content)['message']
                pretty_logs.append('{} {}'.format(timestamp, message))
            elif source == 'logger_stderr' or source == 'logger_stdout':
                # Stdout/stderr are already printed as raw lines
                pass
            else:
                for content_line in content.splitlines():
                    pretty_logs.append('{} {}'.format(timestamp, content_line))

                if stack_trace is not None:
                    for trace_line in stack_trace.splitlines():
                        pretty_logs.append('{} {}'.format(timestamp, trace_line))
        except (KeyError, ValueError):
            # We can't understand this line or it's not JSON, so resort to printing the raw line.
            pretty_logs.append(line)

    return '\n'.join(pretty_logs)


def get_docker_network(docker_client, network_name):
    """
    Gets (or creates) a Docker network by its name.
    """
    try:
        return docker_client.networks.list(network_name)[0]
    except docker.errors.APIError as e:
        raise WebserviceException('Failed to get Docker network {}: {}'.format(network_name, e), logger=module_logger)
    except IndexError:
        pass  # Network doesn't exist

    try:
        return docker_client.networks.create(network_name)
    except docker.errors.APIError as e:
        raise WebserviceException('Failed to create Docker network {}: {}'.format(network_name, e),
                                  logger=module_logger)


def get_docker_port(docker_client, container_name, container):
    """
    Starts the docker container given the image location and container name and returns the docker port
    :param docker_client:
    :type docker_client: docker.DockerClient
    :param container_name:
    :type container_name: str
    :param container:
    :type container: docker.Container
    :return:
    :rtype: str
    """
    container = get_docker_container(docker_client, container_name)

    for key, value in container.attrs['NetworkSettings']['Ports'].items():
        if str(DOCKER_IMAGE_HTTP_PORT) in key and len(value) == 1:
            port = value[0]['HostPort']
            return port

    print('\nContainer Logs:')
    print(get_docker_logs(container))
    cleanup_container(container)
    raise WebserviceException('Error: Container port ({}) is unreachable.'.format(DOCKER_IMAGE_HTTP_PORT),
                              logger=module_logger)


def get_docker_volume(docker_client, volume_name, must_exist=True):
    """
    Gets a Docker volume by name.

    :param docker_client:
    :type docker_client: docker.DockerClient
    :param volume_name:
    :type volume_name: str
    :param must_exist: Raise exception if the volume does not exist.
    :type must_exist: bool
    :return:
    :rtype: docker.Volume
    :raises: WebserviceException
    """
    try:
        return docker_client.volumes.get(volume_name)
    except docker.errors.NotFound:
        if not must_exist:
            return None

        raise WebserviceException('Error: Docker volume {} does not exist.'.format(volume_name), logger=module_logger)
    except Exception as e:
        raise WebserviceException('Error: Failed to get Docker volume {}: {}'.format(volume_name, e),
                                  logger=module_logger)


def connect_docker_network(network, container, aliases=[None]):
    """
    Attaches a Docker container to a Docker network.
    """
    try:
        network.reload()

        # Connecting is slow, so don't redo it if we're already connected.
        if any(c.id == container.id for c in network.containers):
            return

        network.connect(container, aliases=aliases)
    except docker.errors.APIError as e:
        raise WebserviceException('Error: Failed to attach Docker container {} to Docker network {}: {}'
                                  .format(container.short_id, network.name, e), logger=module_logger)


def container_health_check(docker_port, container, health_url=None, cleanup_if_failed=True):
    """
    Sends a post request to check the health of the new container
    :param docker_client:
    :type docker_client: docker.DockerClient
    :param container:
    :type container: docker.Container
    :return:
    :rtype: str
    """
    print("Checking container health...")
    health_url = health_url or 'http://127.0.0.1:{}/'.format(docker_port)

    health_check_iteration = 0
    while health_check_iteration < MAX_HEALTH_CHECK_TRIES:
        try:
            result = ClientBase._execute_func(get_requests_session().get, health_url, verify=False)
        except requests.ConnectionError:
            time.sleep(HEALTH_CHECK_INTERVAL_SECONDS)
            health_check_iteration += 1
            if health_check_iteration >= MAX_HEALTH_CHECK_TRIES and 'http://127.0.0.1' == health_url[:16]:
                print("Container health check failed on localhost. Checking container health using container IP...")
                process = subprocess.Popen(['docker', 'inspect', '--format', "\'{{ .NetworkSettings.IPAddress }}\'",
                                            container.id], stdout=subprocess.PIPE)
                stdout = process.communicate()[0]
                container_ip = stdout.decode().rstrip().replace("'", "")
                if not container_ip:
                    print('\nContainer Logs:')
                    print(get_docker_logs(container))
                    raise WebserviceException('Error: Connection to container has failed. Did your init method fail?',
                                              logger=module_logger)
                health_url = 'http://{}:5001/'.format(container_ip)
                health_check_iteration = 0
            continue
        except requests.Timeout:
            time.sleep(HEALTH_CHECK_INTERVAL_SECONDS)
            health_check_iteration += 1
            continue

        if result.status_code == 200:
            return health_url
        elif result.status_code == 502:
            time.sleep(HEALTH_CHECK_INTERVAL_SECONDS)
            health_check_iteration += 1
            continue
        else:
            if 'http://127.0.0.1' == health_url[:16]:
                print("Container health check failed on localhost. Checking container health using container IP...")
                process = subprocess.Popen(['docker', 'inspect', '--format', "\'{{ .NetworkSettings.IPAddress }}\'",
                                            container.id], stdout=subprocess.PIPE)
                stdout = process.communicate()[0]
                container_ip = stdout.decode().rstrip().replace("'", "")
                if not container_ip:
                    print('\nContainer Logs:')
                    print(get_docker_logs(container))
                    raise WebserviceException('Error: Connection to container has failed. Did your init method fail?',
                                              logger=module_logger)
                health_url = 'http://{}:5001/'.format(container_ip)
                health_check_iteration = 0
                continue
            else:
                print('\nContainer Logs:')
                print(get_docker_logs(container))
                if cleanup_if_failed:
                    cleanup_container(container)
                raise WebserviceException('Error: Connection to container has failed. Did your init method fail?',
                                          logger=module_logger)
    if health_check_iteration >= MAX_HEALTH_CHECK_TRIES:
        print('\nContainer Logs:')
        print(get_docker_logs(container))
        if cleanup_if_failed:
            cleanup_container(container)
        raise WebserviceException('Error: Connection to container has failed. Did your init method fail?',
                                  logger=module_logger)


def container_scoring_call(docker_port, input_data, container, health_url, cleanup_on_failure=True):
    """
    Sends a scoring call to the given container with the given input data
    :param docker_client:
    :type docker_client: docker.DockerClient
    :param input_data:
    :type input_data: str
    :param container:
    :type container: docker.Container
    :return:
    :rtype: str
    """
    print("Making a scoring call...")
    scoring_url = health_url + WEBSERVICE_SCORE_PATH
    headers = {'Content-Type': 'application/json'}
    try:
        result = ClientBase._execute_func(get_requests_session().post, scoring_url, headers=headers, data=input_data,
                                          verify=False)
    except requests.exceptions.HTTPError:
        print('\nContainer Logs:')
        print(get_docker_logs(container))

        if cleanup_on_failure:
            cleanup_container(container)

        raise WebserviceException('Error: Connection with container for scoring has failed.', logger=module_logger)

    if result.status_code == 200:
        result_object = result.json()
        print('Scoring result:')
        print(result_object)
        return result_object
    else:
        content = result.content.decode('utf-8')
        if content == "ehostunreach":
            print('\nContainer Logs:')
            print(get_docker_logs(container))

            if cleanup_on_failure:
                cleanup_container(container)

            raise WebserviceException('Error: Scoring was unsuccessful. Unable to reach the requested host.',
                                      logger=module_logger)

        print("Scoring response content:\n", content)

        if cleanup_on_failure:
            cleanup_container(container)

        raise WebserviceException('Error: Scoring was unsuccessful.', logger=module_logger)


def cleanup_container(container):
    """
    Tries to kill and remove the container
    :param container:
    :type container: docker.Container
    :return:
    :rtype: None
    """
    try:
        container.kill()
    except Exception as exc:
        print('Container (name:{}, id:{}) cannot be killed.'.format(container.name, container.id))
    try:
        container.remove()
        print('Container has been successfully cleaned up.')
    except Exception as exc:
        print('Container (name:{}, id:{}) cannot be removed.'.format(container.name, container.id))


def cleanup_docker_image(docker_client, image_id):
    """
    Deletes a local Docker image.

    :param docker_client:
    :type docker_client: docker.DockerClient
    :param image_id: Docker image ID.
    :type image_id: str
    :return:
    :rtype: None
    """
    try:
        docker_client.images.remove(image_id)
        print('Image {} successfully removed.'.format(image_id))
    except Exception as e:
        print('Image {} cannot be removed: {}'.format(image_id, str(e)))


def validate_path_exists_or_throw(member, name):
    if not os.path.exists(member):
        raise WebserviceException("{0} {1} doesn't exist".format(name, member), logger=module_logger)


def joinPath(source_directory, path):
    if path and source_directory:
        return os.path.join(source_directory, path).replace(os.sep, '/')
    else:
        return path


def validate_entry_script_name(name):
    """

    :param name:
    :type name: str
    :raises: WebserviceException
    """
    if not name.isidentifier() or iskeyword(name):
        raise WebserviceException('Error, invalid name "{}" for provided entry script. The script must be importable '
                                  'as a valid python module, and must adhere to standard module naming. This means it '
                                  'must be a valid python identifier and not a part of the set of python standard '
                                  'keywords.'.format(name), logger=module_logger)


def check_duplicate_properties(current_properties, new_properties):
    """

    :param current_properties:
    :type current_properties: dict[str, str]
    :param new_properties:
    :type new_properties: dict[str, str]
    :raises: WebserviceException
    """
    if new_properties:
        duplicate_properties = []
        for key in new_properties:
            if key in current_properties:
                duplicate_properties.append(key)
        if duplicate_properties:
            raise WebserviceException('Error, properties are immutable, the following keys cannot be added/modified: '
                                      '{}'.format(','.join(duplicate_properties)), logger=module_logger)


def get_requests_session():
    """

    :return: A requests.Session object
    :rtype: requests.Session
    """
    global _session
    if not _session:
        _session = requests.Session()

    return _session


def webservice_name_validation(name):
    """

    :param name:
    :type name: str
    :return:
    :rtype: bool
    :raises: WebserviceException
    """
    if not re.fullmatch(r'^[a-z]([-a-z0-9]*[a-z0-9])?$', name) or len(name) < 3 or len(name) > 32:
        raise WebserviceException('Error, provided name is invalid. It must only consist of lowercase letters, '
                                  'numbers, or dashes, start with a letter, end with a letter or number, and be '
                                  'between 3 and 32 characters long.')
