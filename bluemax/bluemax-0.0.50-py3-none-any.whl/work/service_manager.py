"""
    A service is a task that runs in the background.
    It can be started and stopped.
"""
import asyncio
import importlib
import logging

LOGGER = logging.getLogger(__name__)


class ServiceManager:
    """ This service manager only support async functions """

    def __init__(self, services):
        self._services = {srv.__name__: srv for srv in self._discover_(services)}
        self._tasks = {}
        LOGGER.debug("services %s", self.available_services)
        asyncio.ensure_future(self._run_all_())

    @classmethod
    def _discover_(cls, services):
        """ utility to discover public functions in a module """
        for name in dir(services):
            if name[0] == "_":
                continue
            service = getattr(services, name)
            if callable(service):
                yield service

    @property
    def available_services(self):
        """ names of available services """
        return [name for name in self._services]

    async def run_service(self, name: str):
        """ create a task of a function """
        if name not in self._tasks:
            LOGGER.info("running service %s", name)
            task = asyncio.ensure_future(self._services[name]())
            self._tasks[name] = task

    async def stop_service(self, name: str):
        """ stop a task """
        if name in self._tasks:
            LOGGER.info("stopping service %s", name)
            task = self._tasks[name]
            task.cancel()
            del self._tasks[name]

    async def _run_all_(self):
        """ helper to run all """
        for name in self.available_services:
            await self.run_service(name)

    async def _stop_all_(self):
        """ helper to shut down """
        for name in self._tasks:
            await self.stop_service(name)

    @classmethod
    def run(cls, services: str):
        services_package = importlib.import_module(services)
        manager = cls(services_package)
        LOGGER.info("services: %s", manager.available_services)
        loop = asyncio.get_event_loop()
        try:
            loop.run_forever()
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
