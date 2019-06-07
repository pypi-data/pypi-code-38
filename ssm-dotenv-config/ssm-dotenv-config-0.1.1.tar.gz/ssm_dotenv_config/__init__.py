import os
import boto3
import ujson as json
from dotenv import load_dotenv
from vital.tools.strings import camel_to_underscore


__all__ = 'get',


def get(config=None, ssm_path=None, ssm_client=None, dotenv_path=None):
    config = config or {}
    ssm = ssm_client or boto3.client('ssm', 'us-east-1')

    # Sets parameters in the route config
    def set_params(name, value):
        cfg = config
        _, *keys = name.split('__')

        for key in keys[:-1]:
            if cfg.get(key) is None:
                cfg[key] = {}
            cfg = cfg[key]

        try:
            value = json.loads(value)
        except ValueError:
            pass

        if isinstance(value, list):
            if isinstance(cfg.get(keys[-1]), list):
                value = list({*cfg[keys[-1]], *value})
        elif isinstance(value, dict):
            if isinstance(cfg.get(keys[-1]), dict):
                value = {**cfg[keys[-1]], **value}

        cfg[keys[-1]] = value

    # Adds configs from SSM parameter store
    if ssm_path is not None:
        ssm_options = {
            'Path': ssm_path,
            'Recursive': True,
            'WithDecryption': True
        }
        while True:
            response = ssm.get_parameters_by_path(**ssm_options)

            for param in response['Parameters']:
                set_params(
                    f'config__{"__".join(camel_to_underscore(param["Name"]).split("/")[2:])}',
                    param['Value']
                )

            try:
                ssm_options['NextToken'] = response['NextToken']
            except KeyError:
                break

    if dotenv_path is not None and os.path.isfile(dotenv_path):
        load_dotenv(dotenv_path)

    # Adds configs from os.environ
    for name, value in os.environ.items():
        name = name.lower()
        if name.startswith('config__'):
            set_params(name, value)

    return config
