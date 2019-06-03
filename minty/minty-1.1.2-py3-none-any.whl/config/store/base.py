import re
from abc import ABC, abstractmethod

from ... import Base


class ConfigurationNotFound(FileNotFoundError):
    """Exception raised when configuration can't be found
    """

    pass


class ConfigStoreBase(ABC, Base):
    """Abstract base class for configuration store plugins
    """

    ALLOWED_CONFIG_NAME = r"^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)*$"

    @abstractmethod
    def retrieve(self, name: str):
        """Retrieve configuration - base/superclass method

        :param name: Name of the configuration to retrieve
        :param name: str
        :raises NameError: If the configuration name is invalid
        """

        if not re.match(self.ALLOWED_CONFIG_NAME, name):
            self.statsd.get_counter().increment("invalid_config_name")
            raise NameError
