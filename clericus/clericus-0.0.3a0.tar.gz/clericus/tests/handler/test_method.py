import unittest
import asyncio
import json
from aiohttp.test_utils import make_mocked_request

from ...handler import newMethod
from ...parsing.fields import BoolField, StringField


def async_test(f):
    def wrapper(self):
        return asyncio.run(f(self))

    return wrapper


class TestMethods(unittest.TestCase):
    @async_test
    async def testMethodCreation(self):
        async def process(self):
            return {"ok": True, "text": "stuff"}

        method = newMethod(
            httpMethod="Get",
            description="This is a test handler",
            process=process,
            responseFields={
                "ok": BoolField(),
                "text": StringField(),
            },
        )

        req = make_mocked_request('GET', '/')

        resp = await method().handle(req)
        respBody = json.loads(resp.body)

        self.assertEqual(respBody["ok"], True)
        self.assertEqual(respBody["text"], "stuff")
