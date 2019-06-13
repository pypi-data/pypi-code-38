# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

from unittest import TestCase
from six import StringIO

from mock import patch

from rattail import csvutil


class TestDictWriter(TestCase):

    def test_writeheader_26(self):
        # Simulate Python 2.6
        with patch('csv.writer'):
            with patch('rattail.csvutil.csv.DictWriter', spec=['writer']) as DictWriter:
                buf = StringIO()
                writer = csvutil.DictWriter(buf, ['field1', 'field2'])
                writer.writeheader()
                buf.close()
                writer.writer.writerow.assert_called_once_with(['field1', 'field2'])

    def test_writeheader_27(self):
        # Simulate Python 2.7+
        with patch('csv.writer'):
            with patch('rattail.csvutil.csv.DictWriter', spec=['writer', 'writeheader']) as DictWriter:
                buf = StringIO()
                writer = csvutil.DictWriter(buf, ['field1', 'field2'])
                writer.writeheader()
                buf.close()
                self.assertFalse(writer.writer.writerow.called)
                DictWriter.writeheader.assert_called_once_with(writer)
