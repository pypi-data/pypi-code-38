# coding: utf-8
from __future__ import absolute_import

import doctest
import unittest

from django.test import TestCase

from . import tools


class MainTest(TestCase):
    def test_workspace(self):
        pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(tools))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(MainTest))
    return suite
