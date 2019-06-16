# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

import datetime
from unittest import TestCase

import pytz

from rattail import time
from rattail.config import make_config
from rattail.exceptions import ConfigurationError


class TestLocaltime(TestCase):

    def setUp(self):
        self.config = make_config([])
        self.config.set('rattail', 'timezone.default', 'America/Los_Angeles')
        self.config.set('rattail', 'timezone.missouri', 'America/Chicago')

    def test_default_returns_current_time_in_default_timezone(self):
        zone = pytz.timezone('America/Los_Angeles')
        before = zone.normalize(pytz.utc.localize(datetime.datetime.utcnow()).astimezone(zone))
        local = time.localtime(self.config)
        after = zone.normalize(pytz.utc.localize(datetime.datetime.utcnow()).astimezone(zone))
        self.assertTrue(before <= local)
        self.assertTrue(local <= after)
        self.assertEqual(local.tzinfo.zone, 'America/Los_Angeles')

    def test_provided_time_is_localized_to_default_timezone(self):
        t = datetime.datetime(2014, 7, 26, 8, 28, 41)
        t = time.localtime(self.config, t)
        self.assertEqual(t.year, 2014)
        self.assertEqual(t.month, 7)
        self.assertEqual(t.day, 26)
        self.assertEqual(t.hour, 8)
        self.assertEqual(t.minute, 28)
        self.assertEqual(t.second, 41)
        self.assertEqual(t.tzinfo.zone, 'America/Los_Angeles')

    def test_provided_time_is_localized_to_custom_timezone(self):
        t = datetime.datetime(2014, 7, 26, 8, 28, 41)
        t = time.localtime(self.config, t, 'missouri')
        self.assertEqual(t.year, 2014)
        self.assertEqual(t.month, 7)
        self.assertEqual(t.day, 26)
        self.assertEqual(t.hour, 8)
        self.assertEqual(t.minute, 28)
        self.assertEqual(t.second, 41)
        self.assertEqual(t.tzinfo.zone, 'America/Chicago')


class TestTimezone(TestCase):

    def setUp(self):
        self.config = make_config([])

    def test_default_timezone_returned_by_default(self):
        self.config.set('rattail', 'timezone.default', 'Antarctica/Rothera')
        zone = time.timezone(self.config)
        self.assertEqual(zone.zone, 'Antarctica/Rothera')

    def test_local_timezone_returned_if_no_default(self):
        self.config.set('rattail', 'timezone.local', 'Africa/Lagos')
        zone = time.timezone(self.config)
        self.assertEqual(zone.zone, 'Africa/Lagos')

    def test_custom_timezone_returned_instead_of_default(self):
        self.config.set('rattail', 'timezone.another', 'Canada/Yukon')
        zone = time.timezone(self.config, key='another')
        self.assertEqual(zone.zone, 'Canada/Yukon')

    def test_config_error_if_no_timezone_defined(self):
        self.assertRaises(ConfigurationError, time.timezone, self.config)
