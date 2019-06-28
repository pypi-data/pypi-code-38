import unittest

from cpbox.tool import concurrent
from cpbox.tool import logger

class TimerTest:

    def __init__(self):
        self.count = 0
        self.total = 100

    def right(self):
        return self.count == self.total

    def run(self):

        def callback():
            self.count += 1

        timer = concurrent.TRepeatedTimer(callback, 0.001, max_count=self.total)
        timer.start()
        timer.join()

class TestTimer(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_timer(self):
        test = TimerTest()
        test.run()
        self.assertTrue(test.right())

if __name__ == '__main__':
    logger.make_logger_for_test()
    unittest.main()
