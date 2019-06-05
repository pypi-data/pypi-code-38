import logging
import os
import socket
import uuid

import docker
import yaml

from missinglink.resource_manager.docker.utils import is_windows_containers

WS_SERVER = os.environ.get('WS_SERVER') or 'localhost:8765'
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    pass


class ConfigFile(object):
    @classmethod
    def load_yaml_file(cls, path):
        if os.path.isfile(path):
            with open(path) as f:
                return yaml.load(f) or {}
        return {}

    @classmethod
    def save_yaml_file(cls, path, data):
        with open(path, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False)

    def __init__(self, path, default_config=None):
        super(ConfigFile, self).__setattr__('path', path)
        super(ConfigFile, self).__setattr__('default_config', default_config or {})
        super(ConfigFile, self).__setattr__('data', self.load_yaml_file(path))

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]

        return self.default_config[item]

    def __setattr__(self, key, value):
        self.data[key] = value

    def get(self, item, default=None):
        return self.data.get(item, self.default_config.get(item, default))

    def save(self):
        self.save_yaml_file(self.path, self.data)


class ConfigurationInstance(object):

    SHELL_IMAGE = 'library/bash:latest'
    GIT_IMAGE = 'missinglinkai/git-lfs:latest'
    ML_IMAGE = 'missinglinkai/missinglink:latest'

    @classmethod
    def get_default_configuration(cls):
        return {
            'general': {
                'backend_base_url': 'https://missinglink-staging.appspot.com',
                'env': {},
                'hostname': socket.gethostname(),
                'mount': {},
                'ws_server': 'ws://rm-ws-prod.missinglink.ai',
                'pull_job': None,
                'git_image': cls.GIT_IMAGE,
                'shell_image': cls.SHELL_IMAGE,
                'missinglink_image': cls.ML_IMAGE,
                'config_volume': os.environ.get('ML_CONFIG_VOLUME', 'ml_config_volume')
            }
        }

    def __init__(self, config_path=None):
        config_path = config_path or './config'
        logger.info('Configuration path is %s', config_path)
        os.makedirs(config_path, exist_ok=True)
        self.config_path = config_path
        self.general = ConfigFile(os.path.join(config_path, 'index.yaml'), self.get_default_configuration()['general'])

    loaded_config = None

    @classmethod
    def load_config(cls, config_path):
        cls.loaded_config = cls(config_path)

    @classmethod
    def get_config(cls):
        if cls.loaded_config is None:
            load_config()

        return cls.loaded_config


class WindowsConfigurationInstance(ConfigurationInstance):

    SHELL_IMAGE = 'mcr.microsoft.com/windows/servercore:ltsc2016'
    GIT_IMAGE = 'missinglinkai/git-lfs:windows-server-0.1'
    ML_IMAGE = 'missinglinkai/missinglink:windows-server-0.1'


def load_config():
    conf_path = os.environ.get('MLADMIN_CONF_DIR', os.path.expanduser('~/.config'))
    init_cluster(config_folder=conf_path)
    return conf_path


def get_active_config():
    configuration_instance_class = _get_configuration_instance_class()
    return configuration_instance_class.get_config()


def _get_configuration_instance_class():
    return WindowsConfigurationInstance if is_windows_containers() else ConfigurationInstance


def init_from_config(conf):
    id_ = conf.general.get('cluster_id')
    if id_ is None:
        id_ = uuid.uuid4().hex
        logger.info('Setting Cluster ID to %s', id_)
        conf.general.cluster_id = id_
        conf.general.save()


def init_cluster(config_folder=None):
    configuration_instance_class = _get_configuration_instance_class()
    configuration_instance_class.load_config(config_folder)
    init_from_config(configuration_instance_class.get_config())
    docker_init_from_config()


def docker_client(host_base_url=None, version='auto'):
    if host_base_url is None:
        return docker.from_env(version=version)

    return docker.DockerClient(host_base_url, version=version)


ADMIN_VOLUME = {'/var/run/docker.sock': {'bind': '/var/run/docker.sock'}}


def docker_init_from_config():
    import os

    def is_ci():
        return os.environ.get('CI')

    docker_socket = list(ADMIN_VOLUME.keys())[0]
    if not is_windows_containers() and not os.path.exists(docker_socket) and not is_ci():
        from click import BadParameter
        raise BadParameter('Docker host: {} must be mounted'.format(docker_socket))
