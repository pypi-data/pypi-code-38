#! /usr/bin/env python

# Test the unmerged configuration

import os
import sys
import shutil
import unittest

from dynamo_consistency.cms import unmerged
from dynamo_consistency.backend.test import TMP_DIR
from dynamo_consistency.backend import registry

import base
import redefine_lister


unmerged.listdeletable.get_protected = lambda: [
    '/store/unmerged/protected',
    '/store/unmerged/protected2'
    ]


class TestUnmerged(base.TestListing):
    file_list = [
        ('/store/unmerged/protected/000/qwert.root', 20),
        ('/store/unmerged/notprot/000/qwert.root', 20),
        ('/store/unmerged/logs/000/logfile.tar.gz', 20),
        ('/store/unmerged/ignore/RAW/000/file.root', 20)
        ]

    dir_list = [
        '/store/unmerged/ignore/RAW/empty',
        '/store/unmerged/protected/empty',
        '/store/unmerged/protected2',
        ]

    def do_more_setup(self):
        super(TestUnmerged, self).do_more_setup()

        registry._reset()

        for name in self.dir_list:
            path = os.path.join(TMP_DIR, name[7:])
            if not os.path.exists(path):
                os.makedirs(path)
                os.utime(path, (1000000000, 1000000000))
                os.utime('/'.join(path.split('/')[:-1]), (1000000000, 1000000000))

    def test_deletion_file(self):
        unmerged.clean_unmerged('test')
        self.assertEqual(registry.deleted,
                         sorted(['/store/unmerged/notprot/000/qwert.root',
                                 '/store/unmerged/logs/000/logfile.tar.gz'
                                 ]))

        with open('var/cache/test/protectedLFNs.txt', 'r') as checklist:
            self.assertEqual(len(list(checklist)), 2)

    def test_deletion_dir(self):
        path = os.path.join(TMP_DIR, 'unmerged/notprotected/by/anything')
        os.makedirs(path)
        os.utime(path, (1000000000, 1000000000))
        os.utime('/'.join(path.split('/')[:-1]), (1000000000, 1000000000))
        os.utime('/'.join(path.split('/')[:-2]), (1000000000, 1000000000))

        unmerged.clean_unmerged('test')
        self.assertEqual(registry.deleted,
                         sorted(['/store/unmerged/notprot/000/qwert.root',
                                 '/store/unmerged/logs/000/logfile.tar.gz',
                                 '/store/unmerged/notprotected/by/anything',
                                 '/store/unmerged/notprotected/by',
                                 '/store/unmerged/notprotected',
                                 ]))


class TestSetup(unittest.TestCase):
    def test_tmpdir(self):
        # Make sure these are the same
        self.assertEqual(TMP_DIR, base.TMP_DIR)


if __name__ == '__main__':
    unittest.main(argv=[a for a in sys.argv if a not in ['--info', '--debug']])
