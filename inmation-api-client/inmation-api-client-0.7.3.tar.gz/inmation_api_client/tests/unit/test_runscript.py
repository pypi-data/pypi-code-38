import unittest

from inmation_api_client.model import Item
from .base import TestBase


class TestRunScript(TestBase):
    def setUp(self):
        self.context = Item('/System')
        self.script = "return 2 + 3"

    def test_can_run_a_script(self):
        res = self.client.RunScript(self.context, self.script)
        self.assertEqual(res['code'], 200)
        self.assertEqual(res['data'][0]['v'], 5)

    def test_can_run_a_script_async(self):
        res = self.client.RunScript(self.context, self.script)
        self.assertEqual(res['code'], 200)
        self.assertEqual(res['data'][0]['v'], 5)
