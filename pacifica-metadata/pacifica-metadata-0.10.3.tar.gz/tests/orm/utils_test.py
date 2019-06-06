#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the metadata.orm.utils methods."""
from unittest import TestCase
from datetime import datetime, date
from pacifica.metadata.orm.utils import index_hash, datetime_converts, date_converts, datetime_now_nomicrosecond


class TestUtils(TestCase):
    """Test the utils methods to make sure they work and have covergage."""

    def test_index_hash(self):
        """Test the index hash method with some static knowns."""
        in_data = (123, 456)
        chk_data = 'e10adc3949ba59abbe56e057f20f883e'
        self.assertEqual(index_hash(*in_data), chk_data)

    def test_datetime_converts(self):
        """
        The method supports three types of conversions.

        1. a parsable string either unicode or str
        2. a datetime object
        3. an epoch style int
        """
        self.assertEqual(datetime_converts(0), datetime.utcfromtimestamp(0))
        now_chk = datetime_now_nomicrosecond()
        self.assertEqual(datetime_converts(now_chk), now_chk)
        chk_date = datetime(2016, 7, 5, 9, 22, 12)
        uni_date = u'2016-07-05T09:22:12'
        str_date = '2016-07-05T09:22:12'
        self.assertEqual(datetime_converts(uni_date), chk_date)
        self.assertEqual(datetime_converts(str_date), chk_date)
        # error state something it can't deal with
        self.assertEqual(datetime_converts({}), None)

    def test_date_converts(self):
        """
        The method supports three types of conversions.

        1. a parsable string either unicode or str
        2. a datetime object
        3. an epoch style int
        """
        self.assertEqual(date_converts(0), datetime.utcfromtimestamp(0).date())
        now_chk = datetime.utcnow().date()
        self.assertEqual(date_converts(now_chk), now_chk)
        chk_date = date(2016, 7, 5)
        uni_date = u'2016-07-05'
        str_date = '2016-07-05'
        self.assertEqual(date_converts(uni_date), chk_date)
        self.assertEqual(date_converts(str_date), chk_date)
        # error state something it can't deal with
        self.assertEqual(date_converts({}), None)
