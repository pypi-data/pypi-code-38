#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import unittest
import configparser
from goss.app import utils

class TestMain(unittest.TestCase):

    def setUp(self):
        '''before each test function'''
        pass

    def tearDown(self):
        '''after each test function'''
        pass

    def do(self, func):
        '''todo'''
        self.assertEqual(1, 1)
        pass

    def test_config(self):
        filepath = '/tmp/goss/config'
        utils.config(filepath, 'user', name='wxnacy')
        conf = configparser.ConfigParser()
        conf.read(filepath)
        self.assertEqual(conf['user']['name'], 'wxnacy')
        utils.config(filepath, 'user', name='wxnacy1', email='wxnacy@gmail.com')
        conf = configparser.ConfigParser()
        conf.read(filepath)
        self.assertEqual(conf['user']['name'], 'wxnacy1')
        self.assertEqual(conf['user']['email'], 'wxnacy@gmail.com')

if __name__ == "__main__":
    unittest.main()
