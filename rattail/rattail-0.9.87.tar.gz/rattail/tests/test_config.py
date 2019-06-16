# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

import os
import unittest
from six.moves import configparser

from mock import patch
from fixture import TempIO

from rattail import config


class TestParseBoolFunc(unittest.TestCase):

    def test_none(self):
        self.assertIsNone(config.parse_bool(None))

    def test_true(self):
        self.assertIs(config.parse_bool(True), True)

    def test_false(self):
        self.assertIs(config.parse_bool(False), False)

    def test_string(self):
        self.assertTrue(config.parse_bool('true'))
        self.assertTrue(config.parse_bool('yes'))
        self.assertTrue(config.parse_bool('on'))
        self.assertTrue(config.parse_bool('1'))

        self.assertFalse(config.parse_bool('false'))
        self.assertFalse(config.parse_bool('no'))
        self.assertFalse(config.parse_bool('off'))
        self.assertFalse(config.parse_bool('0'))


class TestParseListFunc(unittest.TestCase):

    def test_none(self):
        value = config.parse_list(None)
        self.assertEqual(len(value), 0)

    def test_single_value(self):
        value = config.parse_list(u'foo')
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], u'foo')

    def test_single_value_padded_by_spaces(self):
        value = config.parse_list(u'   foo   ')
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], u'foo')

    def test_slash_is_not_a_separator(self):
        value = config.parse_list(u'/dev/null')
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], u'/dev/null')

    def test_multiple_values_separated_by_whitespace(self):
        value = config.parse_list(u'foo bar baz')
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], u'foo')
        self.assertEqual(value[1], u'bar')
        self.assertEqual(value[2], u'baz')

    def test_multiple_values_separated_by_commas(self):
        value = config.parse_list(u'foo,bar,baz')
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], u'foo')
        self.assertEqual(value[1], u'bar')
        self.assertEqual(value[2], u'baz')

    def test_multiple_values_separated_by_whitespace_and_commas(self):
        value = config.parse_list(u'  foo,   bar   baz')
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], u'foo')
        self.assertEqual(value[1], u'bar')
        self.assertEqual(value[2], u'baz')

    def test_multiple_values_separated_by_whitespace_and_commas_with_some_quoting(self):
        value = config.parse_list("""
        foo
        "C:\\some path\\with spaces\\and, a comma",
        baz
        """)
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], u'foo')
        self.assertEqual(value[1], u'C:\\some path\\with spaces\\and, a comma')
        self.assertEqual(value[2], u'baz')


class TestRattailConfig(unittest.TestCase):

    def setUp(self):
        self.tempio = TempIO()

    def tearDown(self):
        del self.tempio

    def setup_files(self):
        self.site_path = self.tempio.putfile('site.conf', """
[rattail]
        """)

        self.host_path = self.tempio.putfile('host.conf', """
[rattail.config]
include = "{}"
        """.format(self.site_path))

        self.app_path = self.tempio.putfile('app.conf', """
[rattail.config]
include = "{}"
        """.format(self.host_path))

        self.custom_path = self.tempio.putfile('custom.conf', """
[rattail.config]
include = "%(here)s/app.conf"
        """)

    def test_init_defaults(self):
        cfg = config.RattailConfig()
        self.assertEqual(cfg.files_requested, [])
        self.assertEqual(cfg.files_read, [])
        self.assertIsNone(cfg._session_factory)

    def test_init_params(self):
        self.setup_files()

        # files
        cfg = config.RattailConfig()
        self.assertEqual(cfg.files_requested, [])
        self.assertEqual(cfg.files_read, [])
        cfg = config.RattailConfig(files=[self.site_path])
        self.assertEqual(cfg.files_requested, [self.site_path])
        self.assertEqual(cfg.files_read, [self.site_path])

        # usedb
        cfg = config.RattailConfig()
        self.assertFalse(cfg.usedb)
        cfg = config.RattailConfig(usedb=True)
        self.assertTrue(cfg.usedb)

        # preferdb
        cfg = config.RattailConfig()
        self.assertFalse(cfg.preferdb)
        cfg = config.RattailConfig(preferdb=True)
        self.assertTrue(cfg.preferdb)

    def test_read_file_with_recurse(self):
        self.setup_files()
        cfg = config.RattailConfig()
        cfg.read_file(self.custom_path, recurse=True)
        self.assertEqual(cfg.files_requested, [self.custom_path, self.app_path, self.host_path, self.site_path])
        self.assertEqual(cfg.files_read, [self.site_path, self.host_path, self.app_path, self.custom_path])

    def test_read_file_once_only(self):
        self.setup_files()

        another_path = self.tempio.putfile('another.conf', """
[rattail.config]
include = "{custom}" "{site}" "{app}" "{site}" "{custom}"
        """.format(custom=self.custom_path, app=self.app_path, site=self.site_path))

        cfg = config.RattailConfig()
        cfg.read_file(another_path, recurse=True)
        self.assertEqual(cfg.files_requested, [another_path, self.custom_path, self.app_path, self.host_path, self.site_path])
        self.assertEqual(cfg.files_read, [self.site_path, self.host_path, self.app_path, self.custom_path, another_path])

    def test_read_file_skip_missing(self):
        self.setup_files()
        bogus_path = '/tmp/does-not/exist'
        self.assertFalse(os.path.exists(bogus_path))

        another_path = self.tempio.putfile('another.conf', """
[rattail.config]
include = "{bogus}" "{app}" "{bogus}" "{site}"
        """.format(bogus=bogus_path, app=self.app_path, site=self.site_path))

        cfg = config.RattailConfig()
        cfg.read_file(another_path, recurse=True)
        self.assertEqual(cfg.files_requested, [another_path, bogus_path, self.app_path, self.host_path, self.site_path])
        self.assertEqual(cfg.files_read, [self.site_path, self.host_path, self.app_path, another_path])

    @patch('rattail.config.logging.config.fileConfig')
    def test_configure_logging(self, fileConfig):
        cfg = config.RattailConfig()

        # logging not configured by default
        cfg.configure_logging()
        self.assertFalse(fileConfig.called)

        # but config option can enable it
        cfg.set('rattail.config', 'configure_logging', 'true')
        cfg.configure_logging()
        self.assertEqual(fileConfig.call_count, 1)
        fileConfig.reset_mock()

        # invalid logging config is ignored
        fileConfig.side_effect = configparser.NoSectionError('loggers')
        cfg.configure_logging()
        self.assertEqual(fileConfig.call_count, 1)
