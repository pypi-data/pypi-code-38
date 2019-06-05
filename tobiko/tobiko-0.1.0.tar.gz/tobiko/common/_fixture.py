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
import inspect

import fixtures
from oslo_log import log
import six
import testtools

import tobiko

LOG = log.getLogger(__name__)


def is_fixture(obj):
    '''Returns whenever obj is a fixture or not'''
    return (getattr(obj, '__tobiko_fixture__', False) or
            isinstance(obj, fixtures.Fixture) or
            (inspect.isclass(obj) and issubclass(obj, fixtures.Fixture)))


def get_fixture(obj, manager=None):
    '''Returns a fixture identified by given :param obj:

    It returns registered fixture for given :param obj:. If none has been
    registered it creates a new one.

    :param obj: can be:
      - an instance of fixtures.Fixture class: on such case it would return
        obj itself
      - the unique fully qualified name or an object that refers to a fixture
        class or an instance to a fixture.
      - the class of the fixture. It must be a subclass of fixtures.Fixture
        sub-class.

    :returns: an instance of fixture class identified by obj, or obj itself
    if it is instance of fixtures.Fixture class.

    '''
    if isinstance(obj, fixtures.Fixture):
        return obj
    else:
        manager = manager or FIXTURES
        return manager.get_fixture(obj)


def get_fixture_name(obj):
    '''Get unique fixture name'''
    try:
        return obj.__tobiko_fixture_name__
    except AttributeError:
        name = get_object_name(obj)
        if is_fixture(obj):
            obj.__tobiko_fixture__ = True
            obj.__tobiko_fixture_name__ = name
            return name
    raise TypeError('Object {obj!r} is not a fixture.'.format(obj=obj))


def get_fixture_class(obj):
    '''Get fixture class'''
    if isinstance(obj, six.string_types):
        obj = tobiko.load_object(obj)

    if not inspect.isclass(obj):
        obj = type(obj)

    assert issubclass(obj, fixtures.Fixture)
    return obj


def get_fixture_dir(obj):
    '''Get directory of fixture class source code file'''
    return os.path.dirname(inspect.getfile(get_fixture_class(obj)))


def remove_fixture(obj, manager=None):
    '''Unregister fixture identified by given :param obj: if any'''
    manager = manager or FIXTURES
    return manager.remove_fixture(obj)


def setup_fixture(obj, manager=None):
    '''Get registered fixture and setup it up'''
    fixture = get_fixture(obj, manager=manager)
    try:
        fixture.setUp()
    except testtools.MultipleExceptions as ex:
        for exc_info in ex.args[1:]:
            LOG.exception("Error setting up fixture %r",
                          fixture.fixture_name, exc_info=exc_info)
        six.reraise(*ex.args[0])
    return fixture


def cleanup_fixture(obj, manager=None):
    '''Get registered fixture and clean it up'''
    fixture = get_fixture(obj, manager=manager)
    fixture.cleanUp()
    return fixture


def get_name_and_object(obj):
    '''Get (name, obj) tuple identified by given :param obj:'''
    if isinstance(obj, six.string_types):
        return obj, tobiko.load_object(obj)
    else:
        return get_object_name(obj), obj


def visit_objects(objects):
    if not isinstance(objects, list):
        raise TypeError("parameter 'objects' is not a list")

    visited = set()
    while objects:
        obj = objects.pop()
        try:
            name, obj = get_name_and_object(obj)
        except Exception:
            LOG.exception('Unable to get (name, object) pair from {!r}'.format(
                obj))
        else:
            if name not in visited:
                visited.add(name)
                yield name, obj


def list_required_fixtures(objects):
    '''List fixture names required by given objects'''
    result = []
    objects = list(objects)
    for name, obj in visit_objects(objects):
        if is_fixture(obj):
            result.append(name)
            continue

        if is_test_method(obj):
            # Test methods also require test class fixtures
            if '.' in name:
                parent_name = name.rsplit('.', 1)[0]
                objects.append(parent_name)

        objects.extend(get_required_fixture(obj))

    result.sort()
    return result


def is_test_method(obj):
    '''Returns whenever given object is a test method'''
    return ((inspect.isfunction(obj) or inspect.ismethod(obj)) and
            obj.__name__.startswith('test_'))


def get_required_fixture(obj):
    '''Get fixture names required by given :param obj:'''
    required_fixtures = getattr(obj, '__tobiko_required_fixtures__', None)
    if required_fixtures is None:
        required_fixtures = []
        try:
            # try to cache list for later use
            obj.__tobiko_required_fixtures__ = required_fixtures
        except AttributeError:
            pass

        if is_test_method(obj):
            defaults = six.get_function_defaults(obj)
            if defaults:
                for default in defaults:
                    if is_fixture(default):
                        required_fixtures.append(get_fixture_name(default))

        elif inspect.isclass(obj):
            # inspect.getmembers() would iterate over such many
            # testtools.TestCase members too, so let exclude members from
            # very base classes
            mro_index = obj.__mro__.index(testtools.TestCase)
            if mro_index > 0:
                member_names = sorted(set(
                    [name
                     for cls in obj.__mro__[:mro_index]
                     for name in cls.__dict__]))
                for member_name in member_names:
                    member = getattr(obj, member_name)
                    if isinstance(member, RequiredFixtureProperty):
                        required_fixtures.append(member.fixture)

    return required_fixtures


