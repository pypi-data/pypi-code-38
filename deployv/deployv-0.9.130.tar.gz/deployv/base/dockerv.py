# coding: utf-8

"""DockerV - Docker helper class by Vauxoo
==========================================

This module provides a helper class to deal with docker containers in an OO way, basically wraps
`docker-py <https://github.com/docker/docker-py>`_ to deal with a json formatted configuration.

Most of the parameters can be checked in the docker official `documentation
<https://docs.docker.com/reference/run/>`_ or in the `docker-py api documentation
<http://docker-py.readthedocs.org/en/latest/api/>`_.

Still not all functionalities are implemented, but the minimal to start a docker container with
basic configuration::

    {
        "apt_install": {},
        "pip_install": {},
        "domain": "localhost",
        "command": "sleep 20",
        "env_vars": {
            "odoo_config_file": "/home/odoo/.openerp_serverrc",
            "odoo_home": "/home/odoo",
            "odoo_user": "odoo"
        },
        "image_name": "busybox",
        "mem_limit": "768m",
        "ports": {
            "8069": 8069,
            "8072": None
        },
        "remove_previous": True,
        "working_folder": "/path/to/docker_volumes",
        "volumes":{
            "filestore": "/home/odoo/.local/share/Odoo",
            "logs": "/var/log/supervisor",
            "ssh": "/home/odoo/.ssh",
            "tmp": "/tmp"
        }
    }

Where:

* *apt_install* (not implemented yet): Install additional packages using apt-get install.
    (This will be changed to use a generic way of installing packages in other distros)
* *pip_install* (not implemented yet): Install additional dependencies using pip.
* *domain*: Domain where the container will be executing.
* *image_name*: Docker image name that will be used to create the container.
    (See `official documentation <https://docs.docker.com/userguide/dockerimages/>`_)
* *mem_limit*: Max amount of ram allowed for the container.
* *ports*: A dict with ports mapping, key is the port number inside the container, value the host
    port.  If None is provided as value the port number will be assigned randomly by docker
    service.
* *remove_previous*: If there is a container with the same name or id it will be removed before
    launching the new one.
* *working_folder*: Folder in the host where the shared volumes (if any) will be created.
* *volumes*: A dict with the volume mapping, keys are the folder names inside working_folder and
    values are the actual path inside the container.
"""

