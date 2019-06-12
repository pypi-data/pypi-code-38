import unittest
from datetime import datetime, timedelta

from inmation_api_client.model import HistoricalDataItem
from .base import TestBase


class TestReadHistoricalData(TestBase):
    def setUp(self):
        self.items = [HistoricalDataItem(self.HolderItems[0], 'AGG_TYPE_AVERAGE')]
        date_format = '%Y-%m-%dT%H:%M:%S.000Z'
        now = datetime.now()
        now_minus_month = now + timedelta(-30)

        self.start_time = now_minus_month.strftime(date_format)
        self.end_time = now.strftime(date_format)

    def test_can_read_historical_data(self):
        res = self.client.ReadHistoricalData(self.items, self.start_time, self.end_time, 1)
        self.assertIn('items', res['data'].keys())
        self.assertEqual(res['code'], 200)

    def test_can_read_historical_data_async(self):
        res = self.run_coro(self.client.ReadHistoricalDataAsync(self.items, self.start_time, self.end_time, 1))
        self.assertEqual(res['code'], 200)
        self.assertIn('items', res['data'].keys())
