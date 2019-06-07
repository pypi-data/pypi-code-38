# Copyright (c) 2019 Red Hat
# All Rights Reserved.
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


def condition(value):
    return value


class PositiveSkipMethodTest(unit.TobikoUnitTest):

    @tobiko.skip_if('condition value was true',
                    condition, True)
    def test_skip_if_condition_called_with_args(self):
        self.fail('Not skipped')

    @tobiko.skip_if('condition value was true',
                    condition, value=True)
    def test_skip_if_condition_called_with_kwargs(self):
        self.fail('Not skipped')

    @tobiko.skip_until('condition value was false',
                       condition, False)
    def test_skip_until_condition_called_with_args(self):
        self.fail('Not skipped')

    @tobiko.skip_until('condition value was false',
                       condition, value=False)
    def test_skip_until_condition_called_with_kwargs(self):
        self.fail('Not skipped')


class NegativeSkipBase(unit.TobikoUnitTest):
    test_method_called = False

    def setUp(self):
        super(NegativeSkipBase, self).setUp()
        self.addCleanup(self.assert_test_method_called)

    def assert_test_method_called(self):
        self.assertTrue(self.test_method_called)


class NegativeSkipMethodTest(NegativeSkipBase):

    @tobiko.skip_if('condition value was false',
                    condition, False)
    def test_skip_if_condition_called_with_args(self):
        self.test_method_called = True

    @tobiko.skip_if('condition value was false',
                    condition, value=False)
    def test_skip_if_condition_called_with_kwargs(self):
        self.test_method_called = True

    @tobiko.skip_until('condition value was true',
                       condition, True)
    def test_skip_until_condition_called_with_args(self):
        self.test_method_called = True

    @tobiko.skip_until('condition value was true',
                       condition, value=True)
    def test_skip_until_condition_called_with_kwargs(self):
        self.test_method_called = True


@tobiko.skip_if('condition value was true',
                condition, True)
class PositiveSkipIfConditionCalledWithArgsFixture(tobiko.SharedFixture):
    pass


@tobiko.skip_if('condition value was true',
                condition, value=True)
class PositiveSkipIfConditionCalledWithKwargsFixture(tobiko.SharedFixture):
    pass


@tobiko.skip_until('condition value was false',
                   condition, False)
class PositiveSkipUntilConditionCalledWithArgsFixture(tobiko.SharedFixture):
    pass


@tobiko.skip_until('condition value was false',
                   condition, value=False)
class PositiveSkipUntilConditionCalledWithKwargsFixture(tobiko.SharedFixture):
    pass


class PositiveSkipFixtureTest(unit.TobikoUnitTest):

    def test_skip_if_condition_called_with_args(self):
        ex = self.assertRaises(
            self.skipException, tobiko.setup_fixture,
            PositiveSkipIfConditionCalledWithArgsFixture)
        self.assertEqual('condition value was true', str(ex))

    def test_skip_if_condition_called_with_kwargs(self):
        ex = self.assertRaises(
            self.skipException, tobiko.setup_fixture,
            PositiveSkipIfConditionCalledWithKwargsFixture)
        self.assertEqual('condition value was true', str(ex))

    def test_skip_until_condition_called_with_args(self):
        ex = self.assertRaises(
            self.skipException, tobiko.setup_fixture,
            PositiveSkipUntilConditionCalledWithArgsFixture)
        self.assertEqual('condition value was false', str(ex))

    def test_skip_until_condition_called_with_kwargs(self):
        ex = self.assertRaises(
            self.skipException, tobiko.setup_fixture,
            PositiveSkipUntilConditionCalledWithKwargsFixture)
        self.assertEqual('condition value was false', str(ex))


@tobiko.skip_if('condition value was false',
                condition, False)
class NegativeSkipIfConditionCalledWithArgsFixture(tobiko.SharedFixture):
    pass


@tobiko.skip_if('condition value was false',
                condition, value=False)
class NegativeSkipIfConditionCalledWithKwargsFixture(tobiko.SharedFixture):
    pass


@tobiko.skip_until('condition value was true',
                   condition, True)
class NegativeSkipUntilConditionCalledWithArgsFixture(tobiko.SharedFixture):
    pass


@tobiko.skip_until('condition value was true',
                   condition, value=True)
class NegativeSkipUntilConditionCalledWithKwargsFixture(tobiko.SharedFixture):
    pass


class NegativeSkipFixtureTest(unit.TobikoUnitTest):

    def test_skip_if_condition_called_with_args(self):
        fixture = tobiko.setup_fixture(
            NegativeSkipIfConditionCalledWithArgsFixture)
        self.assertIsInstance(
            fixture, NegativeSkipIfConditionCalledWithArgsFixture)

    def test_skip_if_condition_called_with_kwargs(self):
        fixture = tobiko.setup_fixture(
            NegativeSkipIfConditionCalledWithKwargsFixture)
        self.assertIsInstance(
            fixture, NegativeSkipIfConditionCalledWithKwargsFixture)

    def test_skip_until_condition_called_with_args(self):
        fixture = tobiko.setup_fixture(
            NegativeSkipUntilConditionCalledWithArgsFixture)
        self.assertIsInstance(
            fixture, NegativeSkipUntilConditionCalledWithArgsFixture)

    def test_skip_until_condition_called_with_kwargs(self):
        fixture = tobiko.setup_fixture(
            NegativeSkipUntilConditionCalledWithKwargsFixture)
        self.assertIsInstance(
            fixture, NegativeSkipUntilConditionCalledWithKwargsFixture)


@tobiko.skip_if('condition value was true',
                condition, True)
class PositiveSkipIfConditionCalledWithArgsTest(unit.TobikoUnitTest):

    def test_fail(self):
        self.fail('Not skipped')


@tobiko.skip_if('condition value was true',
                condition, value=True)
class PositiveSkipIfConditionCalledWithKwargsTest(unit.TobikoUnitTest):

    def test_fail(self):
        self.fail('Not skipped')


@tobiko.skip_until('condition value was false',
                   condition, False)
class PositiveSkipUntilConditionCalledWithArgsTest(unit.TobikoUnitTest):

    def test_fail(self):
        self.fail('Not skipped')


@tobiko.skip_until('condition value was false',
                   condition, value=False)
class PositiveSkipUntilConditionCalledWithKwargsTest(unit.TobikoUnitTest):

    def test_fail(self):
        self.fail('Not skipped')


@tobiko.skip_if('condition value was true',
                condition, False)
class NegativeSkipIfConditionCalledWithArgsTest(NegativeSkipBase):

    def test_fail(self):
        self.test_method_called = True


@tobiko.skip_if('condition value was true',
                condition, value=False)
class NegativeSkipIfConditionCalledWithKwargsTest(NegativeSkipBase):

    def test_fail(self):
        self.test_method_called = True


@tobiko.skip_until('condition value was false',
                   condition, True)
class NegativeSkipUntilConditionCalledWithArgsTest(NegativeSkipBase):

    def test_fail(self):
        self.test_method_called = True


@tobiko.skip_until('condition value was false',
                   condition, value=True)
class NegativeSkipUntilConditionCalledWithKwargsTest(NegativeSkipBase):

    def test_fail(self):
        self.test_method_called = True
