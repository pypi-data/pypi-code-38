#! /usr/bin/env python

import os
import shutil
import sys
import unittest

import base

from dynamo_consistency import main
from dynamo_consistency import picker
from dynamo_consistency import history
from dynamo_consistency import config

class TestNoOrphanMain(unittest.TestCase):
    def setUp(self):
        config.CONFIG = None
        config.LOCATION = 'consistency_config.json'
        main.opts.NOORPHAN = False
        for dirname in ['www', 'var']:
            if os.path.exists(dirname):
                shutil.rmtree(dirname)

        main.registry.deleted = []

    def run_main(self):
        main.main(picker.pick_site())

        self.assertEqual(history.missing_files(main.config.SITE),
                         ['/store/data/runB/0003/missing.root'])
        self.assertFalse(history.orphan_files(main.config.SITE))
        self.assertEqual(history.empty_directories(main.config.SITE),
                         ['/store/data/runC/0000/emtpy/dir',
                          '/store/data/runC/0000/emtpy',
                          '/store/data/runC/0000',
                          '/store/data/runC'])

        self.assertEqual(sorted(main.registry.deleted, reverse=True),
                         history.empty_directories(main.config.SITE))

    def test_flag(self):
        main.opts.NOORPHAN = True

        self.run_main()

    def test_config(self):
        config.LOCATION = 'txtfiles/no_orphan_config.json'

        self.run_main()


if __name__ == '__main__':
    unittest.main(argv=base.ARGS)
