import unittest

import sys
import inspect
import pprint
pp = pprint.PrettyPrinter(indent=2)
from datetime import datetime


class LoopReporterTestCase(unittest.TestCase):

    def test_valid_LoopReporter(self):
        l = LoopReporter(title='test_LoopReporter', len=10)
        for i in list(range(100)):
            l.report()

    def test_invalid_LoopReporter(self):
        l = LoopReporter(title='test_LoopReporter', len=100)
        l.count = 101
        self.assertEqual(l.report(), None)


#class PrintConvertedTimeunitTestCase(unittest.TestCase):

    def test_valid_timeunit(self):
        print('\n\n')
        self.assertEqual(print_converted_timeunit('test', 0.01), 'msec')
        self.assertEqual(print_converted_timeunit('test', 3), 'secs')
        self.assertEqual(print_converted_timeunit('test', 69), 'mins')
        self.assertEqual(print_converted_timeunit('test', 3500), 'mins')
        self.assertEqual(print_converted_timeunit('test', 60*60*9), 'hrs')
        self.assertEqual(print_converted_timeunit('test', 60*60*24+456), 'hrs')



    def test_funcname(a='a', b='b'):
        #fn = dbg.funcinit(inspect.currentframe())
        #dbg.funcfin(fn)
        f = FuncReporter(inspect.currentframe(), True)
        f.report()

class TestRes(unittest.TestCase):

    def test_google(self):
        import requests
        r = requests.get('http://www.google.com')
        res(r)



if __name__ == '__main__':
    unittest.main()
