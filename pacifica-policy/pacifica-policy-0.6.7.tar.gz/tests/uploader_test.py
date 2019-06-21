#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the uploader policy."""
from __future__ import print_function
from json import dumps, loads
from cherrypy.test import helper
from pacifica.policy.uploader.rest import UploaderPolicy
from common_test import CommonCPSetup


class TestUploaderPolicy(helper.CPWebCase, CommonCPSetup):
    """Test the uploader policy service."""

    PORT = 8181
    HOST = '127.0.0.1'
    headers = [('Content-Type', 'application/json')]

    queries = {
        'user_query': {
            'query': {
                'user': -1,
                'from': 'users',
                'columns': ['last_name', 'first_name'],
                'where': {'network_id': 'dmlb2001'}
            },
            'answer': [
                {
                    'last_name': u'Brown\u00e9 Jr',
                    'first_name': u'David\u00e9'
                }
            ]
        },
        'user_query_no_where': {
            'query': {
                'user': 100,
                'from': 'users',
                'columns': ['last_name', 'first_name'],
                'where': {}
            },
            'answer': [
                {
                    'last_name': u'Brown\u00e9 Jr',
                    'first_name': u'David\u00e9'
                }
            ]
        },
        'user_query_with_project': {
            'query': {
                'user': 100,
                'from': 'users',
                'columns': ['last_name', 'first_name'],
                'where': {'project_id': '1234a', 'user': 10}
            },
            'answer': [
                {
                    'last_name': u'Brown\xe9 Jr',
                    'first_name': u'David\xe9'
                }
            ]
        },
        'project_query': {
            'query': {
                'user': 10,
                'from': 'projects',
                'columns': ['_id', 'title'],
                'where': {'project_id': '1234a'}
            },
            'answer': [
                {
                    '_id': '1234a',
                    'title': u'Pacifica D\xe9velopment (active no close)'
                }
            ]
        },
        'project_query_not_admin': {
            'query': {
                'user': 100,
                'from': 'projects',
                'columns': ['_id', 'title'],
                'where': {'project_id': u'1234b\u00e9'}
            },
            'answer': [
                {
                    '_id': u'1234b\u00e9',
                    'title': u'Pacifica D\xe9velopment'
                }
            ]
        },
        'project_query_user': {
            'query': {
                'user': 100,
                'from': 'projects',
                'columns': ['_id', 'title'],
                'where': {'_id': '1234a'}
            },
            'answer': [
                {
                    '_id': '1234a',
                    'title': u'Pacifica D\xe9velopment (active no close)'
                }
            ]
        },
        'project_query_admin': {
            'query': {
                'user': 10,
                'from': 'projects',
                'columns': ['_id', 'title'],
                'where': {'_id': '1234a'}
            },
            'answer': [
                {
                    '_id': '1234a',
                    'title': u'Pacifica D\xe9velopment (active no close)'
                }
            ]
        },
        'project_query_with_instruments': {
            'query': {
                'user': 11,
                'from': 'projects',
                'columns': ['_id', 'title'],
                'where': {'instrument_id': 74}
            },
            'answer': [
                {
                    '_id': u'1234c\u00e9',
                    'title': u'Pacifica D\xe9velopment (Alt)',
                }
            ]
        },
        'project_query_for_user': {
            'query': {
                'user': 10,
                'from': 'projects',
                'columns': ['_id', 'title'],
                'where': {}
            },
            'answer': [
                {
                    '_id': '1234a',
                    'title': u'Pacifica D\xe9velopment (active no close)'
                }
            ]
        },
        'project_query_for_non_admin_no_group': {
            'query': {
                'user': 100,
                'from': 'projects',
                'columns': ['_id', 'title'],
                'where': {'instrument_id': 75}
            },
            'answer': [
                {
                    '_id': u'1234b\u00e9',
                    'title': u'Pacifica D\xe9velopment'
                }
            ]
        },
        'instrument_query': {
            'query': {
                'user': 100,
                'from': 'instruments',
                'columns': ['_id', 'name'],
                'where': {}
            },
            'answer': [
                {
                    '_id': 54,
                    'name': u'NMR PROBES: Nittany Liquid Prob\xe9s'
                }
            ]
        },
        'instrument_query_with_id': {
            'query': {
                'user': 100,
                'from': 'instruments',
                'columns': ['_id', 'name'],
                'where': {'_id': 54}
            },
            'answer': [
                {
                    '_id': 54,
                    'name': u'NMR PROBES: Nittany Liquid Prob\xe9s'
                }
            ]
        },
        'instrument_query_from_project': {
            'query': {
                'user': 10,
                'from': 'instruments',
                'columns': ['_id', 'name'],
                'where': {'project_id': '1234a'}
            },
            'answer': [
                {
                    '_id': 54,
                    'name': u'NMR PROBES: Nittany Liquid Prob\xe9s'
                }
            ]
        },
        'instrument_query_from_project_bad': {
            'query': {
                'user': 100,
                'from': 'instruments',
                'columns': ['_id', 'name'],
                'where': {'project_id': '1234a'}
            },
            'answer': [
                {
                    '_id': 54,
                    'name': u'NMR PROBES: Nittany Liquid Prob\xe9s'
                }
            ]
        }
    }

    def test_queries(self):
        """Test posting the queries."""
        for title, value in self.queries.items():
            print(title)
            self.getPage('/uploader',
                         self.headers +
                         [('Content-Length', str(len(dumps(value['query']))))],
                         'POST',
                         dumps(value['query']))
            self.assertStatus('200 OK')
            self.assertHeader('Content-Type', 'application/json')
            if loads(self.body.decode('UTF-8')):
                answer = loads(self.body.decode('UTF-8'))
                if '_id' in answer[0]:
                    answer = sorted(answer, key=lambda i: i['_id'])
                answer = answer[0]
                for akey, avalue in value['answer'][0].items():
                    self.assertTrue(akey in answer)
                    self.assertEqual(avalue, answer[akey])
            else:
                self.assertEqual(len(loads(self.body.decode('UTF-8'))), 0)

    def test_bad_query(self):
        """Try to throw a bad query at the query select method."""
        upolicy = UploaderPolicy()
        hit_exception = False
        try:
            # pylint: disable=protected-access
            upolicy._query_select({})
            # pylint: enable=protected-access
        except KeyError:
            hit_exception = True
        self.assertTrue(hit_exception)
        hit_exception = False
        try:
            bad_query = {
                'user': 100,
                'from': 'foo',
                'where': {}
            }
            # pylint: disable=protected-access
            upolicy._query_select(bad_query)
            # pylint: enable=protected-access
        except TypeError:
            hit_exception = True
        self.assertTrue(hit_exception)

        bad_queries = [
            {
                'user': 'abcd'
            },
            {
                'user': 'abcd',
                'from': 'users',
                'columns': ['first_name'],
                'where': {'no_such_column': 'foo'}
            },
            {
                'user': 10,
                'from': 'foobar',
                'columns': ['first_name'],
                'where': {'network_id': 'foo'}
            }
        ]
        for bad_query in bad_queries:
            self.getPage('/uploader',
                         self.headers +
                         [('Content-Length', str(len(dumps(bad_query))))],
                         'POST',
                         dumps(bad_query))
            self.assertStatus('500 Internal Server Error')
            hit_exception = False
            try:
                loads(self.body.decode('UTF-8'))
            except ValueError:  # pragma no cover
                hit_exception = True
            self.assertFalse(hit_exception)

        # pylint: disable=protected-access
        self.assertFalse(upolicy._valid_query({'foo': 'bar'}))
        self.assertFalse(upolicy._valid_query({'user': 'bar', 'from': 'baz'}))
        # pylint: enable=protected-access
