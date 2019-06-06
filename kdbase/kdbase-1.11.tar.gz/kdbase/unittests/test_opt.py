#!/usr/bin/env python
#-*-coding: utf-8 -*-

import unittest
import sys

sys.path.append('..')
from opt import *


class TestOpt(unittest.TestCase):
    
    def test_option(self):
        res = option()
        self.assertIsNotNone(res)

   
if __name__ == '__main__':
    unittest.main()
