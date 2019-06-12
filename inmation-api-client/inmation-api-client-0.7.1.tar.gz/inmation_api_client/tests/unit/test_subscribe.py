import asyncio
import unittest
from random import randint

from inmation_api_client.model import Item, ItemValue, SubscriptionType
from .base import TestBase

TEST_VALUE = randint(1, 1000)
VALUE = None


async def unsubscribe_from_data_changes(client, sItem):
    await asyncio.sleep(.1)
    await client.UnsubscribeAsync(Item(sItem), SubscriptionType.DataChanged)


class TestSubscribe(TestBase):
    def setUp(self):
        self.items = [Item(self.HolderItems[0])]
        self.subcriptionItem = self.HolderItems[1]

    def test_can_subscribe(self):
        def on_data_changed(*args):
            global VALUE
            items = args[1]
            if items and isinstance(items, list):
                VALUE = items[0]['v']

        self.client.OnDataChanged(on_data_changed)

        self.client.RunAsync([
            self.client.SubscribeAsync(Item(self.subcriptionItem), SubscriptionType.DataChanged),
            self.client.WriteAsync(ItemValue(self.subcriptionItem, TEST_VALUE)),
            unsubscribe_from_data_changes(self.client, self.subcriptionItem)
        ])
        self.assertEqual(VALUE, TEST_VALUE)
