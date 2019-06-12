import time
import json
import unittest

from inmation_api_client.model import ItemValue
from .base import TestBase


class TestWrite(TestBase):
    def setUp(self):
        self.item_name = 'WriteItem'
        self.item = self.path + '/' + self.item_name
        self.client.Mass([{
            'path': self.item,
            'operation': 'UPSERT',
            'class': 'HolderItem',
            'ObjectName': self.item_name
        }])

    def test_can_write_int(self):
        val = 123
        res = self.client.Write(
            ItemValue(self.item, val)
        )
        time.sleep(0.3)
        self.assertEqual(res['code'], 200)
        self.assertEqual(res['data'][0]['v'], val)

    def test_can_write_string(self):
        val = 'test'
        res = self.client.Write(
            ItemValue(self.item, val)
        )
        time.sleep(0.3)
        self.assertEqual(res['code'], 200)
        self.assertEqual(res['data'][0]['v'], val)

    def test_can_write_array(self):
        val = [1, 2, 3]
        res = self.client.Write(
            ItemValue(self.item, val)
        )
        time.sleep(0.3)
        self.assertEqual(res['code'], 200)
        self.assertEqual(res['data'][0]['v'], val)

    def test_can_write_async(self):
        val = [1, 2, 3]
        res = self.run_coro(self.client.WriteAsync(
            ItemValue(self.item, val)
        ))
        time.sleep(0.3)
        self.assertEqual(res['code'], 200)
        self.assertEqual(res['data'][0]['v'], val)
