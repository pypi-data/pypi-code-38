#! /usr/bin/env python

"""
This is just to make sure the configuration documentation is
up to date and consistent between the .yml and .json examples
"""

import unittest
import json
import yaml
import re
import os

from dynamo_consistency import config

class TestConfiguration(unittest.TestCase):
    def setUp(self):
        config.CONFIG_FILE = os.path.join(os.path.dirname(__file__),
                                          'config.yml')
        config.LOADER = yaml
        self.yml_config = config.config_dict()

    def test_configs_are_same(self):
        self.maxDiff = None

        config.LOADER = json

        # Test the example, and also the T2 production for now.
        for config_file in ['consistency_config.json', '../prod/consistency_config.json']:

            config.CONFIG_FILE = os.path.join(os.path.dirname(__file__),
                                          config_file)
            json_config = config.config_dict()

            for key in json_config.keys():
                self.assertTrue(str(key) in self.yml_config.keys())

            for key in self.yml_config.keys():
                self.assertTrue(unicode(key) in json_config.keys(),
                                '%s not in %s' % (key, json_config.keys()))

    def test_is_documented(self):
        for key in self.yml_config.keys():
            with open(config.CONFIG_FILE) as config_file:
                # Make sure the key is documented in the comments
                self.assertTrue(True in [bool(re.match(r'^#.*\*\*%s\*\*' % key, line)) for line in config_file],
                                'Key %s not found' % key)


if __name__ == '__main__':
    unittest.main()
