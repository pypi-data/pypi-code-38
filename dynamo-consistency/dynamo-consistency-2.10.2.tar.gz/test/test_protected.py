#! /usr/bin/env python

import unittest

from dynamo_consistency import picker
from dynamo_consistency import main
from dynamo_consistency import history
from dynamo_consistency.backend import test

import base
import redefine_lister

test._FILES = sorted([
    ('/store/mc/ttThings/0000/qwert.root', 20),
    ('/store/mc/ttThings/0000/orphan.root', 20),
    ('/store/data/runC/RAW/0000/reg.root', 100),
    ('/store/data/runC/RAW/0000/orphan.root', 100),
    ('/store/data/runC/RAW/0000/empty', ),
    ])

test._INV = sorted([
    ('/store/mc/ttThings/0000/qwert.root', 20),
    ('/store/data/runC/RAW/0000/reg.root', 100),
    ('/store/data/runC/RAW/0000/missing.root', 100)
    ])


class TestProtected(base.TestBase):

    def do_more_setup(self):
        # Run the main program
        main.main(picker.pick_site())

    def test_removed(self):
        # Note that there's no RAW file here to delete
        self.assertEqual(history.orphan_files(main.config.SITE),
                         ['/store/mc/ttThings/0000/orphan.root'])

    def test_missing(self):
        # We do want to recover one of the files though
        self.assertEqual(history.missing_files(main.config.SITE),
                         ['/store/data/runC/RAW/0000/missing.root'])

    def test_empty(self):
        # Don't delete directories in the protected folders
        self.assertFalse(history.empty_directories(main.config.SITE))


if __name__ == '__main__':
    unittest.main(argv=base.ARGS)
