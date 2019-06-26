from typing import List, Dict, ClassVar
import logging
import asyncio

from macrobase.config import AppConfig, SimpleAppConfig
from macrobase.pool import DriversProccesesPool
# from macrobase.context import context

from macrobase.logging import get_logging_config
from macrobase_driver import MacrobaseDriver
from macrobase_driver.hook import HookNames

from structlog import get_logger

log = get_logger('macrobase')


class Application:

    def __init__(self, loop: asyncio.AbstractEventLoop, name: str = None):
        """Create Application object.

        :param loop: asyncio compatible event loop
        :param name: string for naming drivers
        :return: Nothing
        """
        self.name = name
        self.loop = loop
        self.config = AppConfig()
        self._pool = DriversProccesesPool()
        self._drivers: List[MacrobaseDriver] = []

    def add_config(self, config: SimpleAppConfig):
        self.config.update(config)

    def get_driver(self, driver_obj: ClassVar[MacrobaseDriver], *args, **kwargs) -> MacrobaseDriver:
        driver = driver_obj(*args, **kwargs)
        driver.update_config(self.config)

        return driver

    def add_driver(self, driver: MacrobaseDriver):
        self._drivers.append(driver)

    def add_drivers(self, drivers: List[MacrobaseDriver]):
        self._drivers.extend(drivers)

    async def _apply_logging(self):
        self._logging_config = get_logging_config(self.config)
        logging.config.dictConfig(self._logging_config)

    async def _prepare(self):
        await self._apply_logging()

    async def run(self):
        await self._prepare()

        self._pool.start(self._drivers)
