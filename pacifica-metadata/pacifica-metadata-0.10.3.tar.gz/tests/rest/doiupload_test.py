#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the ORM interface DOIUpload."""
from __future__ import print_function
from json import loads
from os.path import realpath
import requests
from . import CPCommonTest


class TestDOIUploadAPI(CPCommonTest):
    """Test the DOIUploadAPI class."""

    __test__ = True

    def test_doiupload_api(self):
        """Test the POST method."""
        header_list = {'Content-Type': 'application/json'}
        entry_path = realpath('test_files')
        entry_data = loads(open(
            '{0}/{1}.json'.format(
                entry_path,
                'doiupload_api'
            )
        ).read())

        self._setup_released_transaction()

        req = requests.post(
            url='{0}/doiupload/new_entry'.format(self.url),
            json=entry_data,
            headers=header_list
        )
        self.assertEqual(req.status_code, 200)

        # test for unreleased transaction_id
        entry_data['doi'] = entry_data['doi'].replace('.67', '.68')
        entry_data['meta']['doi_infix'] = entry_data['meta']['doi_infix'].replace(
            '.67', '.68')
        entry_data['meta']['site_url'] = entry_data['meta']['site_url'].replace(
            '/67', '/68')

        req = requests.post(
            url='{0}/doiupload/new_entry'.format(self.url),
            json=entry_data,
            headers=header_list
        )
        self.assertEqual(req.status_code, 400)
        self.assertTrue('has not been released' in req.text)

    def test_doi_entry_mod_time_update(self):
        """Test the method for touching a DOI Entry to update its modification time."""
        entry_path = realpath('test_files')
        entry_data = loads(open(
            '{0}/{1}.json'.format(
                entry_path,
                'doi_entries'
            )
        ).read())
        print(entry_data)
        doi_string = [entry_data[0]['doi']]
        header_list = {'Content-Type': 'application/json'}
        req = requests.post(
            url='{0}/doiupload/update_modified_time'.format(self.url),
            json=doi_string,
            headers=header_list
        )
        self.assertEqual(req.status_code, 200)
        self.assertTrue('"num_records_updated": 1' in req.text)

    def test_osti_update(self):
        """Test the POST method for information updates."""
        path = realpath('test_files')
        update_data = open(
            '{0}/{1}.xml'.format(
                path,
                'osti_update'
            )
        ).read()

        header_list = {'Content-Type': 'application/xml'}
        req = requests.post(
            url='{0}/doiupload/update'.format(self.url),
            data=update_data,
            headers=header_list
        )

        self.assertEqual(req.status_code, 200)

        update_data = open(
            '{0}/{1}.xml'.format(
                path,
                'osti_update_missing_trans'
            )
        ).read()

        req = requests.post(
            url='{0}/doiupload/update'.format(self.url),
            data=update_data,
            headers=header_list
        )

        self.assertEqual(req.status_code, 404)

        # Process return with no records
        update_data = open(
            '{0}/{1}.xml'.format(
                path,
                'osti_update_empty'
            )
        ).read()

        req = requests.post(
            url='{0}/doiupload/update'.format(self.url),
            data=update_data,
            headers=header_list
        )

        self.assertEqual(req.status_code, 404)

        # Process invalid XML doc
        update_data = open(
            '{0}/{1}.xml'.format(
                path,
                'osti_update_bad'
            )
        ).read()

        req = requests.post(
            url='{0}/doiupload/update'.format(self.url),
            data=update_data,
            headers=header_list
        )
        self.assertEqual(req.status_code, 400)

        # Process invalid XML doc
        update_data = open(
            '{0}/{1}.xml'.format(
                path,
                'osti_update_bad'
            )
        ).read()

        header_list = {'Content-Type': 'application/json'}
        req = requests.post(
            url='{0}/doiupload/update'.format(self.url),
            data=update_data,
            headers=header_list
        )
        self.assertEqual(req.status_code, 415)
