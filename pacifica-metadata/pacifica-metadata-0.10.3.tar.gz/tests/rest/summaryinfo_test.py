#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the ORM interface SummaryInfoAPI."""
import datetime
import requests
from . import CPCommonTest


class TestSummaryInfoAPI(CPCommonTest):
    """Test the SummaryInfoAPI class."""

    __test__ = True

    def test_summaryinfo_api(self):
        """Test the POST method."""
        # test for modified time with instrument
        instrument_list = [54]
        header_list = {'Content-Type': 'application/json'}
        url = '{0}/summaryinfo/by_date/modified/instrument/'.format(self.url)
        url += '2016-11-01/2016-12-31'
        req = requests.post(
            url=url, json=instrument_list, headers=header_list
        )
        self.assertEqual(req.status_code, 200)

        # test for submitted time with instruemnt
        url = '{0}/summaryinfo/by_date/submitted/instrument/'.format(self.url)
        tomorrow = datetime.datetime.utcnow().date() + datetime.timedelta(days=1)
        yesterday = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)
        url += '{0}/{1}'.format(tomorrow.strftime('%Y-%m-%d'),
                                yesterday.strftime('%Y-%m-%d'))

        req = requests.post(
            url=url, json=instrument_list, headers=header_list
        )
        self.assertEqual(req.status_code, 200)

    def test_detailed_list(self):
        """Test the detailed_transaction_list function."""
        transaction_list = [67, 68]
        header_list = {'Content-Type': 'application/json'}
        url = '{0}/summaryinfo/transaction_details'.format(self.url)
        req = requests.post(
            url=url, json=transaction_list, headers=header_list
        )
        self.assertEqual(req.status_code, 200)

    def test_bad_summaryinfo_api(self):
        """Test the POST method with bad data."""
        # test for modified time with bad time basis and times
        instrument_list = [54]
        header_list = {'Content-Type': 'application/json'}
        url = '{0}/summaryinfo/by_date/fred/betty/'.format(self.url)
        url += 'barney/wilma'
        req = requests.post(
            url=url, json=instrument_list, headers=header_list
        )
        self.assertEqual(req.status_code, 200)
