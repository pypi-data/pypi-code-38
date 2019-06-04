from ... import main
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        self.eazy = main.EazySDK().patch

    def test_payment_patch_valid_patch(self):
        req = self.eazy.payment(
            '2b62a358-9a1a-4c71-9450-e419e393dcd1',
            'a75f9829-2753-4f67-aafb-bb24aba27dd1', 10.00, '2019-07-15',
            'test comment'
        )
        self.assertIn('"Payment updated', req)

