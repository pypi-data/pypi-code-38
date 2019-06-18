# coding: utf-8

from os import path
from six import string_types
import six


def generate_hostname(config):
    """ Helper method that generates the hostname according to Vauxoo standard:

        container_name.domain_serving.the.instance.com

    :param config: Configuration Object

    :return: String formated as "{{prefix}}.{{domain}}"
    """
    res = "{}.{}".format(
        generate_prefix(config),
        config.container_config.get('domain'))
    return res.replace('_', '')


def generate_binds(volumes, working_folder):
    """ Helper method to generate volume binds as required by docker-py

        http://docker-py.readthedocs.org/en/latest/volumes/

        In case the working folder is prefixed with ~ it'll be expanded to the user's
        home directory

    :param volumes: dict with volumes in the following format:

        .. code-block:: python

            {
                "host_folder_name": "volume_inside_docker",
                "host_folder_name_2": "volume_inside_docker_2",
            }

    :param working_folder: base folder in the host where the volumes mounted inside the container
        will be created

    :returns: Dict with the following format:

        .. code-block:: python

            {
                "{{ working_folder }}/host_folder_name": {
                    "bind": "/volume_inside_docker",
                    "ro": False
                    },
                "{{ working_folder }}/host_folder_name_2": {
                    "bind": "/volume_inside_docker_2",
                    "ro": False
                    }
            }

    """
    volume_binds = {}
    for key, value in six.iteritems(volumes):
        volume = path.join(path.expanduser(working_folder), key)
        volume_binds.update({
            volume: {
                "bind": value,
                "ro": False,
            }
        })
    return volume_binds


def generate_volumes(volumes):
    """ Helper method to generate list of volumes used to deploy docker
    http://docker-py.readthedocs.org/en/latest/volumes/

    :param volumes: dict with volumes in the following format

        .. code-block:: python

            {
                "host_folder_name": "volume_inside_docker",
                "host_folder_name_2": "volume_inside_docker_2",
            }

    :return: List of volumes inside docker ["volume_inside_docker", "volume_inside_docker_2"]
    """
    res = [item for item in six.itervalues(volumes)]
    return res


def generate_prefix(config):
    """ Helper method that generates the prefix for containers name, folders and databases
        to be created.

    :param config: Object with the deployment configuration

    :return: String formatted as "{{task_id}}_{{customer_id}}"
    """
    if config.prefix:
        return config.prefix
    task = config.instance_config.get('task_id')
    customer = config.instance_config.get('customer_id')
    return "{}_{}".format(task, customer) if task and customer else False


def generate_env_vars(config):
    """ Helper method to generate list of env vars in the format required by docker-py
        http://docker-py.readthedocs.org/en/latest/api/#create_container

    :param config: dict with env vars and values as follows:

        .. code-block:: python

            {
                "var1": "value1",
                "var2": 234,
            }

    :return: List of env vars, vars names are uppercased as most of unixlike OS ["VAR1=value1",
        "VAR2=234"]
    """
    return ["{}={}".format(key.upper(), value) for key, value in six.iteritems(config)]


def generate_port_lists(config):
    """ Helper method to generate list of exposed ports inside container
        http://docker-py.readthedocs.org/en/latest/api/#create_container

    :param config: keys are the ports inside docker and values the ports in the host:

        .. code-block:: python

            {
                "8069": 2213,
                "8072": 2214,
            }

    :return: List of integers that represents the ports to be exposed:
            [8069, 8072]
    """
    return [int(value) for value in config.keys()]


def generate_port_bindings(config):
    """Helper method that generates the dictionary of the host ports that will be
    bound to the container's exposed ports.

    :param config: Dictionary where the keys are the ports inside docker and the values
        are the ports in the host
    :return: Parsed dictionary with the correct format of the ports
    """
    res = config.copy()
    for container_port, host_port in config.items():
        if isinstance(host_port, string_types):
            parts = host_port.split(':')
            res.update({container_port: [(parts[0], int(parts[1]))]})
        elif isinstance(host_port, list):
            res.update({container_port: list()})
            for port in host_port:
                parts = port.split(':')
                res.get(container_port).append((parts[0], int(parts[1])))
    return res


def get_ports_dict(networking):
    """ Parse the networking dict gotten from docker inspect and returns a dict with the private
        ports as keys and exposed ports as values

    :param networking: Networking configuration gotten from
        :meth:`~deployv.base.dockerv.DockerV.inspect`

    :return: Mapping ports dict:

        .. code-block:: python

            {
                '8072': 32768,
                '8069': 8069
            }

    .. todo:: Fix the reference deployv.base.dockerv.DockerV.inspect

    """
    ports = networking.get('NetworkSettings').get('Ports')
    res = dict()
    if not ports:
        return res
    for private, public in ports.items():
        private_port = private.split('/')[0]
        if not public:
            continue
        res.update({private_port: []})
        for port in public:
            ip = port.get('HostIp')
            port = int(port.get('HostPort'))
            if ip == '0.0.0.0':
                res.update({private_port: port})
                break
            res.get(private_port).append('{ip}:{port}'.format(ip=ip, port=port))
    return res


def parse_env_vars(env_vars):
    """ Parses the env var list gotten from docker inspect and returns a dict with the env vars
        in lowercase as keys

    :param env_vars: list of env vars as returned by docker inspect

    :return: Dict with the lowercase env vars

    """
    res = {}
    for var in env_vars:
        name, value = var.split('=')
        res.update({name.lower(): value})
    return res
