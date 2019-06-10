#! /usr/bin/env python

import os
import sys
import unittest

from dynamo_consistency import config

config.LOCATION = 'locktest.json'

from dynamo_consistency import picker

picker.siteinfo.site_list = lambda: ['TEST_SITE', 'BAD_SITE', 'GFAL_SITE']
picker.siteinfo.ready_list = lambda: ['TEST_SITE', 'GFAL_SITE']
picker.check_site = lambda site: site in picker.siteinfo.ready_list()


import base


class TestLockSelection(unittest.TestCase):
    def setUp(self):
        os.remove(os.path.join(os.path.dirname(__file__), 'www', 'stats.db'))

    def test_normal(self):
        self.assertEqual(picker.pick_site('TEST'), 'TEST_SITE')
        self.assertEqual(picker.pick_site('GFAL'), 'GFAL_SITE')
        self.assertRaises(picker.NoMatchingSite, picker.pick_site, 'BAD')

    def test_gfal(self):
        self.assertRaises(picker.NoMatchingSite, picker.pick_site, 'TEST', 'gfal')
        self.assertEqual(picker.pick_site('GFAL', 'gfal'), 'GFAL_SITE')

    def test_nolock(self):
        self.assertEqual(picker.pick_site('TEST', ''), 'TEST_SITE')
        self.assertRaises(picker.NoMatchingSite, picker.pick_site, 'GFAL', '')

    def test_getgfal(self):
        self.assertEqual(picker.pick_site(lockname='gfal'), 'GFAL_SITE')

    def test_getnolock(self):
        self.assertEqual(picker.pick_site(lockname=''), 'TEST_SITE')


if __name__ == '__main__':
    unittest.main(argv=base.ARGS)
