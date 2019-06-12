import unittest

from inmation_api_client.model import Item, ItemValue
from .base import TestBase


class TestRead(TestBase):
    def setUp(self):
        self.item_name = 'ReadItem'
        self.item = self.path + '/' + self.item_name
        self.items = [Item(self.item)]
        self.client.Mass([{
            'path': self.item,
            'operation': 'UPSERT',
            'class': 'HolderItem',
            'ObjectName': self.item_name
        }])

    def test_can_read(self):
        self.client.Write(
            ItemValue(self.item, 234)
        )
        res = self.client.Read(self.items)
        self.assertEqual(res['code'], 200)
        self.assertIn('v', res['data'][0].keys())
        self.assertEqual(234, res['data'][0]['v'])
        self.assertEqual(len(res['data']), len(self.items))

    def test_can_read_async(self):
        self.client.Write(
            ItemValue(self.item, 432)
        )
        res = self.run_coro(self.client.ReadAsync(self.items))
        self.assertEqual(res['code'], 200)
        self.assertIn('v', res['data'][0].keys())
        self.assertEqual(432, res['data'][0]['v'])
        self.assertEqual(len(res['data']), len(self.items))
