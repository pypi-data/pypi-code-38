# -*- coding: utf-8 -*-

import configparser
import os
import sys

from omxware import omxware


class OmxConfig:

    def __init__(self):
        self.config = configparser.RawConfigParser()

        dir_path = os.path.dirname(
            os.path.realpath(os.path.abspath(sys.modules[omxware.omxware.__module__].__file__))) + '/config/omxware.cfg'

        self.config.read(dir_path)

    @staticmethod
    def __load_config():
        config = configparser.RawConfigParser()

        dir_path = os.path.dirname(
            os.path.realpath(os.path.abspath(sys.modules[omxware.omxware.__module__].__file__))) + '/config/omxware.cfg'

        config.read(dir_path)

        return config

    @staticmethod
    def get_server(env_type='master'):
        config = OmxConfig.__load_config()

        if env_type == 'dev':
            section = 'OmxwareDev'
        elif env_type == 'dev_search':
            section = 'OmxwareDevSearch'
        elif env_type == 'master':
            section = 'OmxwareMaster'
        elif env_type == 'local':
            section = 'OmxwareLocal'
        else:
            section = 'OmxwareMaster'

        server = config.get(section, 'server.host') + ':' + config.get(section, 'server.port')

        return server

    @staticmethod
    def help_info(env_type='master'):
        config = OmxConfig.__load_config()

        if env_type == 'dev':
            section = 'OmxwareDev'
        elif env_type == 'dev_search':
            section = 'OmxwareDevSearch'
        elif env_type == 'master':
            section = 'OmxwareMaster'
        elif env_type == 'local':
            section = 'OmxwareLocal'
        else:
            section = 'OmxwareMaster'

        server = config.get(section, 'server.host') + ':' + config.get(section, 'server.port')
        ui = config.get(section, 'server.host') + ':' + config.get(section, 'ui.port')

        docs_link = ui + config.get('omxware', 'doc_link_slug')
        swagger_link = server + config.get('omxware', 'services_swagger_slug')
        forums_link = config.get('omxware', 'forums_link')
        contact_info = config.get('omxware', 'admin_contact_email')

        help_info = '---------------------------------------------------------------------------' + "\n" \
                    '* OMXWare Useful Links' + "\n" \
                    '---------------------------------------------------------------------------' + "\n" \
                    'Hub:           ' + ui + "/ \n" \
                    'Services:      ' + swagger_link + "\n" \
                    'Forums:        ' + forums_link + " \n" \
                    'Documentation: ' + docs_link + "\n" \
                    'Contact:       ' + contact_info + "\n" \
                    '---------------------------------------------------------------------------'

        return help_info

