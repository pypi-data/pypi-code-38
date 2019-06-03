#!/usr/bin/env python
"""
A utility to create a Girder hierarchy from metadata.json.

Useful in testing the monkeybrains plugin to set up a hierarchy,
then set_metadata.py can be run to add the metadata.
"""

import argparse
import json

import requests.packages.urllib3

from girder_client import GirderClient

requests.packages.urllib3.disable_warnings()


parser = argparse.ArgumentParser(
    prog='create_tree_from_metadata',
    description='Create a hierarchy in girder from the metadata.json.')
parser.add_argument('--username', required=False, default=None)
parser.add_argument('--password', required=False, default=None)
parser.add_argument('--parent-folder-id', required=True, default=None)
parser.add_argument('--scheme', required=False, default=None)
parser.add_argument('--host', required=False, default=None)
parser.add_argument('--port', required=False, default=None)


def main():
    """Create the folder hierarchy with metadata in a Girder instance."""
    args = parser.parse_args()
    g = GirderClient(host=args.host, port=args.port, scheme=args.scheme)
    g.authenticate(args.username, args.password)

    def create_folder_on_demand(parent_folder_id, folder_name):
        existing_folders = list(
            g.listFolder(parent_folder_id, name=folder_name))
        if not len(existing_folders):
            sought_folder = g.createFolder(parent_folder_id, name=folder_name)
        else:
            sought_folder = existing_folders[0]
        return sought_folder

    metadata_file = 'metadata.json'
    with open(metadata_file) as json_file:
        metadata = json.load(json_file)
    parent_folder_id = args.parent_folder_id

    for subject_id, subject_metadata in metadata.items():
        subject_folder = create_folder_on_demand(parent_folder_id, subject_id)
        for (scan_time, scan_date, scan_weight) in subject_metadata['scans']:
            create_folder_on_demand(subject_folder['_id'], scan_time)

if __name__ == '__main__':
    main()
