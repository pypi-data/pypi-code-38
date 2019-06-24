"""
Utility method for loading properties form the configuration file and environment variables.
"""

import configparser
import logging
import os

# Relative location of configuration file
_PROGRAM_CONFIG = '../config.ini'
_LOGGER_FILENAME = 'stderr.log'


class Config:
    """A configuration supplier.

    An object for reading configuration properties. Properties are injected with
    the following priority. Properties with higher priority overwrite those
    with lower priority.

    1. Program defaults
    2. The 'DEFAULT' section in 'config.ini'
    3. The environment in the 'config.ini' file set by the 'ENV' environment variable
    4. Runtime system environment variables
    """

    def __init__(self, environment=os.getenv("ENV", 'DEFAULT').upper()):

        # Create an application logger
        logger = logging.getLogger("termlink")
        logging.basicConfig(filename=_LOGGER_FILENAME)

        # Set the logging level
        if environment == "TEST":
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        logger.info("The logging level has been set to %s", logger.level)

        parser = configparser.ConfigParser(os.environ, strict=False)

        # Get the absolute path based on the execution directory
        root = os.path.abspath(os.path.dirname(__file__))
        config = os.path.join(root, _PROGRAM_CONFIG)

        configs = [config]
        parser.read(configs)

        self.environment = environment
        self.logger = logger
        self.parser = parser

    def get_property(self, property_name, default=None):
        """Get a property value from the configuration.

        The os environment variables are first checked. If the property
        does not exists there it is read from the configuration file.

        Args:
            property_name (str):    A name, or key, of a property

        Returns:
            The property value associated with the property_name
        """
        if property_name in os.environ:
            return os.environ[property_name]

        return self.parser.get(self.environment, property_name, fallback=default)
