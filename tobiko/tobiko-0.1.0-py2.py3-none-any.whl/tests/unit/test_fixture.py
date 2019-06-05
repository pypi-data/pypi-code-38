# Copyright 2018 Red Hat
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

import os
import sys

import fixtures
import mock
import testtools

import tobiko
from tobiko.tests import unit


def canonical_name(cls):
    return __name__ + '.' + cls.__name__


class MyBaseFixture(tobiko.SharedFixture):

    def __init__(self):
        super(MyBaseFixture, self).__init__()
        self.setup_fixture = mock.Mock(
            specs=tobiko.SharedFixture.setup_fixture)
        self.cleanup_fixture = mock.Mock(
            specs=tobiko.SharedFixture.cleanup_fixture)


class MySkyppingFixture(tobiko.SharedFixture):

    def setup_fixture(self):
        tobiko.skip('some-reason')

    def cleanup_fixture(self):
        tobiko.skip('some-reason')


class MyFixture(MyBaseFixture):
    pass


class GetFixtureTest(unit.TobikoUnitTest):

    def test_by_name(self):
        self._test_get_fixture(canonical_name(MyFixture))

    def test_by_type(self):
        self._test_get_fixture(MyFixture)

    def test_by_instance(self):
        self._test_get_fixture(MyFixture())

    def _test_get_fixture(self, obj):
        fixture = tobiko.get_fixture(obj)
        self.assertIsInstance(fixture, MyFixture)
        self.assertIs(fixture, tobiko.get_fixture(obj))
        if isinstance(obj, fixtures.Fixture):
            self.assertIs(obj, fixture)
        else:
            self.assertIs(fixture, tobiko.get_fixture(
                canonical_name(MyFixture)))
        fixture.setup_fixture.assert_not_called()
        fixture.cleanup_fixture.assert_not_called()


class GetFixtureNameTest(unit.TobikoUnitTest):

    def test_with_instance(self):
        fixture = MyFixture()
        result = tobiko.get_fixture_name(fixture)
        self.assertEqual(canonical_name(MyFixture), result)

    def test_with_other_type(self):
        obj = object()
        ex = self.assertRaises(TypeError, tobiko.get_fixture_name, obj)
        self.assertEqual('Object {obj!r} is not a fixture.'.format(obj=obj),
                         str(ex))


class GetFixtureClassTest(unit.TobikoUnitTest):

    def test_with_name(self):
        result = tobiko.get_fixture_class(canonical_name(MyFixture))
        self.assertIs(MyFixture, result)

    def test_with_type(self):
        result = tobiko.get_fixture_class(MyFixture)
        self.assertIs(MyFixture, result)

    def test_with_instance(self):
        result = tobiko.get_fixture_class(MyFixture())
        self.assertIs(MyFixture, result)


class GetFixtureDirTest(unit.TobikoUnitTest):

    expected_dir = os.path.dirname(__file__)

    def test_with_name(self):
        actual_dir = tobiko.get_fixture_dir(canonical_name(MyFixture))
        self.assertEqual(self.expected_dir, actual_dir)

    def test_with_type(self):
        actual_dir = tobiko.get_fixture_dir(MyFixture)
        self.assertEqual(self.expected_dir, actual_dir)

    def test_with_instance(self):
        actual_dir = tobiko.get_fixture_dir(MyFixture())
        self.assertEqual(self.expected_dir, actual_dir)


class RemoveFixtureTest(unit.TobikoUnitTest):

    def test_with_name(self):
        self._test_remove_fixture(canonical_name(MyFixture))

    def test_with_type(self):
        self._test_remove_fixture(MyFixture)

    def _test_remove_fixture(self, obj):
        fixture = tobiko.get_fixture(obj)
        result = tobiko.remove_fixture(obj)
        self.assertIs(fixture, result)
        self.assertIsNot(fixture, tobiko.get_fixture(obj))
        fixture.setup_fixture.assert_not_called()
        fixture.cleanup_fixture.assert_not_called()


