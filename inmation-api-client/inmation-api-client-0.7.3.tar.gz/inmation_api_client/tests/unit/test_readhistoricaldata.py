import time
import unittest
from datetime import datetime, timedelta

from inmation_api_client.model import HistoricalDataItem, ItemValue
from .base import TestBase


class TestReadHistoricalData(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.item_name = 'ReadHistoricalDataItem'
        cls.item = cls.path + '/' + cls.item_name
        cls.items = [HistoricalDataItem(cls.item, 'AGG_TYPE_AVERAGE')]

        cls.client.Mass([{
            'path': cls.item,
            'operation': 'UPSERT',
            'class': 'HolderItem',
            'ObjectName': cls.item_name,
            'ArchiveOptions.StorageStrategy': True
        }])

        item_values = []
        for i in range(10):
            time.sleep(.05)
            item_values.append(ItemValue(cls.item, i))
        cls.client.Write(item_values)

    def setUp(self):
        date_format = '%Y-%m-%dT%H:%M:%S.000Z'
        now = datetime.now()
        now_minus_month = now + timedelta(-30)

        self.start_time = now_minus_month.strftime(date_format)
        self.end_time = now.strftime(date_format)

    def test_can_read_historical_data(self):
        time.sleep(.5)
        res = self.client.ReadHistoricalData(self.items, self.start_time, self.end_time, 1)
        self.assertEqual(res['code'], 200)
        self.assertEqual(sum(range(10)) / 10, res['data']['items'][0]['intervals'][0]['V'])

    def test_can_read_historical_data_async(self):
        res = self.run_coro(self.client.ReadHistoricalDataAsync(self.items, self.start_time, self.end_time, 1))
        self.assertEqual(res['code'], 200)
        self.assertEqual(sum(range(10)) / 10, res['data']['items'][0]['intervals'][0]['V'])
