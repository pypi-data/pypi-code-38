import unittest

from cpbox.tool import concurrent
from cpbox.tool import logger
from cpbox.tool import system


class SimpleThreadPoolTest:

    def __init__(self):
        self.count = 0
        self.total = 100

    def right(self):
        return self.count == self.total

    def run(self):
        def callback():
            self.count += 1
            system.shell_run('sleep 0.01')

        tp = concurrent.SimpleThreadPool()
        for i in range(0, self.total):
            tp.add_task(callback)
        tp.start()
        tp.wait()

class TestThreadPool(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_simple_thread_pool(self):
        test = SimpleThreadPoolTest()
        test.run()
        self.assertTrue(test.right())

if __name__ == '__main__':
    logger.make_logger_for_test()
    unittest.main()
