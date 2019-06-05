#! /usr/bin/env python

import os
import shutil
import unittest

import base

from dynamo_consistency import config
from dynamo_consistency.backend import redirectors

config.config_dict()
config.CONFIG['GlobalRedirectors'] = []
redirectors.get_domain = lambda _: 'example.com'

class TestRedirectors(unittest.TestCase):
    def setUp(self):
        if os.path.exists('var'):
            shutil.rmtree('var')

        self.file_name = os.path.join(config.vardir('redirectors'), 'TEST_SITE_redirector_list.txt')

    def test_empty(self):
        redirector, doors = redirectors.get_redirector('TEST_SITE')
        self.assertFalse(redirector)
        self.assertFalse(doors)

        self.assertFalse(os.path.exists(self.file_name))

    def test_list(self):
        with open(self.file_name, 'w') as redlist:
            redlist.write('test.example.com\n')

        redirector, doors = redirectors.get_redirector('TEST_SITE')
        self.assertFalse(redirector)
        self.assertEqual(doors, ['test.example.com'])


if __name__ == '__main__':
    unittest.main(argv=base.ARGS)
