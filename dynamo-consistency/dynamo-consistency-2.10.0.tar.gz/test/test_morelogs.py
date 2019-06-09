#! /usr/bin/env python

import os
import shutil
import unittest

import dynamo_consistency
from dynamo_consistency import config
from dynamo_consistency import picker
from dynamo_consistency import main
from dynamo_consistency import history
from dynamo_consistency import summary
from dynamo_consistency.cms import unmerged

import base


unmerged.listdeletable.get_protected = lambda: [
    '/store/unmerged/protected',
    '/store/unmerged/protected2'
    ]
summary.is_debugged = lambda _: True


class TestMoreLogDeletions(unittest.TestCase):
    def setUp(self):
        for dirname in ['www', 'var']:
            if os.path.exists(dirname):
                shutil.rmtree(dirname)
        main.config.CONFIG = None
        dynamo_consistency.opts.UNMERGED = True
        dynamo_consistency.opts.MORELOGS = False

    def tearDown(self):
        history.RUN = None


    def test_nomore(self):
        site = picker.pick_site()
        main.main(site)
        unmerged = history.unmerged_files(site)
        self.assertFalse('/store/logs/prod/recent/test.tar.gz' in unmerged)
        self.assertFalse('/store/logs/prod/nope/test.tar.gz' in unmerged)

    def test_yesmore(self):
        dynamo_consistency.opts.MORELOGS = True
        site = picker.pick_site()
        main.main(site)
        unmerged = history.unmerged_files(site)
        self.assertTrue('/store/logs/prod/recent/test.tar.gz' in unmerged)
        self.assertFalse('/store/logs/prod/nope/test.tar.gz' in unmerged)

    def test_othersite(self):
        dynamo_consistency.opts.MORELOGS = True
        config.config_dict()
        config.CONFIG['AdditionalLogDeletions']['TEST_SITE2'] = config.CONFIG['AdditionalLogDeletions'].pop('TEST_SITE')
        site = picker.pick_site()

        main.main(site)
        self.assertTrue(history.orphan_files(site))
        unmerged = history.unmerged_files(site)
        self.assertFalse('/store/logs/prod/recent/test.tar.gz' in unmerged)
        self.assertFalse('/store/logs/prod/nope/test.tar.gz' in unmerged)


if __name__ == '__main__':
    unittest.main(argv=base.ARGS)
