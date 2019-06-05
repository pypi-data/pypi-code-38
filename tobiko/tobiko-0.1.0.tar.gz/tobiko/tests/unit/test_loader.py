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

import sys

import tobiko
from tobiko.common.managers import loader
from tobiko.tests.unit import TobikoUnitTest


SOME_NONE = None


class SomeClass(object):

    def some_method(self):
        pass


class TestLoader(TobikoUnitTest):

    def setUp(self):
        super(TestLoader, self).setUp()
        self.manager = loader.LoaderManager()
        self.patch(loader, 'LOADERS', self.manager)

    def test_load_object_with_none(self):
        object_id = '.'.join([__name__, 'SOME_NONE'])
        obj = tobiko.load_object(object_id)
        self.assertIsNone(obj)

        _loader = self.manager.get_loader(object_id)
        self.assertEqual(_loader.id, object_id)
        self.assertFalse(_loader.is_module)
        self.assertIs(_loader.get(), obj)
        self.assertIs(_loader, self.manager.get_loader(object_id))

    def test_load_module_with_none(self):
        object_id = '.'.join([__name__, 'SOME_NONE'])
        module = tobiko.load_module(object_id)
        self.assertEqual(__name__, module.__name__)

    def test_load_object_with_module(self):
        object_id = __name__
        obj = tobiko.load_object(object_id)
        self.assertIs(sys.modules[object_id], obj)

        _loader = self.manager.get_loader(object_id)
        self.assertEqual(_loader.id, object_id)
        self.assertTrue(_loader.is_module)
        self.assertIs(_loader.get(), obj)
        self.assertIs(_loader, self.manager.get_loader(object_id))

    def test_load_module_with_module(self):
        object_id = __name__
        module = tobiko.load_module(object_id)
        self.assertEqual(__name__, module.__name__)

    def test_load_object_with_class(self):
        object_id = '.'.join([SomeClass.__module__,
                              SomeClass.__name__])
        obj = tobiko.load_object(object_id)
        self.assertIs(SomeClass, obj)

    def test_load_module_with_class(self):
        object_id = '.'.join([SomeClass.__module__,
                              SomeClass.__name__])
        module = tobiko.load_module(object_id)
        self.assertEqual(__name__, module.__name__)

    def test_load_object_with_class_method(self):
        object_id = '.'.join([SomeClass.__module__,
                              SomeClass.__name__,
                              SomeClass.some_method.__name__])
        obj = tobiko.load_object(object_id)
        self.assertEqual(SomeClass.some_method, obj)

        _loader = self.manager.get_loader(object_id)
        self.assertEqual(_loader.id, object_id)
        self.assertFalse(_loader.is_module)
        self.assertIs(_loader.get(), obj)
        self.assertIs(_loader, self.manager.get_loader(object_id))

    def test_load_module_with_class_method(self):
        object_id = '.'.join([SomeClass.__module__,
                              SomeClass.__name__,
                              SomeClass.some_method.__name__])
        module = tobiko.load_module(object_id)
        self.assertEqual(__name__, module.__name__)

    def test_load_object_with_non_existing(self):
        object_id = '.'.join([SomeClass.__module__, '<non-existing>'])
        self.assertRaises(ImportError, tobiko.load_object, object_id)

    def test_load_module_with_non_existing(self):
        object_id = '.'.join([SomeClass.__module__, '<non-existing>'])
        self.assertRaises(ImportError, tobiko.load_module, object_id)

    def test_load_object_with_non_existing_member(self):
        object_id = '.'.join([SomeClass.__module__,
                              SomeClass.__name__,
                              '<non-existing>'])
        self.assertRaises(AttributeError, tobiko.load_object, object_id)

    def test_load_module_with_non_existing_member(self):
        object_id = '.'.join([SomeClass.__module__,
                              SomeClass.__name__,
                              '<non-existing>'])
        self.assertRaises(AttributeError, tobiko.load_module, object_id)
