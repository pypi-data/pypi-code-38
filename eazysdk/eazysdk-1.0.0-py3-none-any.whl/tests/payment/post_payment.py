from ... import main
from ...settings import Settings as s
from ...exceptions import InvalidParameterError
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        self.eazy = main.EazySDK().post

    def test_post_payment_all_valid_details(self):
        req = self.eazy.payment(
            '1802e1dd-a657-428c-b8d0-ba162fc76203', 10.00, '2019-07-15',
            'test comment', False
        )
        self.assertIn('"Error":null', req)

    def test_auto_fix_payment_date(self):
        s.payments['auto_fix_payment_date'] = True
        req = self.eazy.payment(
            '2b62a358-9a1a-4c71-9450-e419e393dcd1', 10.00, '2018-07-15',
            'test comment', False
        )
        self.assertIn('"Error":null', req)

    def test_post_payment_accepts_no_comment(self):
        req = self.eazy.payment(
            '2b62a358-9a1a-4c71-9450-e419e393dcd1', 10.00, '2019-07-15',
            '', False
        )
        self.assertIn('"Error":null', req)

    def test_post_payment_invalid_contract_throws_error(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.payment(
                '1b62a358-9a1a-4c71-9450-e419e393dcd1', 10.00, '2019-07-15',
                '', False
            )
        self.assertIn(
            'The specified contract GUID does not relate', str(e.exception)
        )

    def test_post_payment_non_positive_amount_throws_error(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.payment(
                '1b62a358-9a1a-4c71-9450-e419e393dcd1', 0, '2019-07-15',
                '', False
            )
        self.assertIn(
            'collection_amount must be a number', str(e.exception)
        )

    def test_post_payment_invalid_date_throws_error(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.payment(
                '1b62a358-9a1a-4c71-9450-e419e393dcd1', 1.0, '2018-07-15',
                '', False
            )
        self.assertIn(
            '2018-07-15 is not a valid start date.', str(e.exception)
        )
