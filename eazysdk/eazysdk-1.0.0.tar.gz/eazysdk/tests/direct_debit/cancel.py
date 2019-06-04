from ... import main
from ...exceptions import ResourceNotFoundError
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        self.eazy = main.EazySDK().post

    def test_cancel_direct_debit(self):
        req = self.eazy.cancel_direct_debit(
            'a899ced6-a601-4146-92f7-5c8ee40bbf93'
        )
        self.assertIn('Contract cancelled', req)

    def test_cancel_already_cancelled_returns_cancel_instruction(self):
        req = self.eazy.cancel_direct_debit(
            'a899ced6-a601-4146-92f7-5c8ee40bbf93'
        )
        self.assertIn('Contract cancelled', req)

    def test_cancel_direct_debit_invalid_contract_throws_error(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.cancel_direct_debit(
                '99ced6-a601-4146-92f7-5c8ee40bbf93'
            )
            self.assertIn('resource could not be found', str(e.exception))
