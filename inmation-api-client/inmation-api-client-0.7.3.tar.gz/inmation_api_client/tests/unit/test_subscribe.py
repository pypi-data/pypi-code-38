import asyncio
import time
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
        self.item_name = 'SubscribeItem'
        self.item = self.path + '/' + self.item_name

        self.items = [Item(self.item)]

        self.client.Mass([{
            'path': self.item,
            'operation': 'UPSERT',
            'class': 'HolderItem',
            'ObjectName': self.item_name,
            'ArchiveOptions.StorageStrategy': True
        }])

    def test_can_subscribe(self):
        def on_data_changed(*args):
            global VALUE
            items = args[1]
            if items and isinstance(items, list):
                VALUE = items[0]['v']

        self.client.OnDataChanged(on_data_changed)

        self.client.RunAsync([
            self.client.SubscribeAsync(Item(self.item), SubscriptionType.DataChanged),
            self.client.WriteAsync(ItemValue(self.item, TEST_VALUE)),
            unsubscribe_from_data_changes(self.client, self.item)
        ])
        time.sleep(.5)
        self.assertEqual(VALUE, TEST_VALUE)
