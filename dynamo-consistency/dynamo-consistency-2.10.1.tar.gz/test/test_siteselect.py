#! /usr/bin/env python

import os
import shutil
import unittest

from dynamo_consistency import config
from dynamo_consistency import summary
from dynamo_consistency import picker
from dynamo_consistency.backend.test import siteinfo


class TestSelection(unittest.TestCase):
    def setUp(self):
        webdir = config.config_dict()['WebDir']        
        if os.path.exists(webdir):
            shutil.rmtree(webdir)

        # This fills the database with sites
        picker.pick_site()


    def test_works(self):
        self.assertEqual(sorted(summary.get_sites()),
                         sorted(siteinfo.site_list()))

    def test_flag(self):
        self.assertFalse(summary.get_sites(True))

    def test_act(self):
        summary.set_reporting('TEST_SITE', summary.ACT)
        self.assertEqual(summary.get_sites(True),
                         ['TEST_SITE'])
        summary.set_reporting('BAD_SITE', summary.ACT)
        self.assertEqual(sorted(summary.get_sites()),
                         sorted(siteinfo.site_list()))


if __name__ == '__main__':
    unittest.main()
