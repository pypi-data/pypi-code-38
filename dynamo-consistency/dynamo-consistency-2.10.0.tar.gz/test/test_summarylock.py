#! /usr/bin/env python

import os
import shutil
import unittest
import threading
from time import sleep

from dynamo_consistency import summary
from dynamo_consistency import picker
from dynamo_consistency.summary import _connect

class TestSummary(unittest.TestCase):
    def setUp(self):
        for dirname in ['www', 'var']:
            if os.path.exists(dirname):
                shutil.rmtree(dirname)
        summary.unlock_site(picker.pick_site())

    def test_site(self):
        conn = _connect()

        self.assertEqual(list(conn.execute("SELECT site, isgood FROM sites WHERE site = 'TEST_SITE'")),
                         [('TEST_SITE', 0)])

        updater = threading.Thread(target=lambda: os.system('set-status TEST_SITE act'))
        updater.start()

        sleep(3)
        self.assertEqual(list(conn.execute("SELECT site, isgood FROM sites WHERE site = 'TEST_SITE'")),
                         [('TEST_SITE', 0)])
        conn.close()
        updater.join()

        conn = _connect()
        self.assertEqual(list(conn.execute("SELECT site, isgood FROM sites WHERE site = 'TEST_SITE'")),
                         [('TEST_SITE', 1)])
        conn.close()


if __name__ == '__main__':
    unittest.main()
