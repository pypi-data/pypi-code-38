# @TODO Remove in py3
from __future__ import print_function

import argparse
import os
import signal
import sys

import pyraftlog


def config_file_storage(must_exist):
    while True:
        # @TODO Convert to `input` in py3
        s_file = raw_input('Path to file: ')
        if not os.path.isfile(s_file):
            print('Not a file')
        elif must_exist and not os.path.exists(s_file):
            print('No such file')
        elif must_exist and os.path.getsize(s_file) == 0:
            print('Empty file')
        else:
            return s_file


def load_from_storage(s_type):
    print('Loading from storage')
    if s_type == 'pickle':
        s_file = config_file_storage(True)
        return pyraftlog.PickleStorage(s_file)
    if s_type == 'sqlite':
        s_file = config_file_storage(True)
        return pyraftlog.SQLiteStorage(s_file)
    return None


def load_to_storage(s_type):
    print('Loading to storage')
    if s_type == 'pickle':
        s_file = config_file_storage(False)
        return pyraftlog.PickleStorage(s_file)
    if s_type == 'sqlite':
        s_file = config_file_storage(False)
        return pyraftlog.SQLiteStorage(s_file)
    return None


def migrate():
    # Exit on SIGINT
    signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(signum))

    parser = argparse.ArgumentParser(description='Migrate between different storage types')
    parser.add_argument('name', help='Name of the consensus node')
    parser.add_argument('from_storage', choices=['pickle', 'sqlite'], help='Type of from storage')
    parser.add_argument('to_storage', choices=['pickle', 'sqlite'], help='Type of to storage')
    parser.add_argument('-f', '--force', action='store_true', default=False, help='Force overwrite to storage')
    args = parser.parse_args()

    # Load the from/to storage
    from_storage = load_from_storage(args.from_storage)
    to_storage = load_to_storage(args.to_storage)

    # Migrate from from_storage to to_storage
    if to_storage.migrate(pyraftlog.State(pyraftlog.STATE_ROLE_FOLLOWER, args.name), from_storage, args.force):
        print('Migration: success')
        return 0
    else:
        print('Migration: failure')
        return 1


if __name__ == '__main__':
    sys.exit(migrate())
