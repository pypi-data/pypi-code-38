# Copyright 2019 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import tobiko
from tobiko.tests import unit


class SomeException(tobiko.TobikoException):
    message = "message formatted with {b} and {a}"


class TestException(unit.TobikoUnitTest):

    def test_init(self, message=None, **properties):
        ex = SomeException(message, **properties)
        expected_str = message or SomeException.message
        if properties:
            expected_str = expected_str.format(**properties)
        self.assertEqual(expected_str, str(ex))
        for k, v in properties.items():
            self.assertEqual(v, getattr(ex, k))

    def test_init_with_properties(self):
        self.test_init(a='a', b='b')

    def test_init_with_message(self):
        self.test_init('{other} message', other='another')

    def test_raise(self):
        def _raise_my_exception(**kwargs):
            raise SomeException(**kwargs)
        ex = self.assertRaises(SomeException, _raise_my_exception, b=1, a=2)
        self.assertEqual('message formatted with 1 and 2', str(ex))

    def test_repr(self):
        ex = SomeException('some reason')
        self.assertEqual("SomeException('some reason')", repr(ex))

    def test_get_invalid_property(self):
        ex = SomeException(a='1', b='2')

        def _get_invalid_property():
            return ex.invalid_attribute_name

        ex = self.assertRaises(AttributeError, _get_invalid_property)
        self.assertEqual(
            "SomeException('message formatted with 2 and 1') object has no "
            "attribute 'invalid_attribute_name'", str(ex))

    def test_docstring_example(self):

        class MyException(tobiko.TobikoException):
            message = "This exception occurred because of {reason}"

        try:
            raise MyException(reason="something went wrong")
        except MyException as ex:
            self.assertEqual(
                'This exception occurred because of something went wrong',
                str(ex))
            self.assertEqual('something went wrong', ex.reason)
