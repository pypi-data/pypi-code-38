#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test status policy methods."""
from json import loads, dumps
from cherrypy.test import helper
from common_test import CommonCPSetup


class TestStatusPolicy(helper.CPWebCase, CommonCPSetup):
    """Test the status policy service."""

    PORT = 8181
    HOST = '127.0.0.1'
    headers = [('Content-Type', 'application/json')]

    def test_instrument_by_project(self):
        """Return instruments for a specified project."""
        url = '/status/instrument/by_project_id/1234a'
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body.decode('UTF-8'))
        self.assertEqual(len(answer.get('items')), 2)

        # Test nonexistent project
        url = '/status/instrument/by_project_id/3455'
        self.getPage(url)
        self.assertStatus('404 Not Found')

        # Test bad project format
        url = '/status/instrument/by_project_id/bob123'
        self.getPage(url)
        self.assertStatus('400 Invalid Request')

        # Test with no instruments to return
        url = '/status/instrument/by_project_id/1238'
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body.decode('UTF-8'))
        self.assertEqual(len(answer.get('items')), 0)

    def test_files_for_transaction(self):
        """Return file listing for a transaction."""
        transaction_id = 67
        url = '/status/transactions/files/{0}'.format(transaction_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body.decode('UTF-8'))
        self.assertEqual(len(answer), 2)
        self.assertListEqual(sorted(answer.keys()),
                             sorted(loads(dumps(['103', '104']))))

    def test_transaction_for_id(self):
        """Return transaction info for a given id."""
        transaction_id = 68
        url = '/status/transactions/by_id/{0}'.format(transaction_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body.decode('UTF-8'))
        self.assertEqual(answer['_id'], 68)

        bad_transaction_id = 'bob'
        url = '/status/transactions/by_id/{0}'.format(bad_transaction_id)
        self.getPage(url)
        self.assertStatus('400 Invalid Request')
        self.assertInBody('Provide an appropriate transaction_id')

    def test_transaction_search(self):
        """Return projects for a specified user."""
        transaction_id = 68
        url = '/status/transactions/search?transaction={0}'.format(
            transaction_id)
        self.getPage(url)
        self.assertStatus('200 OK')

    def test_user_query(self):
        """Test user details retrieval."""
        user_id = 10
        url = '/status/users/by_id/{0}'.format(user_id)
        self.getPage(url)
        self.assertStatus('200 OK')

    def test_user_search(self):
        """Test user search functionality."""
        search_term = 'dmlb2001'
        url = '/status/users/search/{0}/simple'.format(search_term)
        self.getPage(url)
        self.assertStatus('200 OK')
        self.assertInBody('Brown')

        search_term = 'dmlb2004'
        url = '/status/users/search/{0}/simple'.format(search_term)
        self.getPage(url)
        self.assertStatus(404)

    def test_projects_by_user(self):
        """Return projects for a specified user."""
        user_id = 10
        url = '/status/projects/by_user_id/{0}'.format(user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body.decode('UTF-8'))
        self.assertEqual(len(answer), 2)

        user_id = 13
        url = '/status/projects/by_user_id/{0}'.format(user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        self.assertInBody('404 User Does Not Exist')

    def test_project_lookup(self):
        """Return an appropriate project for a specified project_id."""
        project_id = '1234a'
        url = '/status/projects/by_project_id/{0}'.format(project_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body.decode('UTF-8'))
        self.assertEqual(len(answer['instruments']), 1)
        self.assertEqual(answer['id'], project_id)

    def test_instrument_search(self):
        """Return appropriate instruments for a set of search criteria."""
        search_terms = 'nmr'
        user_id = 10
        url = '/status/instrument/search/{0}?user={1}'.format(
            search_terms, user_id)
        self.getPage(url)
        self.assertStatus('200 OK')

        user_id = 12
        url = '/status/instrument/search/{0}?user={1}'.format(
            search_terms, user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        self.assertBody('[]')

        user_id = 100
        url = '/status/instrument/search/{0}?user={1}'.format(
            search_terms, user_id)
        self.getPage(url)
        self.assertStatus('200 OK')

        search_terms = 'flux+capacitor'
        url = '/status/instrument/search/{0}?user={1}'.format(
            search_terms, user_id)
        self.getPage(url)
        self.assertStatus(404)

    def test_project_search(self):
        """Return appropriate projects for a search term and user id."""
        search_term = 'expired'
        user_id = 10  # admin user
        url = '/status/projects/search/{0}?user={1}'.format(
            search_term, user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body.decode('UTF-8'))
        self.assertEqual(len(answer), 2)

        search_term = None
        url = '/status/projects/search?user={0}'.format(user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body.decode('UTF-8'))
        self.assertEqual(len(answer), 2)

        search_term = 'pacifica'
        user_id = 100  # non admin user
        url = '/status/projects/search/{0}?user={1}'.format(
            search_term, user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body.decode('UTF-8'))
        self.assertEqual(len(answer), 1)

        search_term = 'bob'
        url = '/status/projects/search/{0}'.format(search_term)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body.decode('UTF-8'))
        self.assertEqual(len(answer), 0)

        search_term = 'bob'
        url = '/status/projects/search/{0}?user={1}'.format(
            search_term, user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body.decode('UTF-8'))
        self.assertEqual(len(answer), 0)

        url = '/status/projects/search?user={0}'.format(user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
        answer = loads(self.body.decode('UTF-8'))
        self.assertEqual(len(answer), 1)

        user_id = 10  # admin user
        search_term = 'nmr'
        url = '/status/instrument/search/{0}?user={1}'.format(
            search_term, user_id)
        self.getPage(url)
        self.assertStatus('200 OK')
