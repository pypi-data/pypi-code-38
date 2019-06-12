import unittest

from inmation_api_client.model import Item
from .base import TestBase


class TestRead(TestBase):
    def setUp(self):
        self.items = [Item(i) for i in self.HolderItems]

    def test_can_read(self):
        res = self.client.Read(self.items)
        self.assertEqual(res['code'], 200)
        self.assertIn('v', res['data'][0].keys())
        self.assertEqual(len(res['data']), len(self.items))

    def test_can_read_async(self):
        res = self.run_coro(self.client.ReadAsync(self.items))
        self.assertEqual(res['code'], 200)
        self.assertIn('v', res['data'][0].keys())
        self.assertEqual(len(res['data']), len(self.items))