class SetupFixtureTest(unit.TobikoUnitTest):

    def test_with_name(self):
        self._test_setup_fixture(canonical_name(MyFixture))

    def test_with_type(self):
        self._test_setup_fixture(MyFixture)

    def test_with_instance(self):
        self._test_setup_fixture(MyFixture2())

    def _test_setup_fixture(self, obj):
        result = tobiko.setup_fixture(obj)
        self.assertIs(tobiko.get_fixture(obj), result)
        result.setup_fixture.assert_called_once_with()
        result.cleanup_fixture.assert_not_called()


class FailingFixture(tobiko.SharedFixture):

    def setup_fixture(self):
        raise RuntimeError('raised by setup_fixture')

    def cleanup_fixture(self):
        raise RuntimeError('raised by cleanup_fixture')


class FailingSetupFixtureWhenFailingTest(unit.TobikoUnitTest):

    def test_with_name(self):
        self._test_setup_fixture(canonical_name(FailingFixture))

    def test_with_type(self):
        self._test_setup_fixture(FailingFixture)

    def test_with_instance(self):
        self._test_setup_fixture(FailingFixture())

    def _test_setup_fixture(self, obj):
        ex = self.assertRaises(RuntimeError, tobiko.setup_fixture, obj)
        self.assertEqual('raised by setup_fixture', str(ex))


class CleanupFixtureTest(unit.TobikoUnitTest):

    def test_with_name(self):
        self._test_cleanup_fixture(canonical_name(MyFixture))

    def test_with_type(self):
        self._test_cleanup_fixture(MyFixture)

    def test_with_instance(self):
        self._test_cleanup_fixture(MyFixture())

    def _test_cleanup_fixture(self, obj):
        result = tobiko.cleanup_fixture(obj)
        self.assertIs(tobiko.get_fixture(obj), result)
        result.setup_fixture.assert_not_called()
        result.cleanup_fixture.assert_called_once_with()


class MyFixtureWithProperty(MyBaseFixture):

    @tobiko.fixture_property
    def some_property(self):
        return id(self)


class FixturePropertyTest(unit.TobikoUnitTest):

    def test_with_instance(self):
        fixture = tobiko.get_fixture(MyFixtureWithProperty)
        self.assertEqual(id(fixture), fixture.some_property)

    def test_without_instance(self):
        fixture = tobiko.get_fixture(MyFixtureWithProperty)
        self.assertEqual(id(fixture), MyFixtureWithProperty.some_property)


class MyFixture2(MyBaseFixture):
    pass


class MyRequiredFixture(MyBaseFixture):
    pass


class MyRequiredSetupFixture(MyBaseFixture):
    pass


class ListRequiredFixtureTest(unit.TobikoUnitTest):

    required_fixture = tobiko.required_fixture(MyRequiredFixture)
    required_setup_fixture = tobiko.required_setup_fixture(
        MyRequiredSetupFixture)

    def test_with_module(self):
        module = sys.modules[__name__]
        result = tobiko.list_required_fixtures([module])
        self.assertEqual([], result)

    def test_with_module_name(self):
        result = tobiko.list_required_fixtures([__name__])
        self.assertEqual([], result)

    def test_with_testcase_type(self):
        result = tobiko.list_required_fixtures([ListRequiredFixtureTest])
        self.assertEqual([canonical_name(MyRequiredFixture),
                          canonical_name(MyRequiredSetupFixture)], result)

    def test_with_testcase_name(self):
        result = tobiko.list_required_fixtures(
            [canonical_name(ListRequiredFixtureTest)])
        self.assertEqual([canonical_name(MyRequiredFixture),
                          canonical_name(MyRequiredSetupFixture)], result)

    def test_with_unbound_method(self, fixture=MyFixture, fixture2=MyFixture2):
        result = tobiko.list_required_fixtures(
            [ListRequiredFixtureTest.test_with_unbound_method])
        self.assertEqual([canonical_name(fixture),
                          canonical_name(fixture2),
                          canonical_name(MyRequiredFixture),
                          canonical_name(MyRequiredSetupFixture)], result)

    def test_with_bound_method(self, fixture=MyFixture, fixture2=MyFixture2):
        result = tobiko.list_required_fixtures([self.test_with_bound_method])
        self.assertEqual([canonical_name(fixture),
                          canonical_name(fixture2),
                          canonical_name(MyRequiredFixture),
                          canonical_name(MyRequiredSetupFixture)], result)

    def test_with_method_name(self, fixture=MyFixture, fixture2=MyFixture2):
        result = tobiko.list_required_fixtures([self.id()])
        self.assertEqual([canonical_name(fixture),
                          canonical_name(fixture2),
                          canonical_name(MyRequiredFixture),
                          canonical_name(MyRequiredSetupFixture)], result)

    def test_with_fixture_name(self):
        result = tobiko.list_required_fixtures([canonical_name(MyFixture)])
        self.assertEqual([canonical_name(MyFixture)], result)

    def test_with_fixture(self):
        result = tobiko.list_required_fixtures([MyFixture()])
        self.assertEqual([canonical_name(MyFixture)], result)

    def test_with_fixture_type(self):
        result = tobiko.list_required_fixtures([MyFixture])
        self.assertEqual([canonical_name(MyFixture)], result)

    def test_required_fixture_property(self):
        fixture = self.required_fixture
        self.assertIsInstance(fixture, MyRequiredFixture)
        fixture.setup_fixture.assert_not_called()
        fixture.cleanup_fixture.assert_not_called()

    def test_required_setup_fixture_property(self):
        fixture = self.required_setup_fixture
        self.assertIsInstance(fixture, MyRequiredSetupFixture)
        fixture.setup_fixture.assert_called_once_with()
        fixture.cleanup_fixture.assert_not_called()


