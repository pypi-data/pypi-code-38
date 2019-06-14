"""Console script for symbol_please."""
import logging
import json
import os

import symbol_please

_LOGGER = logging.getLogger(__name__)

CONFIG_HOME = os.environ.get(
    "XDG_CONFIG_HOME", os.path.join(os.path.expanduser('~'), '.config'))
CONFIG_FILE_DIR = os.path.join(CONFIG_HOME, symbol_please.__name__)
CONFIG_FILE_PATH = os.path.join(CONFIG_FILE_DIR, 'settings.json')

VERSION = 1


def load_config():
    """Load configuration file."""
    if not os.path.isfile(CONFIG_FILE_PATH):
        return {
            '_version': VERSION,
            'profiles': {},
        }

    _LOGGER.info("Loading config file '%s'", CONFIG_FILE_PATH)
    with open(CONFIG_FILE_PATH, 'r') as config_file:
        config = json.load(config_file)

        if config.get('_version') != VERSION:
            raise ValueError("Invalid config version detected")

        return config


def save_config(config):
    """Save the configuration file."""
    os.makedirs(CONFIG_FILE_DIR, exist_ok=True)

    _LOGGER.info("Saving config file '%s'", CONFIG_FILE_PATH)
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        return json.dump(config, config_file, indent=2)
