import unittest

from rebotics_sdk.providers.dataset import DatasetProvider


class RetailerProviderTestCase(unittest.TestCase):
    def setUp(self):
        self.dp = DatasetProvider('http://alpha.rebotics.net/')

    def test_api_root(self):
        res = self.dp.api_root()
        assert isinstance(res, dict)
