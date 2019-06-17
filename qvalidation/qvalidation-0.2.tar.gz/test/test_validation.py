import unittest
from collections import OrderedDict
from qvalidation.validation import *


class TestValidation(unittest.TestCase):

    def setUp(self):
        self.data = {'firstname': 'John', 'lastname': 'Doe', 'age': 19}
        self.v = Validation(self.data)

    def test_constructor_data(self):
        v = Validation(data=self.data)
        self.assertDictEqual(self.data, v._data)

    def test_set_data(self):
        v = Validation()
        instance = v.set_data(self.data)
        self.assertIsInstance(instance, Validation)
        self.assertDictEqual(self.data, v._data)

    def test_set_rule(self):
        rule = dict(field='age', label='Age', rule='required', message='')
        instance = self.v.set_rule(**rule)
        self.assertIsInstance(instance, Validation)
        self.assertEqual(1, len(self.v._rules))
        self.assertEqual(rule['field'], self.v._rules[0].field)
        self.assertEqual(rule['label'], self.v._rules[0].label)
        self.assertEqual(rule['rule'], self.v._rules[0].rule)
        self.assertEqual(rule['message'], self.v._rules[0].message)


    def test_function_rule(self):
        def fn(field, label, data, **kwargs):
            return False

        rule = dict(field='age', label='Age', rule=fn, message='{value} is invalid for {label}')
        self.v.set_rule(**rule)
        self.assertDictEqual(self.v.errors(True), {'age':'19 is invalid for Age'})


    def test_lambda_rule(self):
        self.v.set_rule(field='firstname', label='First Name', rule=lambda value, label, field, data, args, message: False, message='{label} is invalid')
        self.assertDictEqual(self.v.errors(True), {'firstname': 'First Name is invalid'})


    def test_valid_rule(self):
        self.v.set_rule(field='firstname', label='First Name', rule=lambda data, field, label, **kwargs: True, message='{label} is invalid')
        self.assertDictEqual(self.v.errors(True), {})


    def test_template_variables(self):
        self.v.set_rule(field='firstname', label='Name', rule=lambda **kwargs: False, args='rule_args', message='{field},{label},{value},{args}')
        self.assertDictEqual(self.v.errors(
            True), {'firstname': 'firstname,Name,John,rule_args'})

    def test_data_key_as_template(self):
        self.v.set_rule(field='firstname', label='First Name', rule=lambda **kwargs: False, message='{firstname} {lastname} {notfound} is invalid')
        self.assertDictEqual(self.v.errors(True), {'firstname': 'John Doe  is invalid'})


    def test_sanitize_data(self):
        def sanitize(data, **kwargs):
            data['firstname'] = 'Snow'
            return True
        self.v.set_rule(field='age', label='Age', rule=sanitize, message='{firstname}')
        self.assertEqual(self.v.data(True)['firstname'], 'Snow')
        self.assertEqual(self.v._data['firstname'], 'John')


    def test_function_params(self):
        def between(field, data, **kwargs):
            a, b = kwargs['args']
            return a <= data[field] <= b
        self.v.set_rule(field='age', label='Age', rule=between, args=[15,20], message='{firstname}')
        self.assertEqual(self.v.errors(True), {})


    def test_return_message_by_rule(self):
        def greater(field, data, **kwargs):
            return (data[field] > kwargs['args'], 'Must be greater then {args}')
        self.v.set_rule(field='age', label='Age', rule=greater,args=20)
        self.assertEqual(self.v.errors(True), {'age': 'Must be greater then 20'})


    def test_return_rule_tuple(self):
        """Wehn tuple does not have 2 positions"""
        def greater(field, data, **kwargs):
            return (data[field] > kwargs['args'],)
        self.v.set_rule(field='age', label='Age', rule=greater,args=20, message='tuple len 1')
        self.assertEqual(self.v.errors(True), {'age': 'tuple len 1'})

    def test_priority_message(self):
        def greater(field, data, **kwargs):
            return (data[field] > kwargs['args'], 'Must be greater then {args}')
        self.v.set_rule(field='age', label='Age', rule=greater, args=20, message='show message')
        self.assertEqual(self.v.errors(True), {'age': 'show message'})


    def test_is_valid(self):
        self.v.set_rule(field='age', label='Age', rule=lambda **kwargs: False, message='')
        self.assertFalse(self.v.is_valid(True))
        self.v.set_rule(field='age', label='Age', rule=lambda **kwargs: True, message='')
        self.assertFalse(self.v.is_valid())

    def test_is_invalid(self):
        self.v.set_rule(field='age', label='Age', rule=lambda **kwargs: False, message='')
        self.assertTrue(self.v.is_invalid(True))
        self.v.set_rule(field='age', label='Age', rule=lambda **kwargs: True, message='')
        self.assertTrue(self.v.is_invalid())


    def test_run_returning(self):
        self.v.set_rule(field='age', label='Age', rule=lambda **kwargs: False, message='')
        self.assertEqual(self.v.run(), False)


    def test_default_label(self):
        self.v.set_rule(field='age', rule=lambda **kwargs: False, message='{label}')
        self.assertEqual(self.v.errors(True)['age'], 'age')


    def test_rule_value_in_params(self):
        self.v.set_rule(field='age', rule=lambda value, **kwargs: value > 30, message='{label}')
        self.assertEqual(self.v.errors(True)['age'], 'age')


    def test_real_use_case(self):
        userdata = dict(product='notebook  dell@#$', price='5.65', stock=0)
        sanit_data = dict(product='notebook dell', price='5.65', stock=0)
        error_data = dict(stock='sorry! Then product notebook dell was unavailable')

        def sanitize(field, data, **kwargs):
            data[field] = data[field].replace('@#$', '').replace('  ', ' ').strip()
            return True

        def is_available(field, data, **kwargs):
            return data[field] > 0

        v = Validation(userdata)
        v.set_rule(field='product', label='Product', rule=sanitize)
        v.set_rule(field='stock', label='Disponibility', rule=is_available, message='sorry! Then product {product} was unavailable')

        self.assertDictEqual(v.errors(True), error_data)
        self.assertDictEqual(v.data(), sanit_data)
        self.assertFalse(v.is_valid())
