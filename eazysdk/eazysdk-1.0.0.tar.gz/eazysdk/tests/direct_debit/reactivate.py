from ... import main
from ...exceptions import ResourceNotFoundError
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        self.eazy = main.EazySDK().post

    def test_reactivate_contract(self):
        req = self.eazy.reactivate_direct_debit(
            '2b62a358-9a1a-4c71-9450-e419e393dcd1'
        )
        self.assertIn('Contract reactivated', req)

    def test_reactivate_contract_archived_contract_throws_error(self):
        req = self.eazy.archive_contract(
            'a899ced6-a601-4146-92f7-5c8ee40bbf93'
        )
        self.assertIn('is already archived', req)

    def test_reactivate_contract_non_existing_contract_throws_error(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.cancel_direct_debit(
                '99ced6-a601-4146-92f7-5c8ee40bbf93'
            )
        self.assertIn('resource could not be found', str(e.exception))