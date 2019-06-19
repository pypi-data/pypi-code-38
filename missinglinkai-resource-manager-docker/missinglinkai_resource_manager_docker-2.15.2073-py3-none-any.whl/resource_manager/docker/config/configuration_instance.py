# -*- coding: utf-8 -*-
import os
import socket


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
        from missinglink.resource_manager.docker.config import logger, ConfigFile

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
        from missinglink.resource_manager.docker.config import load_config

        if cls.loaded_config is None:
            load_config()

        return cls.loaded_config
