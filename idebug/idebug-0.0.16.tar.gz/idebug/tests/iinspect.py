
from idebug import *
from idebug.tests.iinspect import *

import unittest



#@unittest.skip("showing class skipping")
class DummyClassTestCase(unittest.TestCase):

    #@unittest.skip("demonstrating skipping")
    def test__dummy(self):
        d = DummyClass('param1','param2')
        d.dummy()


def main():
    unittest.main()
