import unittest

from rebotics_sdk.providers.retailer import RetailerProvider


class RetailerProviderTestCase(unittest.TestCase):
    def setUp(self):
        self.rp = RetailerProvider('http://alpha.rebotics.net/')

    def test_version(self):
        res = self.rp.version()
        print(res)

    def test_api_v4_root(self):
        res = self.rp.api_v4_root()
        print(res)
