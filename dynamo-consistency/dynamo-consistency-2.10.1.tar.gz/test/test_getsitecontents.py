#! /usr/bin/env python

import os
import sys
import re
import socket
import unittest
import logging
import time

from dynamo_consistency import remotelister
from dynamo_consistency import datatypes
from dynamo_consistency import config

def my_ls(path, location='/mnt/hadoop/cms/store'):

    full_path = os.path.join(location, path)

    if not os.path.exists(full_path):
        return True, [], []

    results = [os.path.join(full_path, res) for res in os.listdir(full_path)]

    dirs  = [(os.path.basename(name), os.stat(name).st_mtime) for \
                 name in filter(os.path.isdir, results)]
    files = [(os.path.basename(name), os.stat(name).st_size, os.stat(name).st_mtime) for \
                 name in filter(os.path.isfile, results)]

    return True, dirs, files

class TestT3Listing(unittest.TestCase):

    def test_xrd_on_t3(self):

        remote_tree = remotelister.listing('T3_US_MIT')

        local_listing = datatypes.DirectoryInfo(
            '/store', directories=[
                datatypes.create_dirinfo('', subdir, my_ls) for \
                    subdir in config.config_dict().get('DirectoryList', [])
                ])

        local_listing.setup_hash()

        print '='*30
        local_listing.display()
        print '='*30
        remote_tree.display()

        self.assertEqual(local_listing.hash, remote_tree.hash)

if __name__ == '__main__':

    # no test for now
    exit(0)

    if len(sys.argv) > 1:
        start = time.time()

        if 'info' in sys.argv:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.DEBUG)

        tree = remotelister.listing(sys.argv[1])
        tree.display()

        print '\nDuration: %f seconds\n' % (time.time() - start)

    else:
        if re.match(r'T3DESK\d{3}.MIT.EDU', socket.getfqdn()):
            unittest.main()
