#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the ORM interface InstrumentInfo."""
import requests
from . import CPCommonTest


class TestInstrumentInfoAPI(CPCommonTest):
    """Test the ObjectInfoAPI class."""

    __test__ = True

    def _get_instrument_details(self, instrument_id):
        header_list = {'Content-Type': 'application/json'}
        url = '{0}/instrumentinfo/by_instrument_id/{1}'.format(
            self.url, instrument_id)
        req = requests.get(url=url, headers=header_list)
        return req

    def _search_for_instrument(self, search_term):
        header_list = {'Content-Type': 'application/json'}
        url = '{0}/instrumentinfo/search/{1}'.format(self.url, search_term)
        req = requests.get(url=url, headers=header_list)
        return req

    def _get_instruments_for_user(self, user_id):
        header_list = {'Content-Type': 'application/json'}
        url = '{0}/instrumentinfo/by_user_id/{1}'.format(self.url, user_id)
        req = requests.get(url=url, headers=header_list)
        return req

    def _get_instrument_categories(self):
        header_list = {'Content-Type': 'application/json'}
        url = '{0}/instrumentinfo/categories/'.format(self.url)
        req = requests.get(url=url, headers=header_list)
        return req

    def test_instrumentinfo_api(self):
        """Test the GET method."""
        # test instrument lookup with good id
        instrument_id = 54
        req = self._get_instrument_details(instrument_id)
        self.assertEqual(req.status_code, 200)
        results = req.json()
        self.assertTrue('Nittany' in results['name_short'])

        # test instrument search with known valid term
        search_term = 'nittany'
        req = self._search_for_instrument(search_term)
        self.assertEqual(req.status_code, 200)

        # test instrument search with known id term
        search_term = '54'
        req = self._search_for_instrument(search_term)
        self.assertEqual(req.status_code, 200)

        # test get instruments for user
        user_id = 10
        req = self._get_instruments_for_user(user_id=user_id)
        self.assertEqual(req.status_code, 200)

        # test instrument category retrieval
        req = self._get_instrument_categories()
        self.assertEqual(req.status_code, 200)

    def test_bad_instrumentinfo_api(self):
        """Test the GET method with bad data."""
        # test instrument lookup with nonexistant id
        instrument_id = 96
        req = self._get_instrument_details(instrument_id)
        self.assertEqual(req.status_code, 404)

        # test instrument with malformed id
        text_instrument_id = 'bob'
        req = self._get_instrument_details(text_instrument_id)
        self.assertEqual(req.status_code, 400)

        # test instrument search with known invalid term
        search_term = 'supercalifragilistic'
        req = self._search_for_instrument(search_term)
        self.assertEqual(req.status_code, 404)

        # test instrument search with empty search term
        search_term = ''
        req = self._search_for_instrument(search_term)
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.text, '[]')

        # test get instruments for user
        user_id = 11
        req = self._get_instruments_for_user(user_id=user_id)
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.text, '[]')
