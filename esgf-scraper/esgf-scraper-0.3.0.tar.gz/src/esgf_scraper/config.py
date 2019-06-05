import os
import sys
from os.path import exists, join

import yaml


class ConfigLoader(object):
    """Store the configuration for the application

    Configuration values are stored on disk as YAML. An example of a configuration file is provided in root of the project.

    >>> config = ConfigLoader()
    >>> config['value']
    """

    def __init__(self):
        self._config = {}
        self.is_loaded = False

    def load_from_file(self, fname):
        with open(fname) as fh:
            conf = yaml.load(fh, Loader=yaml.SafeLoader)

        self._config.update(**{k.lower(): v for k, v in conf.items()})
        self.is_loaded = True

    def load_config(self):
        for p in [".", os.environ["HOME"]]:
            fname = join(p, "esgf_scraper.conf")
            if exists(fname):
                return self.load_from_file(fname)
        print("Could not find configuration file. Existing")
        sys.exit(1)

    def get(self, key, default=None):
        """
        Get value for a given key, falling back to a default value if not present.

        Parameters
        ----------
        key : str
            Key
        default: Any
            Default value returned if no configuration for `key` is present.

        Returns
        -------
        Value with key `item`. If not value is present `default` is returned.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        if not self.is_loaded:
            self.load_config()

        return self._config[key.lower()]

    def update(self, conf):
        self._config.update(conf)
