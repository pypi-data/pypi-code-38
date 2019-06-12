import json
import unittest

from inmation_api_client.model import ItemValue
from .base import TestBase


class TestWrite(TestBase):
    def setUp(self):
        pass

    def get_item(self, value):
        return ItemValue(self.HolderItems[0], value)

    def test_can_write_int(self):
        val = 123
        res = self.client.Write(self.get_item(val))
        self.assertEqual(res['code'], 200)
        self.assertEqual(res['data'][0]['v'], val)

    def test_can_write_string(self):
        val = 'test'
        res = self.client.Write(self.get_item(val))
        self.assertEqual(res['code'], 200)
        self.assertEqual(res['data'][0]['v'], val)

    def test_can_write_array(self):
        val = [1, 2, 3]
        res = self.client.Write(self.get_item(val))
        self.assertEqual(res['code'], 200)
        self.assertEqual(res['data'][0]['v'], val)

    def test_can_write_async(self):
        val = [1, 2, 3]
        item = ItemValue(self.HolderItems[0], val)
        res = self.run_coro(self.client.WriteAsync(item))
        self.assertEqual(res['code'], 200)
        self.assertEqual(res['data'][0]['v'], val)
