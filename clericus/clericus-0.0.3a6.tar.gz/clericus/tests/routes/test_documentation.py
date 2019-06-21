import unittest
import asyncio
import json
from aiohttp.test_utils import make_mocked_request

from ...handler import newMethod, Endpoint
from ...parsing.fields import BoolField, StringField

from ..test_case import ClericusTestCase, unittest_run_loop


def async_test(f):
    def wrapper(self):
        return asyncio.run(f(self))

    return wrapper


class TestDocumentation(ClericusTestCase):
    async def get_application(self):
        app = await super().get_application()

        async def process(self, exampleValue):
            return {"result": exampleValue + " cow"}

        getMethod = newMethod(
            httpMethod="Get",
            description="This is a test handler",
            process=process,
            urlParameters={
                "exampleValue": StringField(
                    description="A string to modify",
                ),
            },
            responseFields={
                "result": StringField(
                    description="The value with \"cow\" appended",
                ),
            },
        )

        class end(Endpoint):
            """
            An example endpoint.
            """
            Get = getMethod

        app.addEndpoint(
            "/stuff/{exampleValue}/",
            end,
            name="Example Endpoint",
        )
        return app

    @unittest_run_loop
    async def testBaseDocumentation(self):
        resp = await self.client.request("GET", "/")
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        endpoints = data["endpoints"]
        self.assertGreater(len(endpoints), 1)

        data = next(
            filter(lambda k: k["path"] == "/stuff/{exampleValue}/", endpoints)
        )
        self.assertEqual(data["description"], "An example endpoint.")
        self.assertEqual(data["name"], "Example Endpoint")
        self.assertEqual(data["path"], "/stuff/{exampleValue}/")
        self.assertEqual(
            data["methods"]["get"]["description"],
            "This is a test handler",
        )

        self.assertEqual(
            data["methods"]["get"]["request"]["url"]["exampleValue"]
            ["description"],
            "A string to modify",
        )

    @unittest_run_loop
    async def testEndpointDocumentation(self):
        resp = await self.client.request("GET", "/documentation/stuff/moo/")
        self.assertEqual(resp.status, 200)
        data = await resp.json()

        self.assertEqual(data["description"], "An example endpoint.")
        self.assertEqual(data["name"], "Example Endpoint")
        self.assertEqual(data["path"], "/stuff/{exampleValue}/")
        self.assertEqual(
            data["methods"]["get"]["description"],
            "This is a test handler",
        )

        self.assertEqual(
            data["methods"]["get"]["request"]["url"]["exampleValue"]
            ["description"],
            "A string to modify",
        )
