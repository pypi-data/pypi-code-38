# -*- coding: utf-8 -*-
import os


class MlEnvironmentVariables(object):
    __ml_env_var_mapping = {
        'ML': 'in_context',
        'ML_CLUSTER_ID': 'resource_manager',
        'ML_CLUSTER_MANAGER': 'socket_server',
        'ML_OUTPUT_DATA_VOLUME': 'output_volume_id',
    }

    @classmethod
    def get_ml_env(cls):
        return {k: v for k, v in os.environ.items() if k.startswith('ML_') or k == 'ML'}

    @classmethod
    def _ml_map_value(cls, rm_data, key, value):
        def map_value(prefix, section=None):
            if not key.startswith(prefix):
                return

            section = rm_data[section] if section else rm_data

            actual_prefix = prefix + '_'
            actual_key = key[len(actual_prefix):].lower()

            section[actual_key] = value

            return True

        if key in cls.__ml_env_var_mapping:
            rm_data[cls.__ml_env_var_mapping[key]] = value
            return

        if key.startswith('ML_MOUNT_'):
            if not value.startswith('/'):
                value = '/' + value

            rm_data['volumes'].append(value)
            return

        if map_value('ML_DATA', 'data'):
            return

        if map_value('ML'):
            return

    @classmethod
    def _rm_map_values(cls, mali_env):
        rm_data = {'data': {}, 'volumes': []}

        for k, v in mali_env.items():
            cls._ml_map_value(rm_data, k, v)

        rm_data['volumes'] = list(sorted(rm_data['volumes']))

        return rm_data

    @classmethod
    def get_rm_env(cls):
        mali_env = cls.get_ml_env()

        if mali_env:
            return cls._rm_map_values(mali_env)

        return {}
