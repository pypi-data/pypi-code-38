#! /usr/bin/env python

# We were seeing directory deletions showing up twice in our log files (v2.5.0)
# This was reproduced in this test
# The cause was configuring both a parent and child logs

import unittest
import os
import shutil
import sys

argv = sys.argv[:]
sys.argv.extend(['--info'])

import base
from dynamo_consistency import opts

opts.V1 = True

from dynamo_consistency import backend
from dynamo_consistency.dynamo.v1 import registry

class Dummy(object):
    def __init__(self, _):
        pass
    @staticmethod
    def query(*_):
        pass
    @staticmethod
    def close():
        pass

backend.registry = registry
backend.registry._get_registry = Dummy
registry.transfer = lambda *_: ([], [])

from dynamo_consistency import logsetup
from dynamo_consistency import main
from dynamo_consistency import picker
from dynamo_consistency import summary


class TestLogs(unittest.TestCase):
    def setUp(self):
        for directory in ['logs', 'var']:
            if os.path.exists(directory):
                shutil.rmtree(directory)

    def tearDown(self):
        os.remove('logs/test.log')

    def test_duplog(self):
        summary.unlock_site('TEST_SITE')
        
        logsetup.change_logfile('logs/test.log')

        main.main(picker.pick_site('TEST_SITE'))

        summary.unlock_site('TEST_SITE')

        deletion_lines = 0

        with open('logs/test.log', 'r') as check:
            for line in check:
                if 'INFO:dynamo_consistency.dynamo.v1.registry: Deleting /store/data/runC/0000/emtpy/dir' in line:
                    deletion_lines += 1

        self.assertEqual(deletion_lines, 1)


if __name__ == '__main__':
    unittest.main(argv=base.ARGS)