import logging
from os import path
from docker import DockerClient
from docker import APIClient as Client
import docker.errors
import simplejson as json
from deployv.helpers import container
from deployv.helpers.utils import get_error_message, decode
from deployv.base import errors
from retry_decorator import retry


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class DockerV(object):
    """Helper class to make docker container deployments easier by code.

    If your docker service is not using the default socket you can change it by passing
    docker_url::

        config = {
            'image_name': 'busybox',
            'command': 'sleep 3',
            'mem_limit': '16m',
            'container_name': 'test_deployv',
            'ports' : {
                '8069': 8069,
                '8072': None
            },
            'env_vars': {
                'var1':'value1',
                'var2': 1234,
            }
        }
        container_object = DockerV(config)
        container_id = container_object.deploy_container()

    ``image_name`` and ``command`` are the only required parameters, others parameters are
    optional. If a port is empty, it will be autoasigned by docker.

    If the container already exists the config dict would be something like::

        config = {
            'container_name': 'test_deployv',
            'id': 'container_id'
        }

    Only one of them is needed. You can specify both, but id will be checked first then the
    container_name.
    """

    __config = {}
    __docker_id = None
    __url = None

    def __init__(self, config, timeout=300, docker_url="unix://var/run/docker.sock"):
        self.__cli = Client(base_url=docker_url, timeout=timeout)
        self.__cli2 = DockerClient(base_url=docker_url, timeout=timeout)
        self.__config = config
        self.__url = docker_url
        if self.__config.get('id', False):
            inspected = self.inspect(self.__config.get('id'))
            self.__docker_id = inspected.get('Id')
        elif self.__config.get('container_name', False):
            try:
                inspected = self.inspect(self.__config.get('container_name'))
            except errors.NoSuchContainer as error:
                error_message = get_error_message(error)
                logger.debug('%s', error_message)
            else:
                self.__docker_id = inspected.get('Id')
                logger.debug('Container inspected %s',
                             json.dumps(inspected, sort_keys=True, indent=2))
                self.__config.update({'id': inspected.get('Id')})
                if not self.__config.get('image_name'):
                    self.__config.update({
                        'image_name': inspected.get('Config').get('Image')})
                if not self.__config.get('env_vars'):
                    env_vars = container.parse_env_vars(inspected.get('Config').get('Env'))
                    self.__config.update({'env_vars': env_vars})

    @property
    def url(self):
        return self.__url

    @property
    def cli(self):
        """This is the low-level API (backwards compatible with docker 1.X).

        Read the docs in: https://docker-py.readthedocs.io/en/stable/api.html
        """
        return self.__cli

    @property
    def cli2(self):
        """This is the high-level API (introduced in docker 2.0).

        Read the docs in: https://docker-py.readthedocs.io/en/stable/client.html
        """
        return self.__cli2

    @property
    def config(self):
        return self.__config

    @config.setter
    def config(self, value):
        keys = [u'image_name', u'command', ]
        if not all([key in value for key in keys]):
            raise KeyError('Mandatory keys: {}'.format(', '.join(keys)))
        self.__config = value

    @property
    def docker_id(self):
        """Returns container id, the same you see when executing 'docker ps' in the first column.

        :returns: Container Id.
        :rtype: str
        """
        return self.__docker_id.lower() if self.__docker_id else None

    @property
    def docker_env(self):
        """Gets env vars from a docker container.

        :returns: dict with var name as key and value.
        :rtype: dict
        """
        try:
            inspected = self.inspect()
        except errors.NoSuchContainer as error:
            logger.error("No such container: %s", self.docker_id)
            logger.exception(get_error_message(error))
            return None

        env_vars = inspected.get('Config').get('Env')
        res = container.parse_env_vars(env_vars)
        return res

    def deploy_container(self):
        """Deploys a container with the given config and returns some basic information about the
        container. See :func:`~deployv.base.dockerv.DockerV.basic_info` for more information about
        the format and content.

        :returns: Some basic information about the container.
        :rtype: dict
        """
        env_vars = container.generate_env_vars(self.config.get("env_vars"))
        container_name = self.config.get("container_name").lower()
        logger.debug('Deploying container %s', container_name)
        working_folder = path.join(
            self.__config.get("working_folder"),
            container_name)
        volume_binds = container.generate_binds(
            self.__config.get("volumes"), working_folder)
        volumes = container.generate_volumes(self.__config.get("volumes"))
        self.set_default_ports()
        ports = container.generate_port_lists(self.__config.get("ports"))
        port_bindings = container.generate_port_bindings(self.config.get('ports'))
        container_config = {
            "image": self.config.get("image_name"),
            "command": self.config.get("command"),
            "hostname": self.config.get("container_hostname"),
            "ports": ports,
            "environment": env_vars,
            "volumes": volumes
        }
        if self.config.get("container_name", False):
            container_config.update(
                {'name': self.config.get("container_name").lower()})
        host_config = {
            "binds": volume_binds,
            "port_bindings": port_bindings,
            "mem_limit": self.config.get("mem_limit", 0),
            "memswap_limit": self.config.get("mem_limit", 0),
            "restart_policy": {
                "MaximumRetryCount": 0,
                "Name": "unless-stopped"
            }
        }
        if self.__config.get("remove_previous", False):
            self.__docker_id = self.config.get("container_name").lower()
            self.remove_container()
        hconfig = self.__cli.create_host_config(**host_config)
        hconfig.get('PortBindings').get("5432/tcp", [{}])[0].\
            update({'HostIp': '127.0.0.1'})
        logger.debug('Container config %s', container_config)
        try:
            container_obj = self.__cli.create_container(
                host_config=hconfig, **container_config)
            self.__docker_id = container_obj.get("Id")
            logger.debug('Created container %s', self.__docker_id)
        except docker.errors.NotFound:
            logger.exception('Image not found')
            raise errors.NoSuchImage(self.config.get("image_name"))
        except docker.errors.APIError as error:
            logger.exception('Error creating the container')
            if 'You have to remove (or rename) that container' in error.explanation:
                logger.warning('The container %s already exists, skipping create step',
                               container_config.get('name'))

        try:
            self.__cli.start(container=self.__docker_id)
        except docker.errors.APIError as error:
            if 'port is already allocated' in get_error_message(error) \
                    or 'address already in use' in get_error_message(error):
                logger.warning('Port already allocated')
                raise errors.ErrorPort(
                    'At least one of the ports used by this container are being used by another'
                    ' process, manual intervention is required. Error message:\n{msg}'
                    .format(msg=error.explanation))
        return self.basic_info

    def remove_container(self, container_name=False):
        """Stops and removes the specified container. Docker id or name must be in lowercase, if
        not, it will be converted to lowercase.
        """
        if not container_name:
            container_name = self.docker_id
        try:
            self.__cli.stop(container_name)
            self.__cli.remove_container(container_name, force=True)
        except docker.errors.NotFound as error:
            logger.debug(get_error_message(error))
        else:
            self.__docker_id = None

    def remove_image(self, image_name=False):
        """Try remove the specified image.
        returns a list with message if it succeeded in removing the image,
        else return a list empty

        :param image_name: image name to remove
        :return: list
        """
        res = []
        image_id = self.__cli.images(name=image_name, quiet=True)
        image_id = image_id and image_id[0]
        if not image_id:
            return res
        try:
            self.__cli.remove_image(image_name)
            res.append("Removed image {}".format(image_name))
        except docker.errors.APIError:
            pass
        return res

    @property
    def basic_info(self):
        """Gets some basic information form the container::

            {
                'Id': 'container id',
                'name': 'container name',
                'image_name': 'image used to build the container',
                'status': 'container status (same shown when "docker ps" is executed)',
                'ports': 'dict with port assignments {local (inside docker) : public}'
            }

        :returns: Container information.
        :rtype: dict
        """
        res = {}
        try:
            inspected = self.inspect()
        except errors.NoSuchContainer:
            return res
        if inspected.get('Id') == self.docker_id:
            res.update(
                {
                    'Id': inspected.get('Id'),
                    'name': inspected.get('Name')[1:],
                    'image_name': inspected.get('Config').get('Image'),
                    'status': 'running' if inspected.get('State') else 'exited',
                    'ports': container.get_ports_dict(inspected)
                })
        return res

    def get_container_packages(self):
        """Returns the installed packages inside the container (for pip and apt).

        The packages are returned in a dict with the package manager and the installed packages
        with their versions inside::

            {
                'pip': {
                    'package': 'version',
                    ...
                },
                'apt': {
                    'package': 'version',
                    ...
                },
            }

        :returns: Installed packages
        :rtype: dict
        """
        pip_res = self.exec_cmd(['pip', 'freeze'])
        pip = dict([line.split('==') for line in pip_res.split('\n') if '==' in line])
        apt_res = self.exec_cmd(['apt', 'list', '--installed'])
        apt = dict([(pck.split('/')[0] for pck in line.split(' ')[:2])
                    for line in apt_res.split('\n') if 'installed' in line])
        return {
            'pip': pip,
            'apt': apt,
        }

    @retry(errors.ClientAPIError, tries=3, timeout_secs=0.5, logger=logger)
    def exec_cmd(self, cmd, user=None):
        """Wraps and logs the `exec_create
        <https://docker-py.readthedocs.org/en/latest/api/#exec_create>`_ and `exec_start
        <https://docker-py.readthedocs.org/en/latest/api/#exec_start>`_ methods.
        :param cmd: Command line to be executed inside the Docker container.
        :type cmd: str
        :returns: The command output.
        """
        logger.debug('exec_cmd: %s', cmd)
        try:
            exec_id = self.__cli.exec_create(self.docker_id, cmd, user=user)
        except (docker.errors.APIError, docker.errors.NullResource) as error:
            error_msg = get_error_message(error)
            if 'is not running' in error_msg:
                raise errors.NotRunning(self.docker_id)
            if 'Resource ID was not provided' in error_msg:
                raise errors.CommandError(cmd, "Container does not exist")
            if hasattr(error, 'is_client_error') and error.is_client_error():
                raise errors.ClientAPIError(
                    "Container {0} is in conflict or stopped unexpectedly".format(self.docker_id))
            raise
        res = decode(self.__cli.exec_start(exec_id.get('Id')))
        return res

    def inspect(self, container_id=False):
        """Wrapper for docker-py.inspect _container.

        :param container_id: Optional parameter with the container name or id.
        :type container_id: str
        :returns: Information about the container.  See `inspect_container in the official docs
            <https://docker-py.readthedocs.org/en/latest/api/#inspect_container>`_.
        """
        try:
            res = self.cli.inspect_container(container_id if container_id else self.docker_id)
        except docker.errors.NotFound:
            raise errors.NoSuchContainer(container_id if container_id else self.docker_id)
        except docker.errors.NullResource:
            raise errors.NoSuchContainer(container_id if container_id else self.docker_id)
        return res

    def install_packages(self, apt_packages=None, pip_packages=None):
        """Installs apt and/or pip packages inside the container and returns the full operation
        log. Runs quietly, so the log is cleaner.

        The result has the following format (if no errors were found)::

            {
                'apt_install': [
                    {
                        'package_name': {
                            'installed': True
                        }
                    }
                ]
                'pip_install': [
                    {
                        'package_name': {
                            'installed': True
                        }
                    }
                ]
            }

        In case of error::

            {
                'apt_install': [
                    {
                        'package_name': {
                            'installed': False,
                            'message': 'Error msg generated by the installer'
                        }
                    }
                ]
                'pip_install': [
                    {
                        'package_name': {
                            'installed': False,
                            'message': 'Error msg generated by the installer'
                        }
                    }
                ]
            }

        The results can be mixed if some packages fail and some don't during the installation
        process.

        :param apt_packages: Packages to be installed via apt.
        :type apt_packages: list
        :param pip_packages: Packages to be installed via pip.
        :type pip_packages: list
        :returns: Full log operations.
        :rtype: dict
        """
        res = {}
        if isinstance(apt_packages, list) and apt_packages:
            self.exec_cmd('apt-get update -q')
            res.update({'apt_install': []})
            for apt_package in apt_packages:
                cmd_res = self.exec_cmd('apt-get install {name} -yq'.format(name=apt_package))
                logger.debug('apt_install %s', cmd_res)
                composed = self._compose_message('apt_install', apt_package, cmd_res)
                res.get('apt_install').append(composed)

        if isinstance(pip_packages, list) and pip_packages:
            res.update({'pip_install': []})
            for pip_package in pip_packages:
                cmd_res = self.exec_cmd('pip install {name}'.format(name=pip_package))
                logger.debug('pip_install %s', cmd_res)
                composed = self._compose_message('pip_install', pip_package, cmd_res)
                res.get('pip_install').append(composed)
        return res

    def _compose_message(self, package_installer, package, result):
        """Composes the response.

        The response has the following format::

            {
                'package_name': {
                    'installed': Boolean,
                    'message': 'if any error, this will have the error msg.'
                               'if no error, this won't be present.'
                }
            }

        :param package_installer: Package installer name (so far pip or apt).
        :type package_installer: str
        :param package: Package/dependency installed.
        :type package: string.
        :param result: The result from :meth:`~deployv.base.dockerv.DockerV.exec_cmd`.
        :returns: Formatted output in a json format.
        :rtype: dict
        """
        res = {package: {}}
        errors_txt = ['Unable to locate package', 'No matching distribution found']
        if any([error_txt in result for error_txt in errors_txt]):
            res.get(package).update(
                {
                    'installed': False,
                    'message': result
                })
        else:
            res.get(package).update({'installed': True})
        return res

    @retry(docker.errors.APIError, tries=3, timeout_secs=0.5, logger=logger)
    def pull(self, image_name):
        """This is a simple wrapper for docker pull to use the deployv exceptions instead of the
        docker ones.

        :param image_name: The image name to pull.
        :type image_name: str
        """
        try:
            self.cli.pull(image_name)
        except docker.errors.NotFound:
            raise errors.NoSuchImage(image_name)

    @retry(docker.errors.APIError, tries=3, timeout_secs=0.5, logger=logger)
    def push(self, image_name):
        """Pushes an image and logs (in DEBUG level) the process.

        :param image_name: The image that will be pushed.
        :type image_name: str
        """
        logger.info('Pushing image "%s"', image_name)
        res = {'result': {'log': []}}
        for line in self.cli.push(image_name, stream=True):
            obj = json.loads(decode(line))
            res['result']['log'].append(obj)
            logger.debug(obj)
            if obj.get('error'):
                return {
                    'error': obj.get('error').strip(),
                }
            if obj.get('aux'):
                res['result'].update({'details': obj.get('aux')})
        return res

    def commit(self, repository, tag):
        """Commits the container with the given repository and tag.

        :param repository: The repository for the image.
        :type repository: str
        :param tag: The tag for the image.
        :type tag: str
        """
        res = {'result': {}}
        try:
            container_info = self.basic_info
        except errors.NoSuchContainer:
            res.update({'error': 'Specified container doesn\'t exist'})
            return res
        logger.info('Committing container "%s" as "%s:%s"',
                    container_info.get('name'), repository, tag)
        container_id = container_info.get('Id')
        try:
            commit = self.cli.commit(container_id, repository=repository, tag=tag)
        except docker.errors.APIError as error:
            res.update({'error': str(error)})
            return res
        image = self.cli.inspect_image(commit.get('Id'))
        image_tagged = image.get('RepoTags')[0]
        res['result'].update({
            'container_info': container_info,
            'tagged_image': image_tagged,
        })
        return res

    def commit_and_push(self, repository, tag):
        """Commits an image with the given repository and tag, and pushes it.

        :param repository: The repository for the image.
        :type repository: str
        :param tag: The tag for the image.
        :type tag: str
        """
        res = {'result': {}}
        commit = self.commit(repository, tag)
        res['result'].update(commit.get('result'))
        if commit.get('error'):
            res.update({'error': commit.get('error')})
            return res
        push = self.push(commit.get('result').get('tagged_image'))
        res['result'].update({'push_result': push.get('result')})
        if push.get('error'):
            res.update({'error': push.get('error')})
            return res
        return res

    def tag(self, image, repository, tag):
        """Tags an already created image with a new repository and tag.

        :param image: The image that will be tagged.
        :type image: str
        :param repository: The new repository for the image.
        :type repository: str
        :param tag: The new tag for the image.
        :type tag: str
        """
        res = {'result': {}}
        tagged_image = '{repo}:{tag}'.format(repo=repository, tag=tag)
        logger.info('Tagging image "%s" as "%s"', image, tagged_image)
        try:
            tag = self.cli.tag(image, repository, tag=tag)
        except docker.errors.APIError as error:
            res.update({'error': str(error)})
            return res
        res['result'].update({
            'tagged_image': tagged_image
        })
        return res

    def tag_and_push(self, image, repository, tag):
        """Tags an already created image with a new repository and tag, and pushes the new image.

        :param image: The image that will be tagged.
        :type image: str
        :param repository: The new repository for the image.
        :type repository: str
        :param tag: The new tag for the image.
        :type tag: str
        """
        res = {'result': {}}
        tag_result = self.tag(image, repository, tag=tag)
        res['result'].update(tag_result.get('result'))
        if tag_result.get('error'):
            res.update({'error': tag_result.get('error')})
            return res
        push = self.push(tag_result.get('result').get('tagged_image'))
        res['result'].update({'push_result': push.get('result')})
        if push.get('error'):
            res.update({'error': push.get('error')})
            return res
        return res

    def inspect_image(self, image_name):
        """Wrapper for the inspect image, basically does the same but raises a deployv exception
        instead of the docker-py one.

        :param image_name: The image name that will be inspected.
        :type image_name: str
        :returns: The result of docker inspect_image.
        :raises: :class:`~deployv.base.errors.NoSuchImage` if the image doesn't exist.
        """
        try:
            res = self.cli.inspect_image(image_name)
        except docker.errors.NotFound:
            raise errors.NoSuchImage(image_name)
        return res

    def set_default_ports(self):
        """Sets default port mappings if the ones specified in the json
        contain falsy values so we can have control over the ports assigned
        to the instances. It also checks if the ports specified for a
        develop instance are free, it sets new ports if they are not.
        """
        deploy_cfg = self._InstanceV__full_config.deployer
        instance_ports = self.config.get('ports')
        specified_ports = set(self._parse_ports(instance_ports))
        used_ports = set(self._get_used_ports())
        port_start = int(deploy_cfg.get('docker_start_port', 30000))
        port_end = int(deploy_cfg.get('docker_end_port', 40000))
        available_specified_ports = list(specified_ports - used_ports)
        available_default_ports = [
            p for p in range(port_start, port_end) if
            p not in used_ports
        ]
        available_ports = available_default_ports + available_specified_ports
        if not available_ports:
            raise errors.ErrorPort('There are no available ports in the range'
                                   ' {start} - {end} to deploy this instance'
                                   .format(start=port_start, end=port_end))
        instance_type = self._InstanceV__full_config.instance_config.get(
            'instance_type')
        ports_to_map = [
            port for port, mapping in instance_ports.items() if not mapping
        ]
        if instance_type == 'develop':
            ports_to_map += [
                port for port, mapping in
                instance_ports.items() if mapping not in available_ports
            ]
        if not ports_to_map:
            # There are no ports to map, try to use the ones specified
            return
        instance_ports.update(dict(zip(ports_to_map, available_ports)))
        return

    def _get_used_ports(self):
        """Method that checks the ports of all the containers in the server
        in order to list all the ports used by instances in order to decide
        if the current container's ports should be reassigned. This only checks
        for the ports used by containers because the container's ports are
        reassgined only if the ports are used by another container, if they are
        used by another process (or zombie process), an error will be raised to
        alert the users.
        """
        containers = self.cli2.containers.list()
        used_ports = set()
        for container_obj in containers:
            container_info = self.inspect(container_obj.id)
            ports = self._parse_ports(container.get_ports_dict(container_info))
            used_ports.update(ports)
        return list(used_ports)

    def _parse_ports(self, ports):
        """ Receives a dictionary with the port mappings between the container
        and the host and parses them to return a list of the host ports used by
        the containers.

        :param ports: dictionary of port bindings
        :return: List of integers representing the host ports used by the host
        """
        parse_ports = {
            int: lambda x: x,
            str: lambda x: int(x.split(':')[-1]),
        }
        parse_ports[list] = lambda x: [
            parse_ports[type(port)](port) for port in x if
            port and isinstance(port, (int, str))
        ]
        res = set()
        for port in ports.values():
            parse_func = parse_ports.get(type(port))
            if not parse_func:
                continue
            parsed_ports = parse_func(port)
            if not parsed_ports:
                continue
            res.update(parsed_ports if
                       isinstance(parsed_ports, list) else [parsed_ports])
        return list(res)
