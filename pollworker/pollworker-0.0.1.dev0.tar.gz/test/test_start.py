# coding=utf8
from unittest import TestCase
import time

__author__ = 'Alexander.Li'


class TestStart(TestCase):
    def test_start(self):
        import pollworker

        def worker(message):
            print(message)

        class Poller(object):
            def poll(self, queue_name):
                time.sleep(2)
                return str(time.time())

        pollworker.regist_worker(worker)
        pollworker.regist_poller(Poller())
        pollworker.start('ooxx', stopwaits=3)

        self.assertTrue(True)
