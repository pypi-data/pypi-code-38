import unittest
from datetime import datetime, timedelta

from inmation_api_client.model import Item, RawHistoricalDataQuery
from .base import TestBase


class TestReadRawHistoricalData(TestBase):
    def setUp(self):
        date_format = '%Y-%m-%dT%H:%M:%S.000Z'
        now = datetime.now()

        self.start_time = (now + timedelta(-30)).strftime(date_format)
        self.end_time = now.strftime(date_format)
        self.items = [Item(self.HolderItems[0])]
        self.queries = [
            RawHistoricalDataQuery(self.items, self.start_time, self.end_time)
        ]

    def test_can_read_raw_historical_data(self):
        res = self.client.ReadRawHistoricalData(self.queries)
        if res and 'error' in res.keys():
            print(res)
        self.assertIn('historical_data', res['data'].keys())
        self.assertEqual(res['code'], 200)

    def test_can_read_raw_historical_data_async(self):
        res = self.run_coro(
            self.client.ReadRawHistoricalDataAsync(self.queries))

        self.assertEqual(res['code'], 200)
        self.assertIn('historical_data', res['data'].keys())