def init_fixture(obj, name):
    if (inspect.isclass(obj) and issubclass(obj, fixtures.Fixture)):
        obj = obj()

    if isinstance(obj, fixtures.Fixture):
        obj.__tobiko_fixture__ = True
        obj.__tobiko_fixture_name__ = name
        return obj

    raise TypeError("Invalid fixture object type: {!r}".format(obj))


def fixture_property(*args, **kwargs):
    return FixtureProperty(*args, **kwargs)


def required_fixture(obj):
    '''Creates a property that gets fixture identified by given :param obj:

    '''
    return RequiredFixtureProperty(obj)


def required_setup_fixture(obj):
    '''Creates a property that sets up fixture identified by given :param obj:

    '''
    return RequiredSetupFixtureProperty(obj)


def get_object_name(obj):
    '''Gets a fully qualified name for given :param obj:'''
    if isinstance(obj, six.string_types):
        return obj

    name = getattr(obj, '__tobiko_fixture_name__', None)
    if name:
        return name

    if (not inspect.isfunction(obj) and
            not inspect.ismethod(obj) and
            not inspect.isclass(obj)):
        obj = type(obj)

    module = inspect.getmodule(obj).__name__

    if six.PY2:
        # Below code is only for old Python versions
        if inspect.isclass(obj):
            # This doesn't work for nested classes
            return module + '.' + obj.__name__

        method_class = getattr(obj, 'im_class', None)
        if method_class:
            # This doesn't work for nested classes
            return module + '.' + method_class.__name__ + '.' + obj.__name__

        if inspect.isfunction(obj):
            return module + '.' + obj.func_name

    else:
        # Only Python 3 defines __qualname__
        name = getattr(obj, '__qualname__', None)
        if name:
            return module + '.' + name

    msg = "Unable to get fixture name from object {!r}".format(obj)
    raise TypeError(msg)


class FixtureManager(object):

    def __init__(self):
        self.fixtures = {}

    def get_fixture(self, obj, init=init_fixture):
        name, obj = get_name_and_object(obj)
        fixture = self.fixtures.get(name)
        if fixture is None:
            self.fixtures[name] = fixture = init(name=name, obj=obj)
            assert isinstance(fixture, fixtures.Fixture)
        return fixture

    def remove_fixture(self, obj):
        name = get_object_name(obj)
        return self.fixtures.pop(name, None)


FIXTURES = FixtureManager()


class SharedFixture(fixtures.Fixture):
    """Base class for fixtures intended to be shared between multiple tests

    Make sure that fixture setUp method can be called more than once, but
    actually executing _setUp method only the first time. This allows the
    fixture to be passed to useFixture methods multiple times without caring
    about if has already been used before.

    Fixture set up can anyway be forced by calling 'setup_shared_fixture'
    method.

    Because cleanup policy in a shared fixture is different from a common
    fixture, cleanUp method simply doesn't nothing.

    Actual fixture cleanup is executed by calling
    cleanup_shared_fixture method.

    """

    _setup_executed = False
    _cleanup_executed = False

    def __init__(self):
        # make sure class states can be used before setUp
        self._clear_cleanups()

    @classmethod
    def get(cls, manager=None):
        return get_fixture(cls, manager=manager)

    def _remove_state(self):
        # make sure class states can be used after cleanUp
        super(SharedFixture, self)._clear_cleanups()

    def setUp(self):
        """Executes _setUp/setup_fixture method only the first time is called

        """
        if not self._setup_executed:
            LOG.debug('Set up fixture %r', self.fixture_name)
            super(SharedFixture, self).setUp()
            self._cleanup_executed = False
            self._setup_executed = True

    def cleanUp(self, raise_first=True):
        """Executes registered cleanups if any"""
        if not self._cleanup_executed:
            LOG.debug('Clean up fixture %r', self.fixture_name)
            self.addCleanup(self.cleanup_fixture)
        result = super(SharedFixture, self).cleanUp(raise_first=raise_first)
        self._setup_executed = False
        self._cleanup_executed = True
        return result

    def _setUp(self):
        self.setup_fixture()

    @property
    def fixture_name(self):
        return get_fixture_name(self)

    def setup_fixture(self):
        pass

    def cleanup_fixture(self):
        pass


class FixtureProperty(property):

    def __get__(self, instance, owner):
        instance = instance or tobiko.get_fixture(owner)
        return super(FixtureProperty, self).__get__(instance, owner)


class RequiredFixtureProperty(object):

    def __init__(self, fixture):
        self.fixture = fixture

    def __get__(self, instance, _):
        if instance is None:
            return self
        else:
            return self.get_fixture()

    def get_fixture(self):
        return get_fixture(self.fixture)

    @property
    def __tobiko_required_fixtures__(self):
        return [self.fixture]


class RequiredSetupFixtureProperty(RequiredFixtureProperty):

    def get_fixture(self):
        return setup_fixture(self.fixture)
