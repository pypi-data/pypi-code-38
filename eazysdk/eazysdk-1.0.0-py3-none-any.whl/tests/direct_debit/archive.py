from ... import main
from ...exceptions import ResourceNotFoundError
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        self.eazy = main.EazySDK().post

    def test_archive_contract(self):
        req = self.eazy.archive_contract(
            'a899ced6-a601-4146-92f7-5c8ee40bbf93'
        )
        self.assertIn('has been archived', req)

    def test_archive_contract_already_archived(self):
        req = self.eazy.archive_contract(
            'a899ced6-a601-4146-92f7-5c8ee40bbf93'
        )
        self.assertIn('is already archived', req)

    def test_archive_contract_incorrect_contract_returns_error(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.cancel_direct_debit(
                '899ced6-a601-4146-92f7-5c8ee40bbf93'
            )
        self.assertIn('resource could not be found', str(e.exception))