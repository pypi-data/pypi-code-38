import os
import copy
import importlib

import cerberus

from unv.utils.collections import update_dict_recur


def _convert_value(value):
    if value == 'False':
        value = False
    elif value == 'True':
        value = True
    elif value.isdigit():
        value = int(value)
    return value


def validate_schema(schema, settings):
    validator = cerberus.Validator(schema)
    if not validator.validate(settings):
        raise ValueError(f"Error validation settings {validator.errors}")
    return settings


class ComponentSettings:
    KEY = ''
    SCHEMA = {}
    DEFAULT = {}

    @staticmethod
    def create(settings: dict = None, base_settings: dict = None) -> dict:
        """Create app settings, overrided by env."""
        settings = settings or {}
        if base_settings:
            settings = update_dict_recur(settings, base_settings)
        for key, value in os.environ.items():
            if 'SETTINGS_' not in key:
                continue
            current_settings = settings
            parts = [
                part.lower()
                for part in key.replace('SETTINGS_', '').split('_')
            ]
            last_index = len(parts) - 1
            for index, part in enumerate(parts):
                if index == last_index:
                    current_settings[part] = _convert_value(value)
                else:
                    current_settings = current_settings.setdefault(part, {})
        return settings

    def __init__(self):
        key = self.__class__.KEY
        if not key:
            raise ValueError(f"Provide 'KEY' for settings")

        if 'SETTINGS' in os.environ:
            module_path = os.environ['SETTINGS']
            module = importlib.import_module(module_path)
            app_settings = module.SETTINGS
        else:
            app_settings = {}

        settings = copy.deepcopy(self.__class__.DEFAULT)
        settings = update_dict_recur(
            settings, app_settings.get(self.__class__.KEY, {}))
        settings = validate_schema(self.__class__.SCHEMA, settings)

        self._data = settings


class AppSettings(ComponentSettings):
    KEY = 'app'
    SCHEMA = {
        'env': {
            'type': 'string',
            'allowed': ['prod', 'dev', 'test'],
            'required': True
        },
        'components': {
            'type': 'list',
            'empty': True,
            'schema': {'type': 'string'},
            'required': True
        }
    }
    DEFAULT = {
        'env': 'prod',
        'components': [],
    }

    @property
    def is_dev(self):
        return self._data['env'] == 'dev'

    @property
    def is_prod(self):
        return self._data['env'] == 'prod'

    @property
    def is_test(self):
        return self._data['env'] == 'test'

    def get_components(self):
        for component in self._data['components']:
            component = '{}.app'.format(component)
            yield importlib.import_module(component)


SETTINGS = AppSettings()
