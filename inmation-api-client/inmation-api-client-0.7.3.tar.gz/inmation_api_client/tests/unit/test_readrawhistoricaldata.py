import time
import unittest
from datetime import datetime, timedelta

from inmation_api_client.model import Item, ItemValue, RawHistoricalDataQuery
from .base import TestBase


class TestReadRawHistoricalData(TestBase):
    def setUp(self):
        self.item_name = 'ReadRawHistoricalDataItem'
        self.item = self.path + '/' + self.item_name

        date_format = '%Y-%m-%dT%H:%M:%S.000Z'
        now = datetime.now()

        self.start_time = (now + timedelta(-30)).strftime(date_format)
        self.end_time = now.strftime(date_format)
        self.items = [Item(self.item)]
        self.queries = [
            RawHistoricalDataQuery(self.items, self.start_time, self.end_time)
        ]

        self.client.Mass([{
            'path': self.item,
            'operation': 'UPSERT',
            'class': 'HolderItem',
            'ObjectName': self.item_name,
            'ArchiveOptions.StorageStrategy': True
        }])

        item_values = []
        for i in range(10):
            time.sleep(.05)
            item_values.append(ItemValue(self.item, i))
        self.client.Write(item_values)

    def test_can_read_raw_historical_data(self):
        time.sleep(.5)
        res = self.client.ReadRawHistoricalData(self.queries)
        if res and 'error' in res.keys():
            print(res)

        self.assertEqual(res['code'], 200)

        values = res['data']['historical_data']['query_data'][0]['items'][0]['v']
        self.assertEqual(set(list(range(10))).issubset(values), True)

    def test_can_read_raw_historical_data_async(self):
        res = self.run_coro(
            self.client.ReadRawHistoricalDataAsync(self.queries))

        self.assertEqual(res['code'], 200)

        values = res['data']['historical_data']['query_data'][0]['items'][0]['v']
        self.assertEqual(set(list(range(10))).issubset(values), True)
