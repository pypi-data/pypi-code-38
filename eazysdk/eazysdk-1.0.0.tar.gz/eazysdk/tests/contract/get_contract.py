from ... import main
from json import loads as json
from ...exceptions import SDKNotEnabledError
from ...exceptions import ResourceNotFoundError
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        self.eazy = main.EazySDK().get

    def test_searching_customer_with_contracts_returns_contracts(self):
        req = self.eazy.contracts('310a826b-d095-48e7-a55a-19dba82c566f')
        req_json = json(req)
        for record in req_json['Contracts']:
            id = record['Id']
            self.assertIsNotNone(id)
        self.assertGreaterEqual(len(req_json), 1)

    def test_searching_customer_with_no_contracts_returns_no_contracts(self):
        req = self.eazy.contracts('7c1a60c5-af12-4477-a10b-a61770e312a5')
        self.assertIn('does not own any contracts', req)

    def test_searching_invalid_customer_returns_error(self):
        with self.assertRaises(SDKNotEnabledError) as e:
            self.eazy.contracts('7c1a60c5-af12-4477-a10b-a61770e312b6')
        self.assertIn('This is a generic error.', str(e.exception))

    def test_blank_customer_returns_error(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.contracts('')
        self.assertIn('resource could not be found.', str(e.exception))
