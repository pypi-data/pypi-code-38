# -*- coding: utf-8 -*-
import os
import warnings

import six

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

import abc


config_file_name = 'config'


def parse_bool(val):
    return val.lower() in ['true', '1']


_BOOLEAN_STATES = {'1': True, 'yes': True, 'true': True, 'on': True,
                   '0': False, 'no': False, 'false': False, 'off': False}

SHARED_STORAGE_VOLUME_FIELD_NAME = 'shared_storage_volume_id'


@six.add_metaclass(abc.ABCMeta)
class _DataVolumeConfig:
    @abc.abstractmethod
    def get_boolean(self, section, name, default_value=False, must_exists=False):
        pass

    @abc.abstractmethod
    def items(self, section, must_exists=False):
        pass

    @property
    def embedded(self):
        val = self.general_config.get('embedded', False)

        if isinstance(val, six.string_types):
            val = parse_bool(val)

        return val

    @property
    def org(self):
        return self.get('org')

    @property
    def volume_id(self):
        return int(self.get('id', mandatory=True))

    @property
    def foreign_storage_volume_id(self):
        foreign_storage_volume_id = self.object_store_config.get(SHARED_STORAGE_VOLUME_FIELD_NAME)
        if foreign_storage_volume_id is None:
            return None

        return int(foreign_storage_volume_id)

    @property
    def storage_volume_id(self):
        return self.foreign_storage_volume_id or self.volume_id

    @property
    def db_type(self):
        return self.db_config.get('type')

    @property
    def object_store_type(self):
        return self.object_store_config.get('type')

    def get(self, key, mandatory=False):
        if mandatory:
            return self.general_config[key]

        return self.general_config.get(key)

    @property
    def data_path(self):
        return self.general_config.get('datapath')

    @property
    def general_config(self):
        return self.items('general')

    @property
    def db_config(self):
        return self.items('db')

    @property
    def bucket_name(self):
        return self.object_store_config.get('bucket_name')

    @property
    def object_store_config(self):
        object_store_config = self.items('object_store')

        return object_store_config


class ReadOnlyDataVolumeConfig(_DataVolumeConfig):
    def __init__(self, dict_config):
        self._dict_config = dict_config

    def get_boolean(self, section, name, default_value=False, must_exists=False):
        try:
            try:
                val = str(self.items(section)[name])
            except KeyError:
                raise configparser.NoOptionError(name, section)

            if val.lower() not in _BOOLEAN_STATES:
                raise ValueError('Not a boolean: {}'.format(val))

            return _BOOLEAN_STATES[val.lower()]
        except (configparser.NoSectionError, configparser.NoOptionError):
            if must_exists:
                raise

            return default_value

    def items(self, section, must_exists=False):
        try:
            return self._dict_config[section]
        except KeyError:
            if must_exists:
                raise configparser.NoSectionError(section)

            return {}


class DataVolumeConfig(_DataVolumeConfig):
    def __init__(self, path, general_config_path=None):
        self._config_file = os.path.join(path, config_file_name)

        parser = configparser.RawConfigParser()
        config_files = [self._config_file]
        if general_config_path is not None:
            config_files.append(general_config_path)

        parser.read(config_files)

        self._parser = parser
        self._sections = {}

    def get_boolean(self, section, name, default_value=False, must_exists=False):
        try:
            return self._parser.getboolean(section, name)
        except (configparser.NoSectionError, configparser.NoOptionError):
            if must_exists:
                raise

            return default_value

    def __items_from_parse(self, parser, section, must_exists):
        try:
            if section not in self._sections:
                self._sections[section] = dict(parser.items(section))

            return self._sections[section]
        except configparser.NoSectionError:
            if must_exists:
                raise

            return self._sections.setdefault(section, {})

    def set(self, section, key, val):
        try:
            self._parser.add_section(section)
        except configparser.DuplicateSectionError:
            pass

        if six.PY2 and isinstance(val, str):
            val = val.encode('utf8')

        self._parser.set(section, key, val)

    def _write(self, fo):
        self._parser.write(fo)

    def save(self):
        with open(self._config_file, 'w') as configfile:
            self._write(configfile)

    def items(self, section, most_exists=False):
        return self.__items_from_parse(self._parser, section, must_exists=most_exists)

    def update_and_save(self, d):
        for section, section_values in d.items():
            for key, val in section_values.items():
                if val is None:
                    continue

                self.set(section, key, val)

        self.save()

    def remove_option(self, section, name):
        try:
            self._parser.remove_option(section, name)
        except configparser.NoSectionError:
            pass
