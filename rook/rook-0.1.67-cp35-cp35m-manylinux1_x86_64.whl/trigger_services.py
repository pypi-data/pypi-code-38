"""This module is in charge of managing all the trigger services.

Trigger services are the components responsible managing the execution of Augs.

Each trigger service must export the following methods:
- __init__(self, output) - Construct the object, receives a point to the Output object.
- remove_aug(self, aug_id) - Remove an Aug by it's id.
- clear_augs(self) - Remove all Augs.

Services are loaded from the services packages.
"""
from six import itervalues

from .services import BdbLocationService, ImportService, LoggingLocationService, HttpServerService

from .exceptions import RookServiceMissing

from .logger import logger


class TriggerServices(object):
    """This class implements all the module's functionality."""
    def __init__(self):
        """Load and initialize all the trigger services."""
        self._services = dict()

    def get_service(self, name):
        """Return the trigger service by it's name."""
        try:
            return self._services[name]
        except KeyError:
            raise RookServiceMissing(name)

    def remove_aug(self, aug_id):
        """Remove an Aug from all services by it's id."""
        for service in itervalues(self._services):
            try:
                service.remove_aug(aug_id)
            except:
                logger.exception("Error when removing aug")

    def clear_augs(self):
        """Remove all Augs from all services."""

        for service in itervalues(self._services):
            service.clear_augs()

    def start(self):
        self._load_services()

    def close(self):
        for service in itervalues(self._services):
            service.close()

        self._services = {}

    def _load_services(self):
        try:
            self._services[BdbLocationService.NAME] = BdbLocationService()
            self._services[ImportService.NAME] = ImportService(self._services[BdbLocationService.NAME])
        except:
            logger.exception("Error starting location based services")

        try:
            self._services[LoggingLocationService.NAME] = LoggingLocationService()
        except:
            logger.exception("Error starting log handler services")

        try:
            self._services[HttpServerService.NAME] = HttpServerService()
        except:
            logger.exception("Error starting http server services")
