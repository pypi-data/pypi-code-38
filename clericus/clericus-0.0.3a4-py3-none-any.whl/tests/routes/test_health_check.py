import unittest
from aiohttp.test_utils import unittest_run_loop
from ..test_case import ClericusTestCase

import faker
fake = faker.Faker()


class HealthCheckTestCase(ClericusTestCase):
    @unittest_run_loop
    async def testHealthCheck(self):
        resp = await self.client.request("GET", "/healthy/")
        self.assertEqual(resp.status, 200)
        data = await resp.json()

        self.assertEqual(data["healthy"], True)