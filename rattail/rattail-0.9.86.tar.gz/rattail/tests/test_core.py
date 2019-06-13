# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

from unittest import TestCase

import six

from rattail import core


class TestCore(TestCase):

    def test_get_uuid(self):
        uuid = core.get_uuid()
        self.assertTrue(isinstance(uuid, six.string_types))
        self.assertEqual(len(uuid), 32)
