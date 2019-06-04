from ... import main
from ...exceptions import ResourceNotFoundError
from ...exceptions import InvalidParameterError
import unittest
from random import randint


class Test(unittest.TestCase):
    def setUp(self):
        self.eazy = main.EazySDK().patch

    def test_change_contract_amount(self):
        x = randint(1, 1000)
        req = self.eazy.contract_amount(
            '1802e1dd-a657-428c-b8d0-ba162fc76203', x, 'Change contract amount'
            )
        self.assertIn('collection amount has been updated', req)

    def test_amount_cannot_be_empty(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract_amount(
                '1802e1dd-a657-428c-b8d0-ba162fc76203', '',
                'Change contract amount'
            )
        self.assertIn('amount cannot be empty', str(e.exception))

    def test_amount_must_contain_only_numbers(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract_amount(
                '1802e1dd-a657-428c-b8d0-ba162fc76203', 'twenty pounds',
                'Change contract amount'
            )
        self.assertIn(
            'amount must be a number', str(e.exception)
        )

    def test_amount_comment_cannot_be_blank(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract_amount(
                '1802e1dd-a657-428c-b8d0-ba162fc76203', '15.00',
                ''
            )
        self.assertIn(
            'comment cannot be empty', str(e.exception)
        )

    def test_amount_customer_cannot_be_blank(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract_amount(
                '', '15.00', 'Change contract amount'
            )
        self.assertIn(
            ' cannot be empty', str(e.exception)
        )

    def test_amount_invalid_customer_throws_error(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.contract_amount(
                '1802e1dd-a657-428c-b8d0-ba162fc76212', '15.00',
                'Change contract amount'
            )
        self.assertIn(
            'is not a contract belonging to this client', str(e.exception)
        )

    def test_change_collection_day_month(self):
        x = randint(1, 28)
        req = self.eazy.contract_date_monthly(
            '6dfb8179-2f7f-46cb-bc05-fe7f2d36bf36', x, 'New payment day',
            False,
            )
        self.assertIn(
            'Contract 6dfb8179-2f7f-46cb-bc05-fe7f2d36bf36 day updated to', req
        )

    def test_contract_cannot_be_empty_month(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract_date_monthly(
                '', '1', 'New payment day', False,
            )
        self.assertIn('cannot be empty', str(e.exception))

    def test_invalid_contract_throws_error_month(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.contract_date_monthly(
                '6dfb8179-2f7f-46cb-bc05-fe7f2d36bf23', '1', 'New payment day',
                False,
            )
        self.assertIn(
            'is not a contract belonging to this client.', str(e.exception)
        )

    def test_comment_cannot_be_empty_month(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract_date_monthly(
                '6dfb8179-2f7f-46cb-bc05-fe7f2d36bf36', '1', '', False,
            )
        self.assertIn('cannot be empty', str(e.exception))

    def test_patch_next_payment_cannot_be_blank_month(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract_date_monthly(
                '6dfb8179-2f7f-46cb-bc05-fe7f2d36bf36', '1', '', 'Comment',
            )
        self.assertIn('cannot be empty', str(e.exception))

    def test_next_payment_amount_if_amend_next_payment_month(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract_date_monthly(
                '6dfb8179-2f7f-46cb-bc05-fe7f2d36bf36', '1', True, 'Comment',
            )
        self.assertIn('cannot be empty if amend_next_payment is'
                      ' set to true.', str(e.exception))

    def test_change_collection_day_annual(self):
        x = randint(1, 28)
        y = randint(1, 12)
        req = self.eazy.contract_date_annually(
            '8998eab6-f4fe-43b8-b718-78b4520e5529', x, y, 'New payment day',
            False,
            )
        self.assertIn(
            'Contract 8998eab6-f4fe-43b8-b718-78b4520e5529 day updated to', req
        )

    def test_contract_cannot_be_empty_annual(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract_date_annually(
                '', 1, 1, 'New payment day', False,
            )
        self.assertIn('cannot be empty', str(e.exception))

    def test_invalid_contract_throws_error_annual(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.contract_date_annually(
                '8998eab6-f4fe-43b8-b718-78b4520e5512', 1, 1,
                'New payment day', False,
            )
        self.assertIn(
            'is not a contract belonging to this client.', str(e.exception)
        )

    def test_comment_cannot_be_empty_annual(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract_date_annually(
                '8998eab6-f4fe-43b8-b718-78b4520e5529', 1, 1,
                '', False,
            )
        self.assertIn(
            'cannot be empty.', str(e.exception)
        )

    def test_day_cannot_be_empty_annual(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract_date_annually(
                '8998eab6-f4fe-43b8-b718-78b4520e5529', '', 1,
                'Comment', False,
            )
        self.assertIn(
            'cannot be empty.', str(e.exception)
        )

    def test_month_cannot_be_empty_annual(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract_date_annually(
                '8998eab6-f4fe-43b8-b718-78b4520e5529', 1, '',
                'Comment', False,
            )
        self.assertIn(
            'cannot be empty.', str(e.exception)
        )

    def test_patch_next_payment_cannot_be_blank_annual(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract_date_monthly(
                '8998eab6-f4fe-43b8-b718-78b4520e5529', 1, '', 'Comment', '',
            )
        self.assertIn('cannot be empty', str(e.exception))

    def test_next_payment_amount_if_amend_next_payment_annual(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract_date_annually(
                '8998eab6-f4fe-43b8-b718-78b4520e5529', 1, 2,
                'New payment day', True,
            )
        self.assertIn('cannot be empty if amend_next_payment is'
                      ' set to true.', str(e.exception))