class SharedFixtureTest(unit.TobikoUnitTest):

    def setUp(self):
        super(SharedFixtureTest, self).setUp()
        tobiko.remove_fixture(MyFixture)

    def test_init(self):
        fixture = MyFixture()
        fixture.setup_fixture.assert_not_called()
        fixture.cleanup_fixture.assert_not_called()

    def test_get(self):
        fixture = MyFixture.get()
        self.assertIs(tobiko.get_fixture(MyFixture), fixture)

    def test_use_fixture(self):
        fixture = MyFixture()
        self.addCleanup(fixture.cleanup_fixture.assert_called_once_with)

        self.useFixture(fixture)
        fixture.setup_fixture.assert_called_once_with()
        fixture.cleanup_fixture.assert_not_called()

        self.useFixture(fixture)
        fixture.setup_fixture.assert_called_once_with()
        fixture.cleanup_fixture.assert_not_called()

    def test_add_cleanup(self):
        fixture = MyFixture()
        self.addCleanup(fixture.cleanup_fixture.assert_called_once_with)
        self.addCleanup(fixture.cleanUp)
        self.addCleanup(fixture.cleanUp)

    def test_setup(self):
        fixture = MyFixture()
        fixture.setUp()
        fixture.setup_fixture.assert_called_once_with()

    def test_setup_twice(self):
        fixture = MyFixture()
        fixture.setUp()
        fixture.setUp()
        fixture.setup_fixture.assert_called_once_with()

    def test_setup_when_skipping(self):
        fixture = MySkyppingFixture()
        self.assertRaises(testtools.MultipleExceptions, fixture.setUp)
        self.assertRaises(testtools.MultipleExceptions, fixture.setUp)

    def test_cleanup(self):
        fixture = MyFixture()
        fixture.cleanUp()
        fixture.cleanup_fixture.assert_called_once_with()

    def test_cleanup_twice(self):
        fixture = MyFixture()
        fixture.cleanUp()
        fixture.cleanUp()
        fixture.cleanup_fixture.assert_called_once_with()

    def test_cleanup_when_skipping(self):
        fixture = MySkyppingFixture()
        self.assertRaises(tobiko.SkipException, fixture.cleanUp)
        self.assertRaises(testtools.MultipleExceptions, fixture.cleanUp)

    def test_lifecycle(self):
        fixture = MyFixture()

        for call_count in range(3):
            fixture.setUp()
            fixture.setup_fixture.assert_has_calls([mock.call()] * call_count)
            fixture.setUp()
            fixture.setup_fixture.assert_has_calls([mock.call()] * call_count)

            fixture.cleanUp()
            fixture.cleanup_fixture.assert_has_calls(
                [mock.call()] * call_count)
            fixture.cleanUp()
            fixture.cleanup_fixture.assert_has_calls(
                [mock.call()] * call_count)
