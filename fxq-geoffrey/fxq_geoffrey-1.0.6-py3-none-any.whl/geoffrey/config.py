import logging
import os
from configparser import ConfigParser

import appdirs
from fxq.core.stereotype import Component

from fxq.geoffrey.exception import ConfigNotFoundException

CONFIG_FOLDER = "%s/geoffrey" % appdirs.user_config_dir()
CONFIG_FILE = "%s/config.ini" % CONFIG_FOLDER

LOGGER = logging.getLogger("ApplicationConfig")


@Component
class ApplicationConfig:

    def __init__(self):
        self._config = ConfigParser()
        self._config.read(CONFIG_FILE)
        LOGGER.info("Successfully Loaded Config %s" % CONFIG_FILE)

    def create_new_config(self, config_uri):
        os.makedirs(CONFIG_FOLDER, exist_ok=True)
        with open(CONFIG_FILE, 'w') as config_file:
            self._config["choices"] = {"uri": config_uri}
            self._config.write(config_file)

    def get_config_uri(self):
        try:
            return self._config["choices"]["uri"]
        except KeyError:
            raise ConfigNotFoundException("Config not found at %s" % CONFIG_FILE)
