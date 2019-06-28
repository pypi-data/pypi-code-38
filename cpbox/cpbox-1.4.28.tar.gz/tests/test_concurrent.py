import unittest
from cpbox.tool import concurrent
from cpbox.tool import logger
from threading import Thread
import time
import logging

log = logging.getLogger()


class DelayBatchOpTest(object):

    def __init__(self):
        self.added_num = 0
        self.processed_num = 0
        self.callback_items = []

    def run(self):
        num_max = 25
        put_item_interval = 0.001
        timeout = 0.01
        batch_size = 10

        def callback(items):
            self.callback_items.extend(items)
            self.processed_num += len(items)

        def wait():
            while len(self.callback_items) != num_max:
                time.sleep(put_item_interval * 3)

        def add_element():
            while self.added_num < num_max:
                time.sleep(put_item_interval)
                self.added_num = self.added_num + 1
                delay_op.add_delay_item(self.added_num)

        delay_op = concurrent.DelayBatchOp(callback, timeout, batch_size=batch_size)
        thread_add_element = Thread(target=add_element)
        thread_add_element.daemon = True
        thread_add_element.start()

        thread_wait = Thread(target=wait)
        thread_wait.daemon = True
        thread_wait.start()
        thread_wait.join()


class TRepeatedTimerTest:

    def __init__(self):
        self.processed_num = 0
        self.max_count = 25

    def run(self):
        interval = 0.001

        def callback():
            self.processed_num += 1

        timer = concurrent.TRepeatedTimer(callback, interval, max_count=self.max_count)
        timer.start()
        timer.join()


class TestConcurrent(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_deplay_batch_op(self):
        test = DelayBatchOpTest()
        test.run()
        self.assertEqual(test.processed_num, test.added_num)

    def test_thread_base_timer(self):
        test = TRepeatedTimerTest()
        test.run()
        self.assertEqual(test.processed_num, test.max_count)


if __name__ == '__main__':
    logger.make_logger_for_test()
    unittest.main()
