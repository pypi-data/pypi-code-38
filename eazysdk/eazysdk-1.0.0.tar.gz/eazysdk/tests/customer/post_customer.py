from ... import main
from json import loads as json
from ...exceptions import InvalidParameterError
from ...exceptions import RecordAlreadyExistsError
from random import getrandbits
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        self.eazy = main.EazySDK().post
        self.r = str(getrandbits(32))

    def test_post_customer_using_valid_data_returns_customer_json_object(self):
        req = self.eazy.customer(
            self.r+'@test.com', 'Mr', self.r, self.r, self.r, '1 Test Road',
            'GL52 2NF', '14785236', '456789', 'Mr Test Test'
        )
        req_json = json(req)
        self.assertIn('CustomerRef', req)
        self.assertIsNotNone(req_json)

    def test_customer_reference_must_be_unique(self):
        with self.assertRaises(RecordAlreadyExistsError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL516NB', '14785236', '147852', 'Mr Test Test')

        self.assertIn(
            'A customer with the given customer_reference already exists.'
            ' Please change the customer reference and'
            ' re-submit.', str(e.exception)
        )

    def test_customer_reference_cannot_be_empty(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', '', 'Test', 'Test',
                '1 Test Road', 'GL516NB', '14785236', '147852', 'Mr Test Test')

        self.assertIn(
            'cannot be empty.', str(e.exception)
        )

    def test_post_code_too_short_throws_error(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'G', '14785236', '147852', 'Mr Test Test')

        self.assertIn(
            'G is not formatted as a UK post code. Please check the post code'
            ' and re-submit.', str(e.exception)
        )

    def test_post_code_too_long_throws_error(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL516NBB', '14785236', '147852',
                'Mr Test Test')

        self.assertIn(
            'GL516NBB is not formatted as a UK post code. Please check the'
            ' post code and re-submit.', str(e.exception)
        )

    def test_post_code_must_contain_letters(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', '99501', '14785236', '147852',
                'Mr Test Test')

        self.assertIn(
            '99501 is not formatted as a UK post code. Please check the'
            ' post code and re-submit.', str(e.exception)
        )

    def test_post_code_must_contain_numbers(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GLQQIAN', '14785236', '147852',
                'Mr Test Test')

        self.assertIn(
            'GLQQIAN is not formatted as a UK post code. Please check the'
            ' post code and re-submit.', str(e.exception)
        )

    def test_post_code_cannot_be_empty(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', '', '14785236', '147852',
                'Mr Test Test')

        self.assertIn(
            'cannot be empty.', str(e.exception)
        )

    def test_email_must_contain_at_symbol(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'testemail.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '14785236', '147852',
                'Mr Test Test')

        self.assertIn(
            'is not a valid email address. Please check the email address'
            ' and re-submit.', str(e.exception)
        )

    def test_email_must_contain_tld(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@emailcom', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '14785236', '147852',
                'Mr Test Test')

        self.assertIn(
            'is not a valid email address. Please check the email address'
            ' and re-submit.', str(e.exception)
        )

    def test_email_cannot_contain_special_characters_in_domain(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@e!m&a$il.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '14785236', '147852',
                'Mr Test Test')

        self.assertIn(
            'is not a valid email address. Please check the email address'
            ' and re-submit.', str(e.exception)
        )

    def test_email_cannot_be_empty(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '14785236', '147852',
                'Mr Test Test')

        self.assertIn(
            'cannot be empty.', str(e.exception)
        )

    def test_account_number_must_not_contain_letters(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '1478523a', '147852',
                'Mr Test Test')

        self.assertIn(
            'is not formatted as a UK bank account number. UK bank'
            ' account numbers are 8 digits long. Please check the bank'
            ' account number and re-submit.', str(e.exception)
        )

    def test_account_number_must_not_be_too_short(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '14785', '147852',
                'Mr Test Test')

        self.assertIn(
            'is not formatted as a UK bank account number. UK bank'
            ' account numbers are 8 digits long. Please check the bank'
            ' account number and re-submit.', str(e.exception)
        )

    def test_account_number_must_not_be_too_long(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '1478514717', '147852',
                'Mr Test Test')

        self.assertIn(
            'is not formatted as a UK bank account number. UK bank'
            ' account numbers are 8 digits long. Please check the bank'
            ' account number and re-submit.', str(e.exception)
        )

    def test_account_number_must_not_be_empty(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '', '147852',
                'Mr Test Test')

        self.assertIn(
            'cannot be empty', str(e.exception)
        )

    def test_sort_code_must_not_contain_letters(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '14785231', '14785a',
                'Mr Test Test')

        self.assertIn(
            'is not formatted as a UK sort code. UK sort codes are 6'
            ' digits long. Make sure to not include any hyphens. Please check'
            ' the sort code and re-submit.', str(e.exception)
        )

    def test_sort_code_must_not_be_too_short(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '14785231', '14785',
                'Mr Test Test')

        self.assertIn(
            'is not formatted as a UK sort code. UK sort codes are 6'
            ' digits long. Make sure to not include any hyphens. Please check'
            ' the sort code and re-submit.', str(e.exception)
        )

    def test_sort_code_must_not_be_too_long(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '14785231', '1478521',
                'Mr Test Test')

        self.assertIn(
            'is not formatted as a UK sort code. UK sort codes are 6'
            ' digits long. Make sure to not include any hyphens. Please check'
            ' the sort code and re-submit.', str(e.exception)
        )

    def test_sort_code_must_not_contain_hyphens(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '14785231', '14-78-52',
                'Mr Test Test')

        self.assertIn(
            'is not formatted as a UK sort code. UK sort codes are 6'
            ' digits long. Make sure to not include any hyphens. Please check'
            ' the sort code and re-submit.', str(e.exception)
        )

    def test_sort_code_cannot_be_empty(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '14785231', '',
                'Mr Test Test')

        self.assertIn(
            'cannot be empty', str(e.exception)
        )

    def test_account_holder_name_cannot_be_too_long(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '14785231', '147852',
                'Mr Test Test Test Test Test')

        self.assertIn(
            'is not formatted as an account holder name. Account holder names'
            ' must be between 3 and 18 characters, contain only capital'
            ' letters (A-7), ampersands (&), hyphens (-), forward slashes'
            ' (/), and spaces ( ).', str(e.exception)
        )

    def test_account_holder_name_cannot_be_too_short(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '14785231', '147852',
                'Mr')

        self.assertIn(
            'is not formatted as an account holder name. Account holder names'
            ' must be between 3 and 18 characters, contain only capital'
            ' letters (A-7), ampersands (&), hyphens (-), forward slashes'
            ' (/), and spaces ( ).', str(e.exception)
        )

    def test_account_holder_name_cannot_contain_special_characters(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '14785231', '147852',
                'Mr !^&()$"!')

        self.assertIn(
            'is not formatted as an account holder name. Account holder names'
            ' must be between 3 and 18 characters, contain only capital'
            ' letters (A-7), ampersands (&), hyphens (-), forward slashes'
            ' (/), and spaces ( ).', str(e.exception)
        )

    def test_account_holder_name_cannot_be_empty(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                'test@email.com', 'Mr', 'test-000001', 'Test', 'Test',
                '1 Test Road', 'GL51 6NB', '14785231', '147852',
                '')

        self.assertIn(
            'cannot be empty', str(e.exception)
        )

    def test_parameter_not_allowed_error(self):
        with self.assertRaises(TypeError):
            self.eazy.customer(not_an_arg='test@email.com')

