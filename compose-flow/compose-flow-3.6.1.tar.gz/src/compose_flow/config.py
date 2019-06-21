import os
import pathlib

from functools import lru_cache

from compose_flow.utils import yaml_load


DEFAULT_DC_CONFIG_FILE = pathlib.Path('compose') / 'compose-flow.yml'

# check to see if an overlay file is provided in the environment
DC_CONFIG_PATH = os.environ.get('DC_CONFIG_FILE', DEFAULT_DC_CONFIG_FILE)

DC_CONFIG_ROOT, DC_CONFIG_FILE = os.path.split(DC_CONFIG_PATH)


@lru_cache()
def get_config() -> dict:
    data = None

    if os.path.exists(DC_CONFIG_FILE):
        with open(DC_CONFIG_FILE, 'r') as fh:
            data = yaml_load(fh)

    return data
