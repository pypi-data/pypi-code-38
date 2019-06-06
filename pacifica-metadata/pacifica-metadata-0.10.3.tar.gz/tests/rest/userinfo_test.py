#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the UserInfoAPI object."""
from json import loads
import requests
from . import CPCommonTest


class TestUserInfoAPI(CPCommonTest):
    """Test aspects of the UserInfoAPI class."""

    __test__ = True

    def test_userinfo_api(self):
        """Test the GET method."""
        # test by user_id
        user_id = 10
        req = requests.get('{0}/userinfo/by_id/{1}'.format(self.url, user_id))
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        self.assertEqual(req_json['person_id'], user_id)

        # test search with name fragment
        search_terms = 'd+brown'
        req = requests.get(
            '{0}/userinfo/search/{1}'.format(self.url, search_terms))
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        self.assertEqual(len(req_json), 1)
        user = req_json.pop()
        self.assertEqual(user['person_id'], user_id)

        # test search with network_id, simple return
        search_terms = 'dmlb2001'
        req = requests.get(
            '{0}/userinfo/search/{1}/simple'.format(self.url, search_terms))
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        self.assertEqual(len(req_json), 1)
        user = req_json.pop()
        self.assertEqual(user['person_id'], user_id)

        # test search with network_id
        search_terms = 'dmlb2001'
        req = requests.get(
            '{0}/userinfo/search/{1}'.format(self.url, search_terms))
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        self.assertEqual(len(req_json), 1)
        user = req_json.pop()
        self.assertEqual(user['person_id'], user_id)

        # test search with user id
        search_terms = '10'
        req = requests.get(
            '{0}/userinfo/search/{1}'.format(self.url, search_terms))
        self.assertEqual(req.status_code, 200)
        req_json = loads(req.text)
        self.assertEqual(len(req_json), 1)
        user = req_json.pop()
        self.assertEqual(user['person_id'], user_id)

    def test_bad_userinfo_api(self):
        """Test the GET method with bad data."""
        str_user_id = 'bob'
        req = requests.get(
            '{0}/userinfo/by_id/{1}'.format(self.url, str_user_id))
        self.assertEqual(req.status_code, 400)
        self.assertTrue('Invalid Lookup Options' in req.text)

        user_id = 21
        req = requests.get('{0}/userinfo/by_id/{1}'.format(self.url, user_id))
        self.assertEqual(req.status_code, 404)
        self.assertTrue('Not Found' in req.text)

        req = requests.get('{0}/userinfo/by_id'.format(self.url))
        self.assertEqual(req.status_code, 400)
        self.assertTrue('Invalid Lookup Options' in req.text)

        search_terms = 'd+millard'
        req = requests.get(
            '{0}/userinfo/search/{1}'.format(self.url, search_terms))
        self.assertEqual(req.status_code, 404)
        self.assertTrue('No Valid Users Located' in req.text)

        # search with no terms
        req = requests.get(
            '{0}/userinfo/search'.format(self.url))
        self.assertEqual(req.status_code, 400)
        self.assertTrue('Invalid Request' in req.text)
