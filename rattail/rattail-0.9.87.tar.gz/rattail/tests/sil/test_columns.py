# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from unittest import TestCase

from mock import patch

from rattail.sil import columns
from rattail.sil.exceptions import SILColumnNotFound


class TestGetColumn(TestCase):

    def test_exception_raised_if_no_such_column_exists(self):
        with patch('rattail.sil.columns.supported_columns', new={}):
            self.assertRaises(SILColumnNotFound, columns.get_column, 'bogus-column')
