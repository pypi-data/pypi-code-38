# -*- coding: utf-8 -*-
import errno
import logging
import os

import sys

from .eprint import eprint

try:
    # noinspection PyPep8Naming
    import ConfigParser as configparser
except ImportError:
    # noinspection PyUnresolvedReferences
    import configparser

_missing_link_config = 'missinglink.cfg'

default_api_host = 'https://missinglinkai.appspot.com'
default_host = 'https://missinglink.ai'
default_resource_management_socket_server = 'ws://rm-ws-prod.missinglink.ai'
default_resource_management_config_volume = 'ml_config'
default_rm_manager_image = 'missinglinkai/ml-rm-docker:latest'
default_ml_image = 'missinglinkai/missinglink:latest'
default_rm_container_name = 'missinglink_docker_resource_manger'


def get_prefix_section(config_prefix, section):
    return '%s-%s' % (config_prefix, section) if config_prefix else section


def default_missing_link_folder():
    return os.path.join(os.path.expanduser('~'), '.MissingLinkAI')


def default_config_file(config_prefix, filename=None):
    filename = filename or _missing_link_config
    filename_with_prefix = '%s-%s' % (config_prefix, filename) if config_prefix else filename
    return os.path.join(default_missing_link_folder(), filename_with_prefix)


def _safe_getcwd():
    try:
        FileNotFoundError
    except NameError:
        # py2.X
        FileNotFoundError = (IOError, OSError)

    try:
        return os.getcwd()
    except FileNotFoundError:
        return None


def _is_valid_config_file(possible_path, filename_with_prefix):
    if possible_path is None:
        return None

    candidate_config_file = os.path.join(possible_path, filename_with_prefix)

    if os.path.isfile(candidate_config_file):
        logging.debug('config file at %s', candidate_config_file)
        return candidate_config_file


def find_first_file(config_prefix, filename=None):
    logging.debug('find config file %s %s', config_prefix, filename)

    filename = filename or _missing_link_config

    filename_with_prefix = '%s-%s' % (config_prefix, filename) if config_prefix else filename

    possible_paths = [_safe_getcwd(), default_missing_link_folder()]

    for possible_path in possible_paths:
        candidate_config_file = _is_valid_config_file(possible_path, filename_with_prefix)
        if candidate_config_file is None:
            continue

        return candidate_config_file

    logging.debug('config file not found')

    return None


def _safe_create_dir(dirname):
    if not dirname or os.path.exists(dirname):
        return

    try:
        os.makedirs(dirname)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise


class Config(object):
    def __init__(self, config_prefix=None, config_file=None, **kwargs):
        self.config_file = config_file
        self.config_prefix = config_prefix

        if self.config_file:
            self.config_file_abs_path = os.path.abspath(config_file)
        else:
            self.config_file_abs_path = find_first_file(self.config_prefix)

        if config_file and not os.path.exists(self.config_file_abs_path):
            eprint('config file %s not found' % self.config_file_abs_path)
            sys.exit(1)
        elif config_prefix and self.config_file_abs_path is None:
            eprint('config file for %s not found' % config_prefix)
            sys.exit(1)

        self.config_prefix = config_prefix

        parser = configparser.RawConfigParser()
        readonly_parser = configparser.RawConfigParser()

        if self.config_file_abs_path is not None:
            logging.debug('using config file %s', self.config_file_abs_path)
            parser.read([self.config_file_abs_path])
            readonly_parser.read([self.config_file_abs_path])

        self.parser = parser
        self.readonly_parser = readonly_parser

        self.__append_kwargs(**kwargs)

    def __append_kwargs(self, **kwargs):
        for section, values in kwargs.items():
            try:
                self.parser.add_section(section)
                self.readonly_parser.add_section(section)
            except configparser.DuplicateSectionError:
                pass

            for key, val in values.items():
                self.parser.set(section, key, val)
                self.readonly_parser.set(section, key, val)

    @property
    def init_dict(self):
        return dict(config_file=self.config_file, config_prefix=self.config_prefix)

    @property
    def api_host(self):
        return self.general_config.get('api_host', default_api_host)

    @property
    def ml_image(self):
        return self.resource_management_config.get('ml_image', default_ml_image)

    @property
    def rm_socket_server(self):
        return self.resource_management_config.get('socket_server', default_resource_management_socket_server)

    @property
    def rm_config_volume(self):
        return self.resource_management_config.get('config_volume', '{}_{}'.format(self.config_prefix or 'default', default_resource_management_config_volume))

    @property
    def rm_container_name(self):
        return self.resource_management_config.get('container_name', '{}_{}'.format(default_rm_container_name, self.config_prefix or 'default'))

    @property
    def rm_manager_image(self):
        return self.resource_management_config.get('manager_image', default_rm_manager_image)

    @property
    def host(self):
        host = self.general_config.get('host', default_host)

        if not host.startswith('http://') and not host.startswith('https://'):
            host = 'https://' + host

        return host

    def get_prefix_section(self, section):
        return get_prefix_section(self.config_prefix, section)

    @property
    def token_config(self):
        section_name = self.get_prefix_section('token')
        return self.items(section_name)

    @property
    def general_config(self):
        return self.readonly_items('general', most_exists=self.config_prefix is not None)

    @property
    def resource_management_config(self):
        return self.readonly_items('resource_management', most_exists=False)

    @property
    def resource_manager_config(self):
        section_name = self.get_prefix_section('resource_manager')
        return self.items(section_name)

    @property
    def refresh_token(self):
        return self.token_config.get('refresh_token')

    @property
    def id_token(self):
        return self.token_config.get('id_token')

    @property
    def token_data(self):
        import jwt

        return jwt.decode(self.id_token, verify=False) if self.id_token else {}

    @property
    def user_id(self):
        import jwt

        data = jwt.decode(self.id_token, verify=False) if self.id_token else {}

        return data.get('uid')

    @classmethod
    def items_from_parse(cls, parser, section, most_exists):
        try:
            return dict(parser.items(section))
        except configparser.NoSectionError:
            if most_exists:
                raise

            return {}

    def items(self, section, most_exists=False):
        return self.items_from_parse(self.parser, section, most_exists=most_exists)

    def readonly_items(self, section, most_exists=False):
        return self.items_from_parse(self.readonly_parser, section, most_exists=most_exists)

    def set(self, section, key, val):
        try:
            self.parser.add_section(section)
        except configparser.DuplicateSectionError:
            pass

        self.parser.set(section, key, val)

    def _write(self, fo):
        self.parser.write(fo)

    def save(self):
        # we always save the config prefix file into the default folder
        if self.config_file_abs_path is None:
            self.config_file_abs_path = find_first_file(self.config_prefix) if not self.config_prefix else None
            self.config_file_abs_path = self.config_file_abs_path or default_config_file(self.config_prefix)

        _safe_create_dir(os.path.dirname(self.config_file_abs_path))

        with open(self.config_file_abs_path, 'w') as configfile:
            self._write(configfile)

    def update_and_save(self, d):
        for section, section_values in d.items():
            section_name_with_prefix = self.get_prefix_section(section)
            for key, val in section_values.items():
                self.set(section_name_with_prefix, key, val)

        self.save()
