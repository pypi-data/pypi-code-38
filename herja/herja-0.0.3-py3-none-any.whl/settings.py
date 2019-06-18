
import hashlib
import logging
import json
import os

from .assertions import assert_not_none
from .constants import SETTINGS_PATH, EMPTY_DICT_SHA256_HEXDIGEST
from .conversions import to_bytes, to_str


class Settings(dict):
    """Store settings for use and write them back out to disk."""

    def __init__(self, path=None):
        """Load the settings from the settings path, if it exists."""
        super(Settings, self).__init__()
        self.read_digest = EMPTY_DICT_SHA256_HEXDIGEST
        self.path = path

    def __enter__(self):
        """If this is a with block, automatically read the file for usage."""
        if self.path is None:
            self.path = SETTINGS_PATH
        logging.info('Settings path: %s', self.path)
        self.read(self.path)
        return self

    def __exit__(self, exc_type, exc_val, tb):
        """If this is a with block and we have a path, write the data to disk."""
        if self.read_digest != self.digest:
            self.write(self.path)

    @property
    def current(self):
        """Get a dictionary representation of the current Settings object."""
        return {key: self[key] for key in self}

    @property
    def digest(self):
        """Return a hexdigest of a json dump of this dictionary object."""
        return hashlib.sha256(to_bytes(json.dumps(self.current))).hexdigest()

    def read(self, path=SETTINGS_PATH):
        """Load settings from a file."""
        if not os.path.isfile(path):
            logging.warning('Settings path not found: %s', self.path)
            return 0

        logging.info('Settings reading from: %s', self.path)
        with open(path, 'rb') as f:
            data = f.read()

        self.update(json.loads(data))
        self.read_digest = self.digest

    def write(self, path=SETTINGS_PATH):
        """Write the settings back out to a file."""
        if path is None:
            path = self.path
        assert_not_none(path)
        print(self.current)
        with open(path, 'wb') as f:
            f.write(to_bytes(json.dumps(self.current)))
