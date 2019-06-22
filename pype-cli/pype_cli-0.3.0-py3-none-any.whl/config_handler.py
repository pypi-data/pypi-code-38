# -*- coding: utf-8 -*-
"""Pype configuration handler."""

from json import dump, load
from os import environ
from os.path import dirname, isfile, join
from sys import stderr

from colorama import Fore, Style

from jsonschema import ValidationError, validate

from pype.constants import ENV_CONFIG_FILE
from pype.exceptions import PypeException
from pype.util.iotools import resolve_path


class PypeConfigHandler():
    """Pype configuration handler."""

    DEFAULT_CONFIG_FILE = resolve_path('~/.pype-config.json')
    LOCAL_CONFIG_FILE = join(dirname(dirname(__file__)), 'config.json')
    DEFAULT_CONFIG = {
        'plugins': [],
        'aliases': [],
        'core_config': {}
    }
    CONFIG_SCHEMA_PATH = join(dirname(__file__), 'config-schema.json')
    CONFIG_SCHEMA = load(open(CONFIG_SCHEMA_PATH))

    def __init__(self):
        """Construct a default configuaration handler."""
        self.config = None
        self.filepath = None

    def resolve_config_file(self):
        """Resolve the configuration using various options."""
        try:
            # Priority 1: Environment variable
            self.filepath = environ[ENV_CONFIG_FILE]
        except KeyError:
            # Priority 2: ~/.pype-config.json
            if isfile(self.DEFAULT_CONFIG_FILE):
                self.filepath = self.DEFAULT_CONFIG_FILE
            # Priority 3: ./config.json
            elif isfile(self.LOCAL_CONFIG_FILE):
                self.filepath = self.LOCAL_CONFIG_FILE
        # Priority 4: Create a template config from scratch
        if not self.filepath:
            dump(self.DEFAULT_CONFIG, open(self.DEFAULT_CONFIG_FILE, 'w+'))
            self.filepath = self.DEFAULT_CONFIG_FILE
        self.config = load(open(self.filepath, 'r'))
        self.validate_config(self.config)

    def get_json(self):
        """Get pype configuration as JSON object."""
        if not self.config:
            self.resolve_config_file()
        return self.config

    def get_filepath(self):
        """Get absolute filepath to configuration JSON file."""
        if not self.config:
            self.resolve_config_file()
        return self.filepath

    def set_json(self, config):
        """Validate, set and persist configuration from JSON object."""
        self.validate_config(config)
        self.config = config
        # always update config file as well
        dump(self.config, open(self.filepath, 'w+'), indent=4)

    def validate_config(self, config):
        """Validate given config file against schema definition."""
        try:
            validate(instance=config, schema=self.CONFIG_SCHEMA)
        except ValidationError as err:
            print(Fore.RED + str(err) + Style.RESET_ALL + '\n', file=stderr)
            raise PypeException(
                'Configuration file is not valid. See above for details '
                + 'and refer to the schema file at {}'.format(
                    self.CONFIG_SCHEMA_PATH))
        return True
