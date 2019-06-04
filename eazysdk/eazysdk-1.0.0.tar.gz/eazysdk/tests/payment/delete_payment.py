from ... import main
from ...exceptions import ResourceNotFoundError
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        self.eazy = main.EazySDK().delete

    def test_delete_payment(self):
        req = self.eazy.payment(
            '1802e1dd-a657-428c-b8d0-ba162fc76203',
            '26a77d64-f21d-43cc-9dc4-765d3a3fc6c1', 'Deleted',
        )
        self.assertIn('Payment deleted', req)

    def test_delete_payment_non_payment_throws_error(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.payment(
                '1802e1dd-a657-428c-b8d0-ba162fc76203',
                '26a77d64-f21d-43cc-9dc4-765d3a3fc6c1', 'Deleted',
            )
        self.assertIn('either doesn\'t exist', str(e.exception))

    def test_delete_payment_non_contract_throws_error(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.payment(
                '802e1dd-a657-428c-b8d0-ba162fc76203',
                '26a77d64-f21d-43cc-9dc4-765d3a3fc6c1', 'Deleted',
            )
        self.assertIn('resource could not be found', str(e.exception))
