#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the ORM interface IngestAPI."""
import os
from json import dumps, loads
import requests
from pacifica.metadata.rest.ingest import IngestAPI
from . import CPCommonTest


class TestIngestAPI(CPCommonTest):
    """Test the CherryPyAPI class."""

    __test__ = True

    def test_valid_file_data(self):
        """Test the validate hash and mimetype functions."""
        good_file = {
            'mimetype': 'text/xml',
            'hashsum': 'da39a3ee5e6b4b0d3255bfef95601890afd80709',
            'hashtype': 'sha1'
        }
        self.assertTrue(IngestAPI.validate_file_meta(good_file))
        bad_mimetype = {
            'mimetype': 'bad_mimetype'
        }
        self.assertFalse(IngestAPI.validate_file_meta(bad_mimetype))
        bad_hash_algo = {
            'mimetype': 'text/xml',
            'hashtype': 'abcd',
            'hashsum': 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
        }
        self.assertFalse(IngestAPI.validate_file_meta(bad_hash_algo))
        hash_not_hex = {
            'mimetype': 'text/xml',
            'hashtype': 'sha1',
            'hashsum': 'da39a3ee5e6b4b0d3255bfef95601890afd80709deadbeez'
        }
        self.assertFalse(IngestAPI.validate_file_meta(hash_not_hex))
        bad_hash_len = {
            'mimetype': 'text/xml',
            'hashtype': 'sha1',
            'hashsum': 'da39a3ee5e6b4b0d3255bfef95601890afd80709deadbeef'
        }
        self.assertFalse(IngestAPI.validate_file_meta(bad_hash_len))

    def test_ingest_api(self):
        """Test the PUT (insert) method."""
        putdata = [
            {'destinationTable': 'Transactions._id', 'value': 1234},
            {'destinationTable': 'Transactions.submitter', 'value': 10},
            {'destinationTable': 'Transactions.project', 'value': '1234a'},
            {'destinationTable': 'Transactions.instrument', 'value': 54},
            {
                'destinationTable': 'TransactionKeyValue',
                'key': 'Temp C',
                'value': '27'
            },
            {
                'destinationTable': 'TransactionKeyValue',
                'key': 'Temp F',
                'value': '27'
            },
            {
                'destinationTable': 'TransactionKeyValue',
                'key': 'Tag',
                'value': 'foo'
            },
            {
                'destinationTable': 'Files',
                '_id': 34, 'name': 'foo.txt', 'subdir': 'a/b/',
                'ctime': 'Tue Nov 29 14:09:05 PST 2016',
                'mtime': 'Tue Nov 29 14:09:05 PST 2016',
                'size': 128, 'mimetype': 'text/plain',
                'hashtype': 'sha1',
                'hashsum': 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
            },
            {
                'destinationTable': 'FileKeyValue',
                'key': 'Micronic Adjustment',
                'value': '5.66%',
                'file_id': 34
            },
            {
                'destinationTable': 'Files',
                '_id': 35, 'name': 'bar.txt', 'subdir': 'a/b/',
                'ctime': 'Tue Nov 29 14:09:05 PST 2016',
                'mtime': 'Tue Nov 29 14:09:05 PST 2016',
                'size': 47, 'mimetype': 'text/plain',
                'hashtype': 'sha1',
                'hashsum': 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
            },
        ]
        req = requests.put(
            '{0}/ingest'.format(self.url), data=dumps(putdata), headers={'content-type': 'application/json'})
        self.assertEqual(req.text, '{"status": "success"}')
        self.assertEqual(req.status_code, 200)

        putdata[0]['value'] += 1
        putdata[7]['_id'] += 10
        putdata[8]['file_id'] += 10
        putdata[9]['_id'] += 10
        # notifications url shouldn't be listening
        # however accepting the data should be okay
        os.environ['NOTIFICATIONS_URL'] = 'http://127.0.0.1:8070'
        req = requests.put(
            '{0}/ingest'.format(self.url), data=dumps(putdata), headers={'content-type': 'application/json'})
        self.assertEqual(req.text, '{"status": "success"}')
        self.assertEqual(req.status_code, 200)

        # generate bad file metadata
        putdata[0]['value'] += 1
        putdata[7]['hashtype'] = ''
        req = requests.put(
            '{0}/ingest'.format(self.url), data=dumps(putdata), headers={'content-type': 'application/json'})
        self.assertTrue('traceback' in loads(req.text))
        self.assertTrue('ValueError' in loads(req.text)['traceback'])
        self.assertEqual(req.status_code, 500)
