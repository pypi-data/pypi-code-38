# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

from unittest import TestCase

import six
import sqlalchemy as sa
from fixture import TempIO

from rattail import db
from rattail.config import RattailConfig


class TestSession(TestCase):

    def test_init_rattail_config(self):
        session = db.Session()
        self.assertIsNone(session.rattail_config)
        session.close()

        config = object()
        session = db.Session(rattail_config=config)
        self.assertIs(session.rattail_config, config)
        session.close()

    def test_init_record_changes(self):
        if hasattr(db.Session, 'kw'):
            self.assertFalse(db.Session.kw['rattail_record_changes'])

        session = db.Session()
        self.assertFalse(session.rattail_record_changes)
        session.close()

        session = db.Session(rattail_record_changes=True)
        self.assertTrue(session.rattail_record_changes)
        session.close()

        engine = sa.create_engine('sqlite://')
        engine.rattail_record_changes = True
        session = db.Session(bind=engine)
        self.assertTrue(session.rattail_record_changes)
        session.close()


class TestConfigExtension(TestCase):

    def setUp(self):
        self.tempio = TempIO()

    def tearDown(self):
        db.Session.configure(bind=None, rattail_config=None)
        self.tempio = None

    def test_configure_empty(self):
        config = RattailConfig()
        self.assertRaises(AttributeError, getattr, config, 'rattail_engines')
        self.assertRaises(AttributeError, getattr, config, 'rattail_engine')
        if hasattr(db.Session, 'kw'):
            self.assertIsNone(db.Session.kw['bind'])
            self.assertIsNone(db.Session.kw['rattail_config'])

        db.ConfigExtension().configure(config)
        self.assertEqual(config.rattail_engines, {})
        self.assertIsNone(config.rattail_engine)
        if hasattr(db.Session, 'kw'):
            self.assertIs(db.Session.kw['rattail_config'], config)

    def test_configure_connections(self):
        default_path = self.tempio.putfile('default.sqlite', '')
        default_url = 'sqlite:///{}'.format(default_path)
        host_path = self.tempio.putfile('host.sqlite', '')
        host_url = 'sqlite:///{}'.format(host_path)

        config = RattailConfig()
        config.set('rattail.db', 'keys', 'default, host')
        config.set('rattail.db', 'default.url', default_url)
        config.set('rattail.db', 'host.url', host_url)
        db.ConfigExtension().configure(config)
        self.assertEqual(len(config.rattail_engines), 2)
        self.assertEqual(six.text_type(config.rattail_engines['default'].url), default_url)
        self.assertEqual(six.text_type(config.rattail_engines['host'].url), host_url)
        self.assertEqual(six.text_type(config.rattail_engine.url), default_url)
