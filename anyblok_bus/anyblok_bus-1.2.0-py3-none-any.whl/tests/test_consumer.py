# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from anyblok.config import Configuration
from anyblok_bus.consumer import (bus_consumer, BusConfigurationException)
from anyblok_bus.bloks.bus.exceptions import TwiceQueueConsumptionException
from marshmallow import Schema, fields
from json import dumps
from anyblok import Declarations
from marshmallow.exceptions import ValidationError
from anyblok.registry import RegistryManager
from anyblok.environment import EnvironmentManager


class OneSchema(Schema):
    label = fields.String()
    number = fields.Integer()


class TestValidator(DBTestCase):

    # TODO remove this when this functionnality will be in anyblok
    def reload_registry(self, registry, function, **kwargs):
        """ call a function to filled the blok manager with new model and
        before reload the registry

        :param bloks: list of blok's names
        :param function: function to call
        :param kwargs: kwargs for the function
        :rtype: registry instance
        """
        from copy import deepcopy
        loaded_bloks = deepcopy(RegistryManager.loaded_bloks)
        if function is not None:
            EnvironmentManager.set('current_blok', 'anyblok-test')
            try:
                function(**kwargs)
            finally:
                EnvironmentManager.set('current_blok', None)

        try:
            registry.reload()
        finally:
            RegistryManager.loaded_bloks = loaded_bloks

        return registry

    def add_in_registry(self, schema=None):

        @Declarations.register(Declarations.Model)
        class Test:

            @bus_consumer(queue_name='test', schema=schema)
            def decorated_method(cls, body=None):
                return body

    def test_schema_ok(self):
        registry = self.init_registry(self.add_in_registry, schema=OneSchema())
        self.assertEqual(
            registry.Test.decorated_method(
                body=dumps({'label': 'test', 'number': '1'})),
            {'label': 'test', 'number': 1}
        )

    def test_schema_ko(self):
        registry = self.init_registry(self.add_in_registry, schema=OneSchema())
        with self.assertRaises(ValidationError):
            registry.Test.decorated_method(
                body=dumps({'label': 'test', 'number': 'other'}))

    def test_decorator_without_name(self):
        def add_in_registry():
            @Declarations.register(Declarations.Model)
            class Test:

                @bus_consumer(schema=OneSchema())
                def decorated_method(cls, body=None):
                    return body

        with self.assertRaises(BusConfigurationException):
            self.init_registry(add_in_registry)

    def test_decorator_with_twice_the_same_name(self):

        def add_in_registry():
            @Declarations.register(Declarations.Model)
            class Test:

                @bus_consumer(queue_name='test', schema=OneSchema())
                def decorated_method1(cls, body=None):
                    return body

                @bus_consumer(queue_name='test', schema=OneSchema())
                def decorated_method2(cls, body=None):
                    return body

        registry = self.init_registry_with_bloks(('bus',), add_in_registry)
        with self.assertRaises(TwiceQueueConsumptionException):
            registry.Bus.get_consumers()

    def test_decorator_with_twice_the_same_name2(self):

        def add_in_registry():
            @Declarations.register(Declarations.Model)
            class Test:

                @bus_consumer(queue_name='test', schema=OneSchema())
                def decorated_method(cls, body=None):
                    return body

            @Declarations.register(Declarations.Model)
            class Test2:

                @bus_consumer(queue_name='test', schema=OneSchema())
                def decorated_method(cls, body=None):
                    return body

        registry = self.init_registry_with_bloks(('bus',), add_in_registry)
        with self.assertRaises(TwiceQueueConsumptionException):
            registry.Bus.get_consumers()

    def test_reload(self):
        registry = self.init_registry(self.add_in_registry, schema=OneSchema())
        self.reload_registry(registry, self.add_in_registry, schema=OneSchema())

    def test_with_two_decorator(self):

        def add_in_registry():
            @Declarations.register(Declarations.Model)
            class Test:

                @bus_consumer(queue_name='test1', schema=OneSchema())
                def decorated_method1(cls, body=None):
                    return body

                @bus_consumer(queue_name='test2', schema=OneSchema())
                def decorated_method2(cls, body=None):
                    return body

        registry = self.init_registry_with_bloks(('bus',), add_in_registry)
        # [(nb processes, [(queue, Model, method)])]
        self.assertEqual(len(registry.Bus.get_consumers()), 1)
        self.assertEqual(len(registry.Bus.get_consumers()[0]), 2)
        self.assertEqual(len(registry.Bus.get_consumers()[0][1]), 2)

    def test_with_two_decorator_in_different_processes(self):

        def add_in_registry():
            @Declarations.register(Declarations.Model)
            class Test:

                @bus_consumer(queue_name='test1', schema=OneSchema(),
                              processes=1)
                def decorated_method1(cls, body=None):
                    return body

                @bus_consumer(queue_name='test2', schema=OneSchema(),
                              processes=1)
                def decorated_method2(cls, body=None):
                    return body

        registry = self.init_registry_with_bloks(('bus',), add_in_registry)
        # [(nb processes, [(queue, Model, method)])]
        self.assertEqual(len(registry.Bus.get_consumers()), 2)
        self.assertEqual(len(registry.Bus.get_consumers()[0]), 2)
        self.assertEqual(len(registry.Bus.get_consumers()[0][1]), 1)
        self.assertEqual(len(registry.Bus.get_consumers()[1]), 2)
        self.assertEqual(len(registry.Bus.get_consumers()[1][1]), 1)

    def test_consumer_add_in_get_profile(self):
        registry = self.init_registry_with_bloks(
            ('bus',), self.add_in_registry, schema=OneSchema())
        self.assertEqual(registry.Bus.get_consumers(),
                         [(Configuration.get('bus_processes', 1),
                           [('test', 'Model.Test', 'decorated_method')])])
