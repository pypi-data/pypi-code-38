# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

import warnings
from unittest import TestCase

import six
from sqlalchemy import pool

from rattail.db import config as dbconfig
from rattail.config import RattailConfig


class TestEngineFromConfigFunc(TestCase):

    def test_default_key(self):
        cfg = {'sqlalchemy.url': 'sqlite://'}
        engine = dbconfig.engine_from_config(cfg)
        self.assertEqual(six.text_type(engine.url), 'sqlite://')

    def test_alternate_key(self):
        cfg = {'other.url': 'sqlite://'}
        engine = dbconfig.engine_from_config(cfg, prefix='other.')
        self.assertEqual(six.text_type(engine.url), 'sqlite://')

    def test_poolclass(self):

        # default is SingletonThreadPool
        cfg = {'sqlalchemy.url': 'sqlite://'}
        engine = dbconfig.engine_from_config(cfg)
        self.assertEqual(six.text_type(engine.url), 'sqlite://')
        self.assertIsInstance(engine.pool, pool.SingletonThreadPool)

        # usually we override with NullPool
        cfg = {'sqlalchemy.url': 'sqlite://',
               'sqlalchemy.poolclass': 'sqlalchemy.pool:NullPool'}
        engine = dbconfig.engine_from_config(cfg)
        self.assertEqual(six.text_type(engine.url), 'sqlite://')
        self.assertIsInstance(engine.pool, pool.NullPool)

    def test_record_changes(self):

        # no attribute is set by default
        cfg = {'sqlalchemy.url': 'sqlite://'}
        engine = dbconfig.engine_from_config(cfg)
        self.assertRaises(AttributeError, getattr, engine, 'rattail_record_changes')

        # usually we override with NullPool
        cfg = {'sqlalchemy.url': 'sqlite://',
               'sqlalchemy.record_changes': 'true'}
        engine = dbconfig.engine_from_config(cfg)
        self.assertTrue(engine.rattail_record_changes)


class TestGetEngines(TestCase):

    def setUp(self):
        self.config = RattailConfig()

    def test_default_section_is_rattail_db(self):
        self.config.set(u'rattail.db', u'keys', u'default')
        self.config.set(u'rattail.db', u'default.url', u'sqlite://')
        engines = dbconfig.get_engines(self.config)
        self.assertEqual(len(engines), 1)
        self.assertEqual(list(engines)[0], 'default')
        self.assertEqual(six.text_type(engines['default'].url), 'sqlite://')

    def test_custom_section_is_honored(self):
        self.config.set(u'mycustomdb', u'keys', u'default')
        self.config.set(u'mycustomdb', u'default.url', u'sqlite://')
        engines = dbconfig.get_engines(self.config, section=u'mycustomdb')
        self.assertEqual(len(engines), 1)
        self.assertEqual(list(engines)[0], 'default')
        self.assertEqual(six.text_type(engines['default'].url), 'sqlite://')

    def test_default_prefix_does_not_require_keys_declaration(self):
        self.config.set(u'rattail.db', u'default.url', u'sqlite://')
        engines = dbconfig.get_engines(self.config)
        self.assertEqual(len(engines), 1)
        self.assertEqual(list(engines)[0], 'default')
        self.assertEqual(six.text_type(engines['default'].url), 'sqlite://')

    def test_default_prefix_falls_back_to_sqlalchemy(self):
        # Still no need to define "keys" option here.
        self.config.set(u'rattail.db', u'sqlalchemy.url', u'sqlite://')
        engines = dbconfig.get_engines(self.config)
        self.assertEqual(len(engines), 1)
        self.assertEqual(list(engines)[0], 'default')
        self.assertEqual(six.text_type(engines['default'].url), 'sqlite://')

    def test_defined_keys_are_included_in_engines_result(self):
        # Note there is no "default" key here.
        self.config.set(u'rattail.db', u'keys', u'host, store')
        self.config.set(u'rattail.db', u'host.url', u'sqlite:///rattail.host.sqlite')
        self.config.set(u'rattail.db', u'store.url', u'sqlite:///rattail.store.sqlite')
        engines = dbconfig.get_engines(self.config)
        self.assertEqual(len(engines), 2)
        self.assertEqual(sorted(engines.keys()), [u'host', u'store'])
        self.assertEqual(six.text_type(engines['host'].url), 'sqlite:///rattail.host.sqlite')
        self.assertEqual(six.text_type(engines['store'].url), 'sqlite:///rattail.store.sqlite')


class TestGetDefaultEngine(TestCase):

    def setUp(self):
        self.config = RattailConfig()

    def test_default_engine_is_loaded_from_rattail_db_section_by_default(self):
        self.config.set(u'rattail.db', u'keys', u'default')
        self.config.set(u'rattail.db', u'default.url', u'sqlite://')
        engine = dbconfig.get_default_engine(self.config)
        self.assertEqual(six.text_type(engine.url), 'sqlite://')

    def test_default_engine_is_loaded_from_custom_section_if_specified(self):
        self.config.set(u'mycustomdb', u'keys', u'default')
        self.config.set(u'mycustomdb', u'default.url', u'sqlite://')
        engine = dbconfig.get_default_engine(self.config, section=u'mycustomdb')
        self.assertEqual(six.text_type(engine.url), 'sqlite://')

    def test_no_engine_is_returned_if_none_is_defined(self):
        engine = dbconfig.get_default_engine(self.config)
        self.assertTrue(engine is None)
