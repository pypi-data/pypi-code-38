#! /usr/bin/env python

import os
import unittest

from dynamo_consistency import picker
from dynamo_consistency import main
from dynamo_consistency import summary

import base

class TestForceUpdate(unittest.TestCase):
    def setUp(self):
        main.config.CONFIG = None
        summary.opts.UPDATESUMMARY = False
        if os.path.exists('www/stats.db'):
            os.remove('www/stats.db')
        self.conn = summary._connect()

    def tearDown(self):
        self.conn.close()
        os.environ.clear()

    def entry(self):
        return list(self.conn.execute('SELECT * FROM stats;'))

    def test_regular(self):
        main.main(picker.pick_site())
        self.assertTrue(self.entry())

    def test_noentry(self):
        os.environ['ListAge'] = '5'
        os.environ['InventoryAge'] = '5'

        main.main(picker.pick_site())
        self.assertFalse(self.entry())

    def test_forceentry(self):
        os.environ['ListAge'] = '5'
        os.environ['InventoryAge'] = '5'
        summary.opts.UPDATESUMMARY = True

        main.main(picker.pick_site())
        self.assertTrue(self.entry())


if __name__ == '__main__':
    unittest.main(argv=base.ARGS)
