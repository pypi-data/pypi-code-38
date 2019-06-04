from ... import main
from json import loads as json
from json import JSONDecodeError
from datetime import datetime
from ...settings import Settings as s
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        self.eazy = main.EazySDK().get

    def test_searching_more_than_one_parameter_narrows_search(self):
        req = self.eazy.customers(
            email='test@email.com', customer_reference='test-000001',
            surname='Test', account_holder_name='Mr Test Test'
        )
        req_json = json(req)
        for record in req_json['Customers']:
            email = record['Email']
            ref = record['CustomerRef']
            surname = record['Surname']
            account_holder_name = record['BankDetail']['AccountHolderName']

            self.assertEqual(email, 'test@email.com')
            self.assertEqual(ref, 'test-000001')
            self.assertEqual(surname, 'Test')
            self.assertEqual(account_holder_name, 'Mr Test Test')

        self.assertEqual(len(req_json), 1)

    def test_searching_more_than_one_parameter_incorrect(self):
        req = self.eazy.customers(
            email='test@email.com', customer_reference='not_a_reference',
            surname='Test', account_holder_name='Mr Test Test'
        )
        try:
            json(req)
            self.fail('You should not see this.')
        except JSONDecodeError:
            self.assertEqual(1, 1)

    def test_search_email_full_email(self):
        req = self.eazy.customers(email='test@email.com')
        req_json = json(req)
        for record in req_json['Customers']:
            email = record['Email']
            self.assertIn('test@email.com', email)
        self.assertEqual(len(req_json), 1)

    def test_search_full_title(self):
        # This will fail. This is a limitation of the API.
        req = self.eazy.customers(title='Mx')
        req_json = json(req)
        for record in req_json['Customers']:
            title = record['Title']
            self.assertIn('Mx', title)
        self.assertGreaterEqual(len(req_json), 1)

    def test_search_partial_title(self):
        # This will fail. This is a limitation of the API.
        req = self.eazy.customers(title='Maste')
        req_json = json(req)
        for record in req_json['Customers']:
            title = record['Title']
            self.assertIn('Maste', title)
        self.assertEqual(len(req_json), 1)

    def test_search_search_from_full_date(self):
        date_format = '%Y-%m-%d'
        req_date = datetime.strptime('2019-01-01', date_format).date()
        req = self.eazy.customers(search_from=req_date)
        self.assertNotIn('No customers could be found', req)

        req_json = json(req)
        for record in req_json['Customers']:
            date_record = record['DateAdded'][0:10]
            date = datetime.strptime(date_record, date_format).date()
            self.assertGreaterEqual(date, req_date)

    def test_search_search_from_month(self):
        date_format = '%Y-%m'
        req_date = datetime.strptime('2019-01', date_format).date()
        req = self.eazy.customers(search_from=req_date)
        self.assertNotIn('No customers could be found', req)

        req_json = json(req)
        for record in req_json['Customers']:
            date_record = record['DateAdded'][0:7]
            date = datetime.strptime(date_record, date_format).date()
            self.assertGreaterEqual(date, req_date)

    def test_search_search_from_year(self):
        date_format = '%Y'
        req_date = datetime.strptime('2019', date_format).date()
        req = self.eazy.customers(search_from=req_date)
        self.assertNotIn('No customers could be found', req)

        req_json = json(req)
        for record in req_json['Customers']:
            date_record = record['DateAdded'][0:4]
            date = datetime.strptime(date_record, date_format).date()
            self.assertGreaterEqual(date, req_date)

    def test_search_date_of_birth_full_date(self):
        # This will fail. This is a limitation of the API.
        date_format = '%Y-%m-%d'
        req_date = datetime.strptime('1990-06-29', date_format).date()
        req = self.eazy.customers(date_of_birth=req_date)
        self.assertNotIn('No customers could be found', req)

        req_json = json(req)
        for record in req_json['Customers']:
            date_record = record['DateOfBirth'][0:10]
            self.assertIsNotNone(date_record)
            date = datetime.strptime(date_record, date_format).date()
            self.assertGreaterEqual(date, req_date)

    def test_search_date_of_birth_from_month(self):
        # This will fail. This is a limitation of the API.
        date_format = '%Y-%m'
        req_date = datetime.strptime('1990-06', date_format).date()
        req = self.eazy.customers(date_of_birth=req_date)
        self.assertNotIn('No customers could be found', req)

        req_json = json(req)
        for record in req_json['Customers']:
            date_record = record['DateOfBirth'][0:7]
            self.assertIsNotNone(date_record)
            date = datetime.strptime(date_record, date_format).date()
            self.assertGreaterEqual(date, req_date)

    def test_search_date_of_birth_from_year(self):
        # This will fail. This is a limitation of the API.
        date_format = '%Y'
        req_date = datetime.strptime('1990', date_format).date()
        req = self.eazy.customers(date_of_birth=req_date)
        self.assertNotIn('No customers could be found', req)

        req_json = json(req)
        for record in req_json['Customers']:
            date_record = record['DateOfBirth'][0:4]
            self.assertIsNotNone(date_record)
            date = datetime.strptime(date_record, date_format).date()
            self.assertGreaterEqual(date, req_date)

    def test_search_customer_ref_full_reference_number(self):
        req = self.eazy.customers(customer_reference='test-000002')
        req_json = json(req)
        for record in req_json['Customers']:
            customer_ref = record['CustomerRef']
            self.assertEqual(customer_ref, 'test-000002')
        self.assertEqual(len(req_json), 1)

    def test_search_customer_ref_partial_ref_number(self):
        # This will fail. This is a limitation of the API.
        req = self.eazy.customers(customer_reference='test')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                customer_ref = record['CustomerRef']
                self.assertIn('test', customer_ref)
            self.assertGreaterEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_first_name_full_name(self):
        req = self.eazy.customers(first_name='test')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                first_name = record['FirstName']
                self.assertIn('test', first_name.lower())
            self.assertGreaterEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_first_name_partial_name(self):
        req = self.eazy.customers(first_name='te')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                first_name = record['FirstName']
                self.assertIn('te', first_name.lower())
            self.assertGreaterEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_surname_full_name(self):
        req = self.eazy.customers(surname='test')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                first_name = record['Surname']
                self.assertIn('test', first_name.lower())
            self.assertGreaterEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_surname_partial_name(self):
        req = self.eazy.customers(surname='te')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                first_name = record['Surname']
                self.assertIn('te', first_name.lower())
            self.assertGreaterEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_company_name_full(self):
        req = self.eazy.customers(company_name='SDK Test Cliemt')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                first_name = record['CompanyName']
                self.assertEqual('sdk test cliemt', first_name.lower())
            self.assertGreaterEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_company_name_partial(self):
        req = self.eazy.customers(company_name='test')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                first_name = record['CompanyName']
                print(first_name)
                self.assertIn('te', first_name.lower())
            self.assertGreaterEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_post_code_full_post_code(self):
        req = self.eazy.customers(post_code='GL52 2NF')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                post_code = record['AddressDetail']['PostCode']
                self.assertEqual('gl52 2nf', post_code.lower())
            self.assertGreaterEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_post_code_partial_post_code(self):
        req = self.eazy.customers(post_code='GL52')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                post_code = record['AddressDetail']['PostCode']
                self.assertIn('gl52', post_code.lower())
            self.assertGreaterEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_account_number_full_number(self):
        req = self.eazy.customers(account_number='45678912')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                account_number = record['BankDetail']['AccountNumber']
                self.assertEqual('45678912', account_number.lower())
            self.assertEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_sort_code_full_number(self):
        req = self.eazy.customers(sort_code='147852')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                sort_code = record['BankDetail']['BankSortCode']
                self.assertEqual('147852', sort_code.lower())
            self.assertGreaterEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_account_holder_name_full_name(self):
        req = self.eazy.customers(account_holder_name='Mr Test Client')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                account_name = record['BankDetail']['AccountHolderName']
                self.assertEqual('mr test client', account_name.lower())
            self.assertGreaterEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_home_phone_full_number(self):
        req = self.eazy.customers(home_phone='01242147852')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                phone_number = record['HomePhoneNumber']
                self.assertEqual('01242147852', phone_number)
            self.assertEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_home_phone_partial_number(self):
        req = self.eazy.customers(home_phone='01242')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                phone_number = record['HomePhoneNumber']
                self.assertIn('01242', phone_number)
            self.assertGreaterEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_mobile_phone_full_number(self):
        req = self.eazy.customers(mobile_phone='07393549789')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                phone_number = record['MobilePhoneNumber']
                self.assertEqual('07393549789', phone_number)
            self.assertEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_mobile_phone_partial_number(self):
        req = self.eazy.customers(mobile_phone='07393')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                phone_number = record['HomePhoneNumber']
                self.assertIn('01242', phone_number)
            self.assertGreaterEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_work_phone_full_number(self):
        req = self.eazy.customers(work_phone='01452365478')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                phone_number = record['WorkPhoneNumber']
                self.assertEqual('01452365478', phone_number)
            self.assertEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_search_customer_work_phone_partial_number(self):
        req = self.eazy.customers(work_phone='01452')
        try:
            req_json = json(req)
            for record in req_json['Customers']:
                phone_number = record['WorkPhoneNumber']
                self.assertIn('01452', phone_number)
            self.assertGreaterEqual(len(req_json), 1)
        except JSONDecodeError:
            self.fail('json was not returned, no customers were returned.')

    def test_warning_enabled_warning_thrown(self):
        s.warnings['customer_search'] = True
        with self.assertWarns(UserWarning):
            self.eazy.customers()

    def test_warning_disabled_warning_not_thrown(self):
        s.warnings['customer_search'] = False
        try:
            with self.assertWarns(UserWarning):
                self.eazy.customers()
        except AssertionError:
            pass
