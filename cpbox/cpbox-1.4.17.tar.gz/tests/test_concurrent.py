import unittest
from cpbox.tool import concurrent
from threading import Thread
import time
import logging
log = logging.getLogger()

class TestConcurrent(unittest.TestCase):

    def setUp(self):
        self.num = 0
        self.callback_items = []

    def tearDown(self):
        pass

    def test_deplay_op(self):
        num_max = 25
        put_item_interval = 0.01
        timeout = 0.5
        threshold = 10

        self.callback_items = []
        def callback(items):
            if concurrent.debug_concurrent:
                log.debug('callback: %s', len(items))
            self.callback_items.extend(items)

        def wait():
            while len(self.callback_items) != num_max:
                time.sleep(put_item_interval * 3)

        def add_element():
            # nonlocal num
            while self.num < num_max:
                time.sleep(put_item_interval)
                self.num = self.num + 1
                delay_op.add_delay_item(self.num)

        delay_op = concurrent.DelayOp(callback, timeout, threshold=threshold)
        thread_add_element = Thread(target=add_element)
        thread_add_element.daemon = True
        thread_add_element.start()

        thread_wait = Thread(target=wait)
        thread_wait.daemon = False
        thread_wait.start()

if __name__ == '__main__':
    unittest.main()
