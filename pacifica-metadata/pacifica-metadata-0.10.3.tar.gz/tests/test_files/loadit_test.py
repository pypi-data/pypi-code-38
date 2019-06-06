#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This is used to generically load the test data."""
from os import getenv
from os.path import dirname, realpath, join
from json import loads
from pacifica.metadata.client import PMClient


def main():
    """Main method for loading the test data."""
    mdclient = PMClient(getenv('METADATA_URL', 'http://127.0.0.1:8121'))
    test_data_dir = dirname(realpath(__file__))
    object_order = [
        'analytical_tools',
        'journals',
        'citations',
        'institutions',
        'users',
        'contributors',
        'projects',
        'instruments',
        'transactions',
        'transsip',
        'transsap',
        'files',
        'groups',
        'keys',
        'relationships',
        'data_sources',
        'keywords',
        'values',
        'atool_transaction',
        'atool_project',
        'citation_contributor',
        'citation_keyword',
        'citation_project',
        'file_key_value',
        'institution_user',
        'instrument_user',
        'instrument_group',
        'project_group',
        'project_instrument',
        'project_user',
        'trans_key_value',
        'user_group',
        'transaction_user',
        'doi_authors',
        'doi_entries',
        'doi_info',
        'doi_transaction',
        'doi_author_mapping',
        'citation_transaction',
        'citation_doi',
        'instrument_data_source',
        'instrument_key_value'
    ]
    for obj in object_order:
        mdclient.create(obj, loads(
            open('{0}.json'.format(join(test_data_dir, obj))).read()))


if __name__ == '__main__':
    main()
