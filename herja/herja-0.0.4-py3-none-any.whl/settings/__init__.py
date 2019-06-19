"""A module for handling stored settings."""


import hashlib
import json
import os

from ..assertions import assert_not_none
from ..constants import EMPTY_DICT_SHA256_HEXDIGEST
from ..conversions import to_bytes
from ..logging import get_logger


__all__ = [
    'SETTINGS_PATH',
    'Settings'
]


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGGER = get_logger()
SETTINGS_PATH = os.path.join(BASE_DIR, 'settings.json')


class Settings(dict):
    """Store settings for use and write them back out to disk."""

    # special functions
    def __init__(self, path=None):
        """Load the settings from the settings path, if it exists."""
        super(Settings, self).__init__()
        self.read_digest = EMPTY_DICT_SHA256_HEXDIGEST
        self.path = path

    def __enter__(self):
        """If this is a with block, automatically read the file for usage."""
        if self.path is None:
            self.path = SETTINGS_PATH
        LOGGER.info('Settings path: "%s"', self.path)
        self.read(self.path)
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        """If this is a with block and we have a path, write the data to disk."""
        if self.changed:
            self.write(self.path)

    def __getitem__(self, key):
        """Perform a get on this item, but prompt if the key does not exist."""
        result = super(Settings, self).get(key, None)
        while result is None:
            value = input('Enter a value for "{0}": '.format(key)).strip()
            if not value:
                continue
            if value.isdigit():
                value = int(value)
            self[key] = value
            result = super(Settings, self).get(key, None)
        return result

    # internal functions
    def _get_path(self, path):
        """Refine the given path between path, self.path, and SETTINGS_PATH."""
        if path is None:
            if self.path is None:
                self.path = path = SETTINGS_PATH
            else:
                path = self.path
        else:
            if self.path is None:
                self.path = path
        return path

    # public properties and functions
    @property
    def changed(self):
        """Return whether the read digest is the same as the current digest."""
        return self.read_digest != self.digest

    @property
    def current(self):
        """Get a dictionary representation of the current Settings object."""
        return {key: self[key] for key in self}

    @property
    def digest(self):
        """Return a hexdigest of a json dump of this dictionary object."""
        return hashlib.sha256(to_bytes(json.dumps(self.current))).hexdigest()

    def read(self, path=None):
        """Load settings from a json file."""
        path = self._get_path(path)
        if not os.path.isfile(path):
            LOGGER.warning('Settings path not found: "%s"', self.path)
            return 1

        LOGGER.info('Settings reading from: "%s"', self.path)
        with open(path, 'rb') as settings_file:
            data = settings_file.read()

        self.update(json.loads(data))
        self.read_digest = self.digest
        return 0

    def write(self, path=None):
        """Write the settings back out to a json file."""
        path = self._get_path(path)
        assert_not_none(path)
        with open(path, 'wb') as settings_file:
            settings_file.write(to_bytes(json.dumps(self.current)))
