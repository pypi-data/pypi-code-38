# -*- coding: utf-8 -*-

import logging
import os
import base64

import six
import docker

from missinglink.commands.utils import is_windows_containers
from missinglink.legit.path_utils import normalize_path
from missinglink.commands.utilities.docker_tools.docker_tools import DockerTools


class WindowsDockerTools(DockerTools):

    @staticmethod
    def _get_default_gateway():
        import netifaces

        try:
            gateways = netifaces.gateways()
            return gateways['default'][netifaces.AF_INET][0]
        except Exception as exc:
            logging.error('Could not get default gateway address: %s', exc)
            raise Exception('Can not initialize docker client')

    @classmethod
    def _get_docker_host_base_url(cls):
        docker_host = os.environ.get('ML_DOCKER_HOST', cls._get_default_gateway())
        docker_host_port = cls._get_docker_host_port()
        return '{}:{}'.format(docker_host, docker_host_port)

    @staticmethod
    def _get_docker_host_port():
        return os.environ.get('ML_DOCKER_HOST_PORT', '2375')

    @classmethod
    def _get_docker_client(cls):
        if is_windows_containers():
            docker_host_base_url = cls._get_docker_host_base_url()
            return docker.DockerClient(docker_host_base_url, version='auto')

        return docker.from_env(version='auto')

    def _get_run_volumes(self):
        return [self._get_config_volume(), self._get_commands_volume()]

    def _get_commands_volume(self):
        return {self.config.rm_commands_volume: {'bind': normalize_path('/{}'.format(self.ML_COMMANDS_VOLUME))}}

    def _apply_ssh_params(self, ssh_key):
        if ssh_key is not None:
            return ['--ssh-private-key-b64', base64.b64encode(ssh_key.encode('ascii')).decode('utf-8')]

        return []

    def _get_ml_data_param(self, ml_data):
        ml_data = self._encode_if_needed(ml_data)
        return ['--ml-config-file-data-b64', base64.b64encode(ml_data).decode('utf-8')]

    @staticmethod
    def _encode_if_needed(data):
        if data and isinstance(data, six.string_types):
            return data.encode('utf-8')

        return data

    def ensure_rms_volumes(self, force):
        self._ensure_config_volume(force)
        self._ensure_commands_volume(force)

    def _ensure_commands_volume(self, force):
        self._ensure_volume(self.config.rm_commands_volume, force)
