# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

import unittest

import six

from rattail import exceptions


class TestRecipientsNotFound(unittest.TestCase):

    def test_init(self):
        self.assertRaises(TypeError, exceptions.RecipientsNotFound)
        exc = exceptions.RecipientsNotFound('testing')
        self.assertEqual(exc.key, 'testing')

    def test_unicode(self):
        exc = exceptions.RecipientsNotFound('testing')
        self.assertEqual(six.text_type(exc),
                         "No recipients found in config for 'testing' emails.  Please set "
                         "'testing.to' (or 'default.to') in the [rattail.mail] section.")
