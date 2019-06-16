
from idebug import *
from idebug.tests.performance import *

import unittest



#@unittest.skip("showing class skipping")
class LoopReporterTestCase(unittest.TestCase):

    #@unittest.skip("demonstrating skipping")
    def test__init(self):
        loop = LoopReporter('title', 2)


    @unittest.skip("demonstrating skipping")
    def test__valid_LoopReporter(self):
        loop = LoopReporter(title='test_LoopReporter', len=10)
        for i in list(range(100)):
            loop.report()

    @unittest.skip("demonstrating skipping")
    def test__invalid_LoopReporter(self):
        loop = LoopReporter(title='test_LoopReporter', len=100)
        loop.count = 101
        self.assertEqual(loop.report(), None)

@unittest.skip("showing class skipping")
class PrintConvertedTimeunitTestCase(unittest.TestCase):

    @unittest.skip("demonstrating skipping")
    def test__valid_timeunit(self):
        print('\n\n')
        self.assertEqual(print_converted_timeunit('test', 0.01), 'msec')
        self.assertEqual(print_converted_timeunit('test', 3), 'secs')
        self.assertEqual(print_converted_timeunit('test', 69), 'mins')
        self.assertEqual(print_converted_timeunit('test', 3500), 'mins')
        self.assertEqual(print_converted_timeunit('test', 60*60*9), 'hrs')
        self.assertEqual(print_converted_timeunit('test', 60*60*24+456), 'hrs')


    @unittest.skip("demonstrating skipping")
    def test__funcname(a='a', b='b'):
        #fn = dbg.funcinit(inspect.currentframe())
        #dbg.funcfin(fn)
        f = FuncReporter(inspect.currentframe(), True)
        f.report()

@unittest.skip("showing class skipping")
class TestRes(unittest.TestCase):

    @unittest.skip("demonstrating skipping")
    def test__google(self):
        import requests
        r = requests.get('http://www.google.com')
        res(r)




def main():
    unittest.main()
