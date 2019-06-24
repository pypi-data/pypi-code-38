# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from anyblok_bus import bus_consumer
from anyblok.column import Integer, String
from marshmallow import Schema, fields
from json import dumps
from anyblok import Declarations
from anyblok_bus.status import MessageStatus


class OneSchema(Schema):
    label = fields.String(required=True)
    number = fields.Integer(required=True)


class TestMessage(DBTestCase):

    def add_in_registry(self, schema=None):

        @Declarations.register(Declarations.Model)
        class Test:
            id = Integer(primary_key=True)
            label = String()
            number = Integer()

            @bus_consumer(queue_name='test', schema=OneSchema())
            def decorated_method(cls, body=None):
                cls.insert(**body)
                return MessageStatus.ACK

    def test_message_ok(self):
        registry = self.init_registry_with_bloks(
            ('bus',), self.add_in_registry)
        file_ = dumps({'label': 'label', 'number': 1})
        message = registry.Bus.Message.insert(
            message=file_.encode('utf-8'),
            queue='test',
            model='Model.Test',
            method='decorated_method')
        self.assertEqual(self.registry.Test.query().count(), 0)
        message.consume()
        self.assertEqual(self.registry.Test.query().count(), 1)
        self.assertEqual(self.registry.Bus.Message.query().count(), 0)

    def test_message_ko(self):
        registry = self.init_registry_with_bloks(
            ('bus',), self.add_in_registry)
        file_ = dumps({'label': 'label'})
        message = registry.Bus.Message.insert(
            message=file_.encode('utf-8'),
            queue='test',
            model='Model.Test',
            method='decorated_method')
        self.assertEqual(self.registry.Test.query().count(), 0)
        message.consume()
        self.assertEqual(self.registry.Test.query().count(), 0)
        self.assertEqual(self.registry.Bus.Message.query().count(), 1)

    def test_message_consume_all(self):
        registry = self.init_registry_with_bloks(
            ('bus',), self.add_in_registry)
        Test = self.registry.Test
        file_ = dumps({'label': 'label', 'number': 2})
        registry.Bus.Message.insert(
            message=file_.encode('utf-8'),
            sequence=2,
            queue='test',
            model='Model.Test',
            method='decorated_method')
        file_ = dumps({'label': 'label', 'number': 1})
        registry.Bus.Message.insert(
            message=file_.encode('utf-8'),
            sequence=1,
            queue='test',
            model='Model.Test',
            method='decorated_method')
        self.assertEqual(Test.query().count(), 0)
        self.registry.Bus.Message.consume_all()
        self.assertEqual(Test.query().count(), 2)
        self.assertEqual(Test.query().order_by(Test.id).all().number, [1, 2])
        self.assertEqual(self.registry.Bus.Message.query().count(), 0)
