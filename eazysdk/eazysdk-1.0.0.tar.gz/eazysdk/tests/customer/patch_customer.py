from ... import main
from ...exceptions import InvalidParameterError
from ...exceptions import SDKNotEnabledError
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        self.eazy = main.EazySDK().patch

    def test_updating_all_customer_details_returns_expected_response(self):
        r = self.eazy.customer(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'test@email.com', 'Mr',
            '1990-01-01', 'Test', 'Test', 'TestCom', '1 Test Road', 'GL52 2NF',
            '14785236', '456123', 'Mr Test Test', '01242694874', '07398745641',
            '0145213458', 'line 2', 'line 3', 'line 4', 'tt'
        )
        self.assertIn('updated successfully', r)

    def test_post_code_too_short_throws_error(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f', post_code='G'
            )

        self.assertIn(
            'is not formatted as a UK post code. Please check the post code'
            ' and re-submit.', str(e.exception)
        )

    def test_post_code_too_long_throws_error(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f', post_code='GL516NBB'
            )

        self.assertIn(
            'is not formatted as a UK post code. Please check the'
            ' post code and re-submit.', str(e.exception)
        )

    def test_post_code_must_contain_letters(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f', post_code='1234567'
            )

        self.assertIn(
            'is not formatted as a UK post code. Please check the'
            ' post code and re-submit.', str(e.exception)
        )

    def test_post_code_must_contain_numbers(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f', post_code='GLTQVMQ'
            )

        self.assertIn(
            'is not formatted as a UK post code. Please check the'
            ' post code and re-submit.', str(e.exception)
        )

    def test_email_must_contain_at_symbol(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f', email='testemail.com'
            )

        self.assertIn(
            'is not a valid email address. Please check the email address'
            ' and re-submit.', str(e.exception)
        )

    def test_email_must_contain_tld(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f', email='test@emailcom'
            )

        self.assertIn(
            'is not a valid email address. Please check the email address'
            ' and re-submit.', str(e.exception)
        )

    def test_email_cannot_contain_special_characters_in_domain(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f',
                email='test@e!m&a$il.com'
            )

        self.assertIn(
            'is not a valid email address. Please check the email address'
            ' and re-submit.', str(e.exception)
        )

    def test_account_number_must_not_contain_letters(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f',
                account_number='1478523a'
            )

        self.assertIn(
            'is not formatted as a UK bank account number. UK bank'
            ' account numbers are 8 digits long. Please check the bank'
            ' account number and re-submit.', str(e.exception)
        )

    def test_account_number_must_not_be_too_short(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f',
                account_number='147852'
            )

        self.assertIn(
            'is not formatted as a UK bank account number. UK bank'
            ' account numbers are 8 digits long. Please check the bank'
            ' account number and re-submit.', str(e.exception)
        )

    def test_account_number_must_not_be_too_long(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f',
                account_number='1478514717'
            )

        self.assertIn(
            'is not formatted as a UK bank account number. UK bank'
            ' account numbers are 8 digits long. Please check the bank'
            ' account number and re-submit.', str(e.exception)
        )

    def test_sort_code_must_not_contain_letters(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f', sort_code='14785a'
            )

        self.assertIn(
            'is not formatted as a UK sort code. UK sort codes are 6'
            ' digits long. Make sure to not include any hyphens. Please check'
            ' the sort code and re-submit.', str(e.exception)
        )

    def test_sort_code_must_not_be_too_short(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f', sort_code='14785')

        self.assertIn(
            'is not formatted as a UK sort code. UK sort codes are 6'
            ' digits long. Make sure to not include any hyphens. Please check'
            ' the sort code and re-submit.', str(e.exception)
        )

    def test_sort_code_must_not_be_too_long(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f', sort_code='1478521'
            )

        self.assertIn(
            'is not formatted as a UK sort code. UK sort codes are 6'
            ' digits long. Make sure to not include any hyphens. Please check'
            ' the sort code and re-submit.', str(e.exception)
        )

    def test_sort_code_must_not_contain_hyphens(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f',
                sort_code='14-78-52')

        self.assertIn(
            'is not formatted as a UK sort code. UK sort codes are 6'
            ' digits long. Make sure to not include any hyphens. Please check'
            ' the sort code and re-submit.', str(e.exception)
        )

    def test_account_holder_name_cannot_be_too_long(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f',
                account_holder_name='Mr Test Test Test Test Test'
            )

        self.assertIn(
            'is not formatted as an account holder name. Account holder names'
            ' must be between 3 and 18 characters, contain only capital'
            ' letters (A-7), ampersands (&), hyphens (-), forward slashes'
            ' (/), and spaces ( ).', str(e.exception)
        )

    def test_account_holder_name_cannot_be_too_short(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f',
                account_holder_name='Mr')

        self.assertIn(
            'is not formatted as an account holder name. Account holder names'
            ' must be between 3 and 18 characters, contain only capital'
            ' letters (A-7), ampersands (&), hyphens (-), forward slashes'
            ' (/), and spaces ( ).', str(e.exception)
        )

    def test_account_holder_name_cannot_contain_special_characters(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.customer(
                '310a826b-d095-48e7-a55a-19dba82c566f',
                account_holder_name='Mr !^&()$"!')

        self.assertIn(
            'is not formatted as an account holder name. Account holder names'
            ' must be between 3 and 18 characters, contain only capital'
            ' letters (A-7), ampersands (&), hyphens (-), forward slashes'
            ' (/), and spaces ( ).', str(e.exception)
        )

    def test_empty_customer_throws_error(self):
        with self.assertRaises(SDKNotEnabledError):
            self.eazy.customer('', email='test@email.com')

    def test_invalid_customer_guid_throws_error(self):
        with self.assertRaises(SDKNotEnabledError):
            self.eazy.customer(
                '310a826b-f195-48e7-a55a-19dba82c566f', email='test@email.com'
            )

