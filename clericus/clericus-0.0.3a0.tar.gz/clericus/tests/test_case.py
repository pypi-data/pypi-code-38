import sys
sys.path.append(".")

from .. import Clericus
from ..config import defaultSettings, connectToDB

import unittest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

import json

from ..schemas import createCollections


class ClericusTestCase(AioHTTPTestCase):
    async def tearDownAsync(self):
        await self.db.client.drop_database(self.db.name)

    async def get_application(self):
        settings = defaultSettings()
        settings["db"]["name"] = f"test{type(self).__name__}"
        settings = connectToDB(settings)
        await settings["db"].client.drop_database(settings["db"].name)
        self._settings = settings
        self.db = settings["db"]
        await createCollections(self.db)
        return Clericus(self._settings)