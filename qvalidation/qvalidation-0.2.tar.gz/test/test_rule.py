import unittest
from qvalidation import  Validation, rule


class TestRule(unittest.TestCase):

    def setUp(self):
        data = dict(field1='ok', field2=None, field3='', field4=[], field5={}, field6=False)
        self.v = Validation(data)

    def test_required(self):
        for i in range(1,7):
            with self.subTest():
                self.v.set_rule(field='field%s' % i, rule=rule.required, message='{field}')

        with self.subTest():
            self.assertFalse(self.v.is_valid(True))

        with self.subTest():
            self.assertDictEqual(self.v.errors(), dict(field2='field2', field3='field3', field4='field4', field5='field5'))


    def test_number(self):
        self.skipTest('TODO: test number')

    def test_date(self):
        self.skipTest('TODO: test date')

    def test_match(self):
        self.skipTest('TODO: test match')

    def test_email(self):
        self.skipTest('TODO: test match')

    def test_contains(self):
        self.skipTest('TODO: test contains')

    def test_only(self):
        self.skipTest('TODO: test only')

    def test_greater(self):
        self.skipTest('TODO: test greater')

    def test_greater_then(self):
        self.skipTest('TODO: test greater_then')

    def test_less(self):
        self.skipTest('TODO: test less')

    def test_less_then(self):
        self.skipTest('TODO: test less_then')

    def test_between(self):
        self.skipTest('TODO: test between')

    def test_email(self):
        self.skipTest('TODO: test email')

    def test_to_date_format(self):
        self.skipTest('TODO: test to date format')

    def test_to_decimal(self):
        self.skipTest('TODO: test to decimal')

