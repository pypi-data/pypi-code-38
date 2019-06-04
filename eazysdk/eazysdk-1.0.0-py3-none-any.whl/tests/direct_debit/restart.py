from ... import main
from ...exceptions import ResourceNotFoundError
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        self.eazy = main.EazySDK().post

    def test_restart_contract(self):
        req = self.eazy.restart_contract(
            'a899ced6-a601-4146-92f7-5c8ee40bbf93', 'Until further notice',
            'Switch to further notice', payment_day_in_month=15,
            payment_month_in_year=6
        )
        self.assertIn('Contract restarted', req)

    def test_restart_contract_contract_not_expired_returns_error(self):
        req = self.eazy.restart_contract(
            'a899ced6-a601-4146-92f7-5c8ee40bbf93', 'Until further notice',
            'Switch to further notice', payment_day_in_month=15,
            payment_month_in_year=6
        )
        self.assertIn('is not expired, no action has been taken', req)

    def test_archive_contract_incorrect_contract_returns_error(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.restart_contract(
                '99ced6-a601-4146-92f7-5c8ee40bbf93', 'Until further notice',
                'Switch to further notice', payment_day_in_month=15,
                payment_month_in_year=6
            )
        self.assertIn('resource could not be found', str(e.exception))