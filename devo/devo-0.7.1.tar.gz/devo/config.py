from collections import defaultdict, MutableMapping
from pathlib import Path

from ruamel.yaml import YAML

CONFIG_FILE = 'devo.yaml'

CREDENTIALS_FILE = '.devo/creds.yaml'

yaml = YAML()


def config_dict():
    return defaultdict(dict)


def read_yaml(filepath):
    data = config_dict()
    data.update(yaml.load(filepath))
    return data


def persist_yaml(filepath, data):
    config = yaml.load(filepath)
    config.update(data)
    yaml.dump(config, filepath)


def read_config():
    current_path = Path.cwd() / CONFIG_FILE
    return read_yaml(current_path)


def persist_config(data):
    current_path = Path.cwd() / CONFIG_FILE
    persist_yaml(current_path, data)


def read_creds():
    current_path = Path.cwd() / CREDENTIALS_FILE
    try:
        return read_yaml(current_path)
    except FileNotFoundError:
        # Todo: read creds from env
        return []


def persist_creds(data):
    current_path = Path.cwd() / CREDENTIALS_FILE
    persist_yaml(current_path, data)


def flatten(d, parent_key='', sep='_'):
    items = []
    for key, value in d.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


def config_to_context():
    config = read_config()
    return flatten(config)
