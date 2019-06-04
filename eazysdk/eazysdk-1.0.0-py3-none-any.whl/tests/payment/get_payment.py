from ... import main
from ...exceptions import ResourceNotFoundError
import unittest
from json import loads


class Test(unittest.TestCase):
    def setUp(self):
        self.eazy = main.EazySDK().get

    def test_payments_get_all_payments_for_a_contract(self):
        req = self.eazy.payments(
            '2b62a358-9a1a-4c71-9450-e419e393dcd1',
        )
        self.assertIn('be047ad1-e314-4980-9cf6-2bb1d324a41d', req)

    def test_payments_get_specific_number_of_payments_from_a_contract(self):
        req = self.eazy.payments(
            '2b62a358-9a1a-4c71-9450-e419e393dcd1', 2
        )
        r = loads(req)
        self.assertEqual(2, len(r['Payments']))
        self.assertIn('8e194a8e-1d0b-4ac1-bf28-404b1516760f', req)

    def test_payments_get_single_payment_from_guid(self):
        req = self.eazy.payments_single(
            '2b62a358-9a1a-4c71-9450-e419e393dcd1',
            'be047ad1-e314-4980-9cf6-2bb1d324a41d',
        )
        self.assertIn('"Amount":10.00,', req)

    def test_payments_get_all_payments_invalid_contract_throws_error(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.payments(
                'b62a358-9a1a-4c71-9450-e419e393dcd1',
            )
        self.assertIn('resource could not be found.', str(e.exception))

    def test_payments_single_payment_invalid_contract_throws_error(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.payments_single(
                'b62a358-9a1a-4c71-9450-e419e393dcd1',
                'be047ad1-e314-4980-9cf6-2bb1d324a41d',
            )
        self.assertIn('resource could not be found.', str(e.exception))

    def test_payments_single_payment_invalid_payment_throws_error(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.payments_single(
                '2b62a358-9a1a-4c71-9450-e419e393dcd1',
                'e047ad1-e314-4980-9cf6-2bb1d324a41d',
            )
        self.assertIn('resource could not be found.', str(e.exception))

    def test_get_all_payments_no_payments_returns_message(self):
        req = self.eazy.payments(
            'a4d77bc5-8480-4148-8838-1afd7f5bab6b',
        )
        self.assertIn('This contract does not own any payments.', req)
