#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the ORM interface CherryPyAPI."""
from time import time
from datetime import datetime
from json import dumps
import requests
from pacifica.metadata.orm.keys import Keys
from pacifica.metadata.orm.utils import datetime_now_nomicrosecond
from . import CPCommonTest


class TestCherryPyAPI(CPCommonTest):
    """Test the CherryPyAPI class."""

    __test__ = True

    def test_get_recursion_flags(self):
        """Test the recursion flags you can pass to get objects."""
        req = requests.get(
            '{0}/users?_id=10&recursion_limit=1'.format(self.url))
        self.assertEqual(req.status_code, 200)
        users = req.json()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['projects'], None)

        req = requests.get(
            '{0}/files?page_number=1&items_per_page=1&recursion_depth=0'.format(self.url))
        self.assertEqual(req.status_code, 200)
        files = req.json()
        self.assertEqual(len(files), 1)

        req = requests.get(
            '{0}/files?page_number=1&items_per_page=1&recursion_depth=4'.format(self.url))
        self.assertEqual(req.status_code, 500)

    def test_methods(self):
        """Test the PUT (insert) method."""
        set_hash = {'name': 'Renamed File', 'updated': None}
        req = requests.post('{0}/files'.format(self.url),
                            data=dumps(set_hash), headers=self.headers)
        self.assertEqual(req.status_code, 500)
        del set_hash['updated']
        set_hash['mtime'] = datetime.now().isoformat()
        req = requests.post('{0}/files'.format(self.url),
                            data=dumps(set_hash), headers=self.headers)
        self.assertEqual(req.status_code, 200)
        req = requests.get('{0}/files'.format(self.url))
        self.assertEqual(req.status_code, 200)
        files = req.json()
        self.assertEqual(len(files), 2)
        for file_hash in files:
            self.assertEqual(file_hash['name'], 'Renamed File')

        req = requests.get('{0}/files'.format(self.url))
        self.assertEqual(req.status_code, 200)
        files = req.json()
        self.assertEqual(len(files), 2)

        # update a foreign key to Keys obj that isn't there
        req = requests.post('{0}/file_key_value?file=103'.format(self.url),
                            data='{"key": 107}', headers=self.headers)
        self.assertEqual(req.status_code, 500)

        req = requests.put('{0}/file_key_value'.format(self.url),
                           data='{"key": 107, "file": 103, "value": 103}',
                           headers=self.headers)
        self.assertEqual(req.status_code, 500)

    # try changing updating something that works
        req = requests.post('{0}/file_key_value?file=103&key=103&value=103'.format(self.url),
                            data='{"key": 104, "file": 103, "value": 103}',
                            headers=self.headers)
        self.assertEqual(req.status_code, 200)

        # just try invalid json
        req = requests.post('{0}/keys'.format(self.url),
                            data='{ some bad json}', headers=self.headers)
        self.assertEqual(req.status_code, 400)
        req = requests.put('{0}/keys'.format(self.url),
                           data='{ some bad json}', headers=self.headers)
        self.assertEqual(req.status_code, 400)

        # insert one item
        req = requests.put('{0}/keys'.format(self.url),
                           data=dumps({
                               '_id': 1, 'key': 'blarg',
                               'created': datetime_now_nomicrosecond().isoformat()
                           }),
                           headers=self.headers)
        self.assertEqual(req.status_code, 200)

        # try inserting empty array
        req = requests.put('{0}/keys'.format(self.url),
                           data=dumps([]),
                           headers=self.headers)
        self.assertEqual(req.status_code, 200)

        # try to insert the same item again
        req = requests.put('{0}/keys'.format(self.url),
                           data=dumps({'_id': 1, 'key': 'blarg'}), headers=self.headers)
        self.assertEqual(req.status_code, 400)

        req = requests.post('{0}/keys?_id=107'.format(self.url),
                            data='{"_id": 142}', headers=self.headers)
        self.assertEqual(req.status_code, 500)

        # delete the item I just put in
        req = requests.delete('{0}/keys?key=blarg'.format(self.url))
        self.assertEqual(req.status_code, 200)

    def test_perf_of_large_insert(self):
        """Create 10000 records of Values and try to insert them."""
        values = []
        for j in range(0, 10):
            values.append([])
            for i in range(0, 1000):
                values[j].append(
                    {'_id': 20000 + i + (j * 1000), 'value': 'Value {0}'.format(i + (j * 1000))})
        txt_dumps = []
        for trans in values:
            txt_dumps.append(dumps(trans))
        start_time = time()
        for txt_trans in txt_dumps:
            req = requests.put('{0}/values'.format(self.url),
                               data=txt_trans, headers=self.headers)
            self.assertEqual(req.status_code, 200)
        end_time = time()
        self.assertTrue(end_time - start_time < 90)

    def test_set_or_create(self):
        """Test the internal set or create method."""
        key = {'_id': 4096, 'key': 'bigger'}
        obj = Keys()
        # pylint: disable=protected-access
        obj._set_or_create(key)
        keys = [{'_id': 4097, 'key': 'blah'}]
        obj._set_or_create(keys)
        obj._set_or_create(key)
        chk_obj = Keys.get_by_id(4096)
        self.assertEqual(chk_obj.id, 4096)
        chk_obj = Keys.get_by_id(4097)
        self.assertEqual(chk_obj.id, 4097)
        obj._meta.database.close()
        # pylint: enable=protected-access

    def test_status_url(self):
        """Test the root level status page."""
        resp = requests.get(self.url)
        self.assertEqual(resp.status_code, 200, 'Status code should be 200 OK')
        self.assertTrue('message' in resp.json(), 'Status should be object with message key.')
        self.assertEqual(resp.json()['message'], 'Pacifica Metadata Up and Running', 'message should be specific.')
