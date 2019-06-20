###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
@author: Stefan-Gabriel CHITIC
'''

import unittest

from lbCVMFSTools.Injector import Injector, inject, injector


class totoInterface():
    def printer(self):
        return "totoInterface"


class toto(totoInterface):
    def printer(self):
        return "toto"


class nonToto(object):
    pass


@inject(iface=toto)
class testInjection():
    def __init__(self, iface=None):
        self.iface = iface

    def printer(self):
        if self.iface:
            return self.iface.printer()
        return None



class TestInjector(unittest.TestCase):

    def setUp(self):
        self.obj = Injector()

    def tearDown(self):
        pass

    def test_provide(self):
        self.assertRaises(AssertionError, self.obj.provide, totoInterface,
                          nonToto)
        self.obj.provide(totoInterface, toto)

    def test_provide_instance(self):
        t = toto()
        nt = nonToto()
        self.assertRaises(AssertionError, self.obj.provide_instance,
                          totoInterface, nt)
        self.obj.provide_instance(totoInterface, t)

    def test_get_instance(self):
        t1 = toto()
        self.obj.provide(totoInterface, toto)
        # Check if the injector returns the implementation
        t = isinstance(self.obj.get_instance(totoInterface), toto)
        self.assertTrue(t)
        self.assertEqual(self.obj.get_instance(totoInterface).__class__,
                         t1.__class__)

    def test_str(self):
        self.assertEqual(str(self.obj), '<injector>')

    def test_injection(self):
        injector.provide(totoInterface, toto)
        t = testInjection()
        self.assertEqual(t.printer(), 'toto')


if __name__ == "__main__":

    unittest.main()
